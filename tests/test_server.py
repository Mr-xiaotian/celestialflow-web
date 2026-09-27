# tests/test_server.py
import re
from pathlib import Path

from celestialflow_web.server.core_server import static_path


def _push_graph_meta(client, graph_id: str):
    """推送一份最小图元信息，用于建立 graph 会话；返回响应供调用方断言状态码。"""
    return client.post(
        "/api/push_graph_meta",
        json={
            "graph_id": graph_id,
            "nodes": ["s1"],
            "edges": {"s1": []},
            "source_nodes": ["s1"],
            "node_meta": {"s1": {"class_name": "TaskExecutor", "max_workers": 1}},
            "analysis": {"graphId": graph_id, "isDAG": True},
        },
    )


def _ensure_session(client, graph_id: str) -> dict:
    """通过 pull_server_state 建立会话并返回状态摘要。"""
    return client.get(f"/api/pull_server_state?graph_id={graph_id}").json()


def test_store_snapshot_methods_return_isolated_copies(web_server):
    """测试 server 快照接口：返回值不应与内部 store 共享可变引用"""
    graph_id = "iso@1000"
    web_server.create_session(graph_id)

    raw_status = {"s1": {"tasks_succeeded": 1, "total_remaining_time": 2.0}}
    raw_graph_meta = {
        "nodes": ["s1"],
        "edges": {"s1": []},
        "source_nodes": ["s1"],
        "node_meta": {"s1": {"class_name": "TaskExecutor", "max_workers": 1}},
        "analysis": {"isDAG": True},
    }
    raw_errors = [
        {
            "event_id": 1,
            "node": "s1",
            "status": "failed",
            "task_json": None,
        }
    ]

    web_server.update_status_store(graph_id, 123.0, raw_status)
    web_server.update_graph_meta_store(graph_id, raw_graph_meta)
    web_server.update_errors_store(graph_id, raw_errors)

    _, status_timestamp, status_snapshot = web_server.get_status_snapshot(graph_id)
    _, graph_meta_snapshot = web_server.get_graph_meta_snapshot(graph_id)
    _, errors_snapshot = web_server.get_errors_snapshot(graph_id)

    raw_status["s1"]["tasks_succeeded"] = 99
    raw_graph_meta["nodes"].append("s2")
    raw_graph_meta["node_meta"]["s1"]["max_workers"] = 99
    raw_graph_meta["analysis"]["isDAG"] = False
    raw_errors[0]["node"] = "mutated"
    status_snapshot["s1"]["tasks_succeeded"] = 88
    graph_meta_snapshot["nodes"].append("s2")
    graph_meta_snapshot["node_meta"]["s1"]["max_workers"] = 77
    graph_meta_snapshot["analysis"]["isDAG"] = False
    errors_snapshot[0]["node"] = "snapshot-mutated"

    _, status_timestamp_after, status_snapshot_after = web_server.get_status_snapshot(
        graph_id
    )
    _, graph_meta_snapshot_after = web_server.get_graph_meta_snapshot(graph_id)
    _, errors_snapshot_after = web_server.get_errors_snapshot(graph_id)

    assert status_timestamp == 123.0
    assert status_timestamp_after == 123.0
    assert status_snapshot_after["s1"]["tasks_succeeded"] == 1
    assert graph_meta_snapshot_after["nodes"] == ["s1"]
    assert graph_meta_snapshot_after["node_meta"]["s1"]["max_workers"] == 1
    assert graph_meta_snapshot_after["analysis"]["isDAG"] is True
    assert errors_snapshot_after[0]["node"] == "s1"


def test_get_error_type_counts_returns_grouped_stats(web_server):
    """测试 server 层可返回全部节点的错误类型聚合统计。"""
    graph_id = "grouped@1000"
    web_server.create_session(graph_id)
    web_server.update_errors_store(
        graph_id,
        [
            {
                "event_id": 1,
                "node": "s1",
                "status": "failed",
                "task_json": {"value": 1},
                "error_type": "ValueError",
                "error_message": "bad",
                "ts": 1.0,
            },
            {
                "event_id": 2,
                "node": "s2",
                "status": "failed",
                "task_json": {"value": 2},
                "error_type": "TypeError",
                "error_message": "boom",
                "ts": 2.0,
            },
            {
                "event_id": 3,
                "node": "s1",
                "status": "failed",
                "task_json": {"value": 3},
                "error_type": "ValueError",
                "error_message": "bad again",
                "ts": 3.0,
            },
        ],
    )

    rev, items = web_server.get_error_type_counts(graph_id)

    assert rev == web_server.get_session(graph_id).store_revs["errors"]
    assert items == [
        {"error_type": "ValueError", "count": 2},
        {"error_type": "TypeError", "count": 1},
    ]


def test_get_error_type_counts_supports_node_filter(web_server):
    """测试 server 层错误类型聚合支持按节点过滤。"""
    graph_id = "nodefilter@1000"
    web_server.create_session(graph_id)
    web_server.update_errors_store(
        graph_id,
        [
            {
                "event_id": 1,
                "node": "s1",
                "status": "failed",
                "task_json": {"value": 1},
                "error_type": "ValueError",
                "error_message": "bad",
                "ts": 1.0,
            },
            {
                "event_id": 2,
                "node": "s1",
                "status": "failed",
                "task_json": {"value": 2},
                "error_type": "TypeError",
                "error_message": "boom",
                "ts": 2.0,
            },
            {
                "event_id": 3,
                "node": "s2",
                "status": "failed",
                "task_json": {"value": 3},
                "error_type": "RuntimeError",
                "error_message": "oops",
                "ts": 3.0,
            },
        ],
    )

    rev, items = web_server.get_error_type_counts(graph_id, "s1")

    assert rev == web_server.get_session(graph_id).store_revs["errors"]
    assert items == [
        {"error_type": "TypeError", "count": 1},
        {"error_type": "ValueError", "count": 1},
    ]


def test_index_page(client):
    """测试 Web 仪表盘首页：验证 HTML 模板是否渲染正确且包含关键 DOM 容器"""
    response = client.get("/")
    assert response.status_code == 200
    assert "html" in response.headers["content-type"]
    # 验证模板是否包含关键元素
    assert 'id="dashboard"' in response.text

def _module_evaluation_order(entry: str) -> list[str]:
    """按 ESM 规范近似推导从入口出发的模块求值顺序（环内已在求值的节点跳过）。"""
    js_dir = Path(static_path) / "js"
    order: list[str] = []
    seen: set[str] = set()

    def visit(name: str) -> None:
        if name in seen:
            return
        seen.add(name)
        text = (js_dir / name).read_text(encoding="utf-8")
        pattern = r'^import\s+(?:.*?from\s+)?"\./([\w.-]+\.js)";'
        for dep in re.findall(pattern, text, re.MULTILINE):
            visit(dep)
        order.append(name)

    visit(entry)
    return order


def test_entry_module_reaches_every_built_artifact(client):
    """入口模块必须能到达全部编译产物。

    前端用原生 ESM，templates 里只写一个入口，其余靠 import 串联；tsc 能校验
    import 路径存在，但发现不了“产物没有任何人 import”这种死模块。
    """
    html = client.get("/").text
    referenced = set(re.findall(r"js/([\w.-]+\.js)", html))
    built = {path.name for path in (Path(static_path) / "js").glob("*.js")}
    assert referenced <= built  # 首页引用的入口必须真实存在
    assert set(_module_evaluation_order("main.js")) == built


def test_card_injecting_module_evaluates_before_dashboards(client):
    """web_config 必须先于各 dashboard 模块求值。

    web_config 在模块加载时用 ensureAllCards() 注入全部卡片 DOM，而 dashboard_*
    模块在顶层就 getElementById 这些卡片内的元素。旧方案靠 scripts.html 的手写
    顺序保证，换成 ESM 后只能由入口的 import 顺序保证。
    """
    order = _module_evaluation_order("main.js")
    config_at = order.index("web_config.js")
    dashboards = [name for name in order if name.startswith("dashboard_")]

    assert dashboards
    assert all(order.index(name) > config_at for name in dashboards), order


def test_config_api(client):
    """测试配置拉取 API：验证前端能够获取到刷新间隔、主题等运行时配置"""
    response = client.get("/api/pull_config")
    assert response.status_code == 200
    data = response.json()
    assert "global" in data
    assert "dashboard" in data
    assert "errors" in data
    assert "injection" in data
    assert "autoRefreshEnabled" in data["global"]
    assert "refreshInterval" in data["global"]
    assert "theme" in data["global"]
    assert "structureEdgeLabel" in data["dashboard"]
    assert "sortOrder" in data["errors"]
    assert "jumpToInjectionAfterRetry" in data["errors"]
    assert "columns" in data["errors"]
    assert "showInjectableOnly" in data["injection"]

def test_server_state_api(client):
    """测试 reporter 拉取的服务端同步状态。"""
    response = client.get("/api/pull_server_state?graph_id=demo@1000")

    assert response.status_code == 200
    data = response.json()
    assert data["graph_id"] == "demo@1000"
    assert data["interval"] > 0
    assert data["has_graph_meta"] is False
    assert data["has_status"] is False
    assert data["alive"] is True
    assert data["max_event_id_in_fail"] is None


def test_pull_server_state_rejects_empty_graph_id(client):
    """空 graph_id 不应被当作合法会话。"""
    response = client.get("/api/pull_server_state?graph_id=")

    assert response.status_code == 404
    assert response.json()["error"] == "unknown graph_id"


def test_server_state_seen_flags_track_writes_and_reset(client):
    """has_status / has_graph_meta 反映服务端是否收到过写入，会话重建后归零。"""
    graph_id = "seen@1000"

    state = _ensure_session(client, graph_id)
    assert state["has_status"] is False
    assert state["has_graph_meta"] is False

    push_status = client.post(
        "/api/push_status",
        json={
            "graph_id": graph_id,
            "timestamp": 1.0,
            "status": {"s1": {"status": 0}},
        },
    )
    assert push_status.status_code == 200
    assert _push_graph_meta(client, graph_id).status_code == 200

    state = _ensure_session(client, graph_id)
    assert state["has_status"] is True
    assert state["has_graph_meta"] is True

    # 会话被移除后由 pull_server_state 重建，两个标志应回到 False 以触发全量重推。
    removed = client.post("/api/remove_session", json={"graph_id": graph_id})
    assert removed.json() == {"ok": True}
    state = _ensure_session(client, graph_id)
    assert state["has_status"] is False
    assert state["has_graph_meta"] is False


def test_empty_graph_meta_still_marks_seen(client):
    """图元信息的 nodes 为空时也应标记为已收到，避免每轮重推。"""
    graph_id = "empty@1000"
    _ensure_session(client, graph_id)

    response = client.post(
        "/api/push_graph_meta",
        json={
            "graph_id": graph_id,
            "nodes": [],
            "edges": {},
            "source_nodes": [],
            "node_meta": {},
            "analysis": None,
        },
    )
    assert response.status_code == 200

    state = _ensure_session(client, graph_id)
    assert state["has_graph_meta"] is True


def test_push_errors_meta_route_removed(client):
    """`/api/push_errors_meta` 已删除，不应再接受请求。"""
    response = client.post(
        "/api/push_errors_meta",
        json={
            "graph_id": "demo@1000",
            "append": False,
        },
    )

    assert response.status_code == 404

def test_status_push_pull(client):
    """测试状态同步链路：验证已知版本号（known_rev）下的增量拉取逻辑"""
    graph_id = "demo@1000"
    state = _ensure_session(client, graph_id)
    assert state["has_graph_meta"] is False

    # 1. 推送状态
    test_timestamp = 1710000000.0
    test_status = {
        "s1": {
            "tasks_succeeded": 10,
            "tasks_failed": 0,
            "remaining_time": 3.5,
            "total_remaining_time": 8.0,
        }
    }
    push_resp = client.post(
        "/api/push_status",
        json={
            "graph_id": graph_id,
            "timestamp": test_timestamp,
            "status": test_status,
        },
    )
    assert push_resp.status_code == 200
    assert push_resp.json() == {"ok": True}

    # 2. 拉取状态 (known_rev=-1)
    pull_resp = client.get(f"/api/pull_status?graph_id={graph_id}&known_rev=-1")
    assert pull_resp.status_code == 200
    pull_data = pull_resp.json()
    assert pull_data["rev"] > 0
    assert pull_data["timestamp"] == test_timestamp
    assert pull_data["data"] == test_status
    assert pull_data["data"]["s1"]["total_remaining_time"] == 8.0

    # 3. 再次拉取相同版本 (known_rev=current_rev)
    current_rev = pull_data["rev"]
    pull_resp_cached = client.get(
        f"/api/pull_status?graph_id={graph_id}&known_rev={current_rev}"
    )
    assert pull_resp_cached.json()["data"] is None


def test_graph_meta_push_pull(client):
    """测试图元信息同步链路：结构、节点元信息与分析结果应经 push/pull 完整保留"""
    graph_id = "demo@1000"
    _ensure_session(client, graph_id)

    test_graph_meta = {
        "graph_id": graph_id,
        "nodes": ["s1", "s2"],
        "edges": {"s1": ["s2"], "s2": []},
        "source_nodes": ["s1"],
        "node_meta": {
            "s1": {
                "class_name": "TaskExecutor",
                "execution_mode": "thread",
                "max_workers": 4,
            },
            "s2": {
                "class_name": "TaskExecutor",
                "execution_mode": "serial",
                "max_workers": 1,
            },
        },
        "analysis": {"graphId": graph_id, "isDAG": True, "layersDict": {"0": ["s1"]}},
    }
    push_resp = client.post("/api/push_graph_meta", json=test_graph_meta)
    assert push_resp.status_code == 200
    assert push_resp.json() == {"ok": True}

    pull_data = client.get(
        f"/api/pull_graph_meta?graph_id={graph_id}&known_rev=-1"
    ).json()
    assert pull_data["rev"] > 0
    assert pull_data["data"] == {
        "nodes": test_graph_meta["nodes"],
        "edges": test_graph_meta["edges"],
        "source_nodes": test_graph_meta["source_nodes"],
        "node_meta": test_graph_meta["node_meta"],
        "analysis": test_graph_meta["analysis"],
    }

    # 版本未变时不应重复下发
    pull_cached = client.get(
        f"/api/pull_graph_meta?graph_id={graph_id}&known_rev={pull_data['rev']}"
    )
    assert pull_cached.json()["data"] is None

def test_task_injection(client):
    """测试任务与终止符注入流程：验证服务端原子返回并在 pull 后清空。"""
    graph_id = "inject@1000"
    _ensure_session(client, graph_id)

    # 1. 注入任务
    injection_data = {
        "StageA": [1, 2, 3],
    }
    push_resp = client.post(
        "/api/push_injection_tasks",
        json={"graph_id": graph_id, "tasks": injection_data},
    )
    assert push_resp.status_code == 200
    assert push_resp.json() == {"ok": True}
    termination_resp = client.post(
        "/api/push_injection_terminations",
        json={"graph_id": graph_id, "nodes": ["StageB"]},
    )
    assert termination_resp.status_code == 200
    assert termination_resp.json() == {"ok": True}

    # 2. 拉取注入任务
    pull_resp = client.get(f"/api/pull_injection?graph_id={graph_id}")
    assert pull_resp.status_code == 200
    tasks = pull_resp.json()
    assert tasks == {
        "tasks": injection_data,
        "terminations": ["StageB"],
    }

    # 3. 再次拉取应为空（已清空）
    pull_again = client.get(f"/api/pull_injection?graph_id={graph_id}")
    assert pull_again.json() == {"tasks": {}, "terminations": []}


def test_task_injection_isolated_between_sessions(client):
    """不同会话的注入队列相互隔离，不会串台。"""
    graph_a = "iso_a@1000"
    graph_b = "iso_b@1000"
    _ensure_session(client, graph_a)
    _ensure_session(client, graph_b)

    client.post(
        "/api/push_injection_tasks",
        json={"graph_id": graph_a, "tasks": {"StageA": [1]}},
    )
    client.post(
        "/api/push_injection_tasks",
        json={"graph_id": graph_b, "tasks": {"StageB": [2]}},
    )

    pulled_a = client.get(f"/api/pull_injection?graph_id={graph_a}").json()
    pulled_b = client.get(f"/api/pull_injection?graph_id={graph_b}").json()

    assert pulled_a == {"tasks": {"StageA": [1]}, "terminations": []}
    assert pulled_b == {"tasks": {"StageB": [2]}, "terminations": []}


def test_task_injection_overwrites_tasklist_per_node(client):
    """新的 push 会逐个节点更新 task list，终止符单独存储。"""
    graph_id = "overwrite@1000"
    _ensure_session(client, graph_id)

    client.post(
        "/api/push_injection_tasks",
        json={"graph_id": graph_id, "tasks": {"StageA": [1, 2, 3]}},
    )
    client.post(
        "/api/push_injection_terminations",
        json={"graph_id": graph_id, "nodes": ["StageB"]},
    )

    client.post(
        "/api/push_injection_tasks",
        json={"graph_id": graph_id, "tasks": {"StageA": [9], "StageC": ["new"]}},
    )

    pull_resp = client.get(f"/api/pull_injection?graph_id={graph_id}")

    assert pull_resp.status_code == 200
    assert pull_resp.json() == {
        "tasks": {
            "StageA": [9],
            "StageC": ["new"],
        },
        "terminations": ["StageB"],
    }


def test_task_injection_requires_tasklist_mapping(client):
    """任务注入接口要求每个节点值都是任务列表数组。"""
    graph_id = "badlist@1000"
    _ensure_session(client, graph_id)
    invalid_payload = {
        "graph_id": graph_id,
        "tasks": {"StageA": {"user_id": 1}},
    }

    response = client.post("/api/push_injection_tasks", json=invalid_payload)

    assert response.status_code == 422


def test_termination_injection_requires_string_array(client):
    """终止符注入接口要求节点列表为字符串数组。"""
    graph_id = "badterm@1000"
    _ensure_session(client, graph_id)
    response = client.post(
        "/api/push_injection_terminations",
        json={"graph_id": graph_id, "nodes": {"StageA": True}},
    )

    assert response.status_code == 422


def test_injection_unknown_session_returns_409(client):
    """向未建立会话投递注入时应返回 409，而不是静默丢失。"""
    response = client.post(
        "/api/push_injection_tasks",
        json={"graph_id": "ghost@1000", "tasks": {"StageA": [1]}},
    )

    assert response.status_code == 409
    assert response.json()["error"] == "unknown graph_id"


def test_errors_pagination(client):
    """测试错误日志分页与过滤 API：验证后端对错误记录的聚合与分页逻辑是否正确"""
    graph_id = "demo@1000"
    state = _ensure_session(client, graph_id)
    assert state["has_graph_meta"] is False

    # 1. 模拟推送错误数据
    test_errors = [
        {
            "event_id": i,
            "node": f"s{i%2}",
            "status": "failed",
            "task_json": {"value": i, "label": f"task{i}"},
            "error_type": "ValueError" if i % 2 == 0 else "TypeError",
            "error_message": f"err{i}",
            "ts": i,
        }
        for i in range(15)
    ]
    # 错误同步已统一走 push_errors。
    client.post(
        "/api/push_errors",
        json={
            "graph_id": graph_id,
            "errors": test_errors,
        },
    )

    # 2. 测试分页（第一页，每页10条）
    resp_p1 = client.get(
        f"/api/pull_errors?graph_id={graph_id}&page=1&page_size=10"
    )
    data_p1 = resp_p1.json()
    assert data_p1["total"] == 15
    assert data_p1["total_pages"] == 2
    assert len(data_p1["data"]) == 10
    assert data_p1["sort_order"] == "newest"
    assert data_p1["data"][0]["event_id"] == 14
    assert data_p1["data"][0]["task_json"] == {"value": 14, "label": "task14"}

    # 3. 测试过滤 (node=s0)
    resp_filter = client.get(f"/api/pull_errors?graph_id={graph_id}&node=s0")
    data_filter = resp_filter.json()
    # 0, 2, 4, 6, 8, 10, 12, 14 -> 8条
    assert data_filter["total"] == 8

    # 4. 测试关键词过滤（任务名与错误字段都可命中）
    resp_keyword = client.get(f"/api/pull_errors?graph_id={graph_id}&keyword=task12")
    data_keyword = resp_keyword.json()
    assert data_keyword["total"] == 1
    assert data_keyword["data"][0]["event_id"] == 12

    resp_error_keyword = client.get(
        f"/api/pull_errors?graph_id={graph_id}&keyword=typeerror"
    )
    data_error_keyword = resp_error_keyword.json()
    assert data_error_keyword["total"] == 7

    # 5. 测试排序（最旧优先）
    resp_oldest = client.get(
        f"/api/pull_errors?graph_id={graph_id}&sort_order=oldest&page_size=5"
    )
    data_oldest = resp_oldest.json()
    assert data_oldest["sort_order"] == "oldest"
    assert len(data_oldest["data"]) == 5
    assert data_oldest["data"][0]["event_id"] == 0


def test_pull_error_type_counts(client):
    """测试错误类型聚合 API：支持全部节点、单节点和缓存命中。"""
    graph_id = "demo@1001"
    state = _ensure_session(client, graph_id)
    assert state["has_graph_meta"] is False

    test_errors = [
        {
            "event_id": 1,
            "node": "s1",
            "status": "failed",
            "task_json": {"value": 1},
            "error_type": "ValueError",
            "error_message": "err1",
            "ts": 1,
        },
        {
            "event_id": 2,
            "node": "s1",
            "status": "failed",
            "task_json": {"value": 2},
            "error_type": "TypeError",
            "error_message": "err2",
            "ts": 2,
        },
        {
            "event_id": 3,
            "node": "s2",
            "status": "failed",
            "task_json": {"value": 3},
            "error_type": "ValueError",
            "error_message": "err3",
            "ts": 3,
        },
    ]
    client.post(
        "/api/push_errors",
        json={
            "graph_id": graph_id,
            "errors": test_errors,
        },
    )

    resp_all = client.get(f"/api/pull_error_type_counts?graph_id={graph_id}")
    assert resp_all.status_code == 200
    all_data = resp_all.json()
    assert all_data["data"] == [
        {"error_type": "ValueError", "count": 2},
        {"error_type": "TypeError", "count": 1},
    ]

    resp_node = client.get(f"/api/pull_error_type_counts?graph_id={graph_id}&node=s1")
    assert resp_node.status_code == 200
    node_data = resp_node.json()
    assert node_data["data"] == [
        {"error_type": "TypeError", "count": 1},
        {"error_type": "ValueError", "count": 1},
    ]

    rev = node_data["rev"]
    resp_cached = client.get(
        f"/api/pull_error_type_counts?graph_id={graph_id}&node=s1&known_rev={rev}"
    )
    assert resp_cached.status_code == 200
    assert resp_cached.json()["data"] is None


def test_push_errors_appends_for_same_graph(client):
    """相同 graph_id 下，push_errors 只追加新错误。"""
    graph_id = "demo@2000"

    first_batch = [
        {
            "event_id": 1,
            "node": "s1",
            "status": "failed",
            "task_json": {"value": 1},
            "error_type": "ValueError",
            "error_message": "err1",
            "ts": 1.0,
        },
        {
            "event_id": 2,
            "node": "s2",
            "status": "failed",
            "task_json": {"value": 2},
            "error_type": "TypeError",
            "error_message": "err2",
            "ts": 2.0,
        },
    ]
    second_batch = [
        {
            "event_id": 3,
            "node": "s1",
            "status": "failed",
            "task_json": {"value": 3},
            "error_type": "RuntimeError",
            "error_message": "err3",
            "ts": 3.0,
        }
    ]

    state = _ensure_session(client, graph_id)
    assert state["has_graph_meta"] is False

    analysis_resp = _push_graph_meta(client, graph_id)
    assert analysis_resp.status_code == 200
    assert analysis_resp.json() == {"ok": True}

    response = client.post(
        "/api/push_errors",
        json={
            "graph_id": graph_id,
            "errors": first_batch,
        },
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    state = _ensure_session(client, graph_id)
    assert state["max_event_id_in_fail"] == 2
    assert state["has_graph_meta"] is True

    response = client.post(
        "/api/push_errors",
        json={
            "graph_id": graph_id,
            "errors": second_batch,
        },
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    pulled = client.get(f"/api/pull_errors?graph_id={graph_id}&page=1&page_size=10").json()
    assert pulled["total"] == 3
    assert [item["event_id"] for item in pulled["data"]] == [3, 2, 1]


def test_push_errors_duplicate_append_is_idempotent(client):
    """重复追加相同 event_id 时，错误缓存不应出现重复行。"""
    graph_id = "demo@3000"
    duplicated_batch = [
        {
            "event_id": 1,
            "node": "s1",
            "status": "failed",
            "task_json": {"value": 1},
            "error_type": "ValueError",
            "error_message": "err1",
            "ts": 1.0,
        }
    ]

    client.get(f"/api/pull_server_state?graph_id={graph_id}")
    assert _push_graph_meta(client, graph_id).status_code == 200

    first = client.post(
        "/api/push_errors",
        json={
            "graph_id": graph_id,
            "errors": duplicated_batch,
        },
    )
    second = client.post(
        "/api/push_errors",
        json={
            "graph_id": graph_id,
            "errors": duplicated_batch,
        },
    )

    assert first.status_code == 200
    assert second.status_code == 200

    pulled = client.get(f"/api/pull_errors?graph_id={graph_id}&page=1&page_size=10").json()
    assert pulled["total"] == 1
    assert [item["event_id"] for item in pulled["data"]] == [1]


def test_sessions_are_isolated_and_coexist(client):
    """多个会话可同时存在，各自的错误与图元信息互不干扰。"""
    graph_a = "coexist_a@1000"
    graph_b = "coexist_b@1000"

    _ensure_session(client, graph_a)
    _ensure_session(client, graph_b)
    assert _push_graph_meta(client, graph_a).status_code == 200
    assert _push_graph_meta(client, graph_b).status_code == 200

    client.post(
        "/api/push_errors",
        json={
            "graph_id": graph_a,
            "errors": [
                {
                    "event_id": 1,
                    "node": "s1",
                    "status": "failed",
                    "task_json": {"value": 1},
                    "error_type": "ValueError",
                    "error_message": "from-a",
                    "ts": 1.0,
                }
            ],
        },
    )

    pulled_a = client.get(f"/api/pull_errors?graph_id={graph_a}&page=1&page_size=10").json()
    pulled_b = client.get(f"/api/pull_errors?graph_id={graph_b}&page=1&page_size=10").json()

    assert pulled_a["total"] == 1
    assert pulled_b["total"] == 0

    # 两个会话都仍然存活，不会因为后来者而互相覆盖。
    state_a = _ensure_session(client, graph_a)
    state_b = _ensure_session(client, graph_b)
    assert state_a["has_graph_meta"] is True
    assert state_b["has_graph_meta"] is True


def test_pull_sessions_lists_all_sessions(client):
    """会话列表接口返回全部会话摘要，并带 created_at 信息。"""
    _ensure_session(client, "list_a@1000")
    _ensure_session(client, "list_b@1000")

    sessions = client.get("/api/pull_sessions").json()
    ids = {item["graph_id"] for item in sessions}

    assert {"list_a@1000", "list_b@1000"} <= ids
    for item in sessions:
        if item["graph_id"] in {"list_a@1000", "list_b@1000"}:
            assert item["name"] in {"list_a", "list_b"}
            assert item["alive"] is True
            assert item["created_at"] > 0


def test_shutdown_session_marks_not_alive(client):
    """shutdown_session 将会话标记为已结束，但保留其数据。"""
    graph_id = "shutdown@1000"
    _ensure_session(client, graph_id)
    assert _push_graph_meta(client, graph_id).status_code == 200

    resp = client.post("/api/shutdown_session", json={"graph_id": graph_id})
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}

    state = _ensure_session(client, graph_id)
    assert state["alive"] is False
    # 数据仍然保留，可继续拉取。
    assert state["has_graph_meta"] is True

    sessions = {item["graph_id"]: item for item in client.get("/api/pull_sessions").json()}
    assert sessions[graph_id]["alive"] is False
    assert sessions[graph_id]["shutdown_reason"] == "reporter_stopped"


def test_shutdown_unknown_session_returns_409(client):
    """对不存在的会话发送 shutdown 应返回 409。"""
    resp = client.post("/api/shutdown_session", json={"graph_id": "ghost@1000"})
    assert resp.status_code == 409


def test_remove_session_drops_data_and_unknown_afterwards(client):
    """remove_session 彻底移除会话，之后的拉取与 push 都视为未知会话。"""
    graph_id = "removed@1000"
    _ensure_session(client, graph_id)
    assert _push_graph_meta(client, graph_id).status_code == 200

    remove_resp = client.post("/api/remove_session", json={"graph_id": graph_id})
    assert remove_resp.status_code == 200
    assert remove_resp.json() == {"ok": True}

    # 会话已不存在：拉取返回 404，push 返回 409。
    assert client.get(f"/api/pull_status?graph_id={graph_id}").status_code == 404
    assert _push_graph_meta(client, graph_id).status_code == 409

    # 重复移除返回 404。
    assert client.post("/api/remove_session", json={"graph_id": graph_id}).status_code == 404


def test_unknown_session_pulls_return_404(client):
    """未建立会话时，各前端拉取接口应返回 404 而非 500。"""
    assert client.get("/api/pull_status?graph_id=ghost@1000").status_code == 404
    assert client.get("/api/pull_graph_meta?graph_id=ghost@1000").status_code == 404
    assert client.get("/api/pull_errors?graph_id=ghost@1000").status_code == 404
    assert (
        client.get("/api/pull_error_type_counts?graph_id=ghost@1000").status_code == 404
    )
    assert client.get("/api/pull_injection?graph_id=ghost@1000").status_code == 404
