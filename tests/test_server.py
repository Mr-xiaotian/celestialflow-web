# tests/test_server.py
import re
from pathlib import Path

from celestialflow_web.server.core_server import static_path


def _push_graph_meta(client, session_id: str, name: str | None = None):
    """推送一份最小图元信息，用于建立 graph 会话；返回响应供调用方断言状态码。"""
    return client.post(
        "/api/push_graph_meta",
        json={
            "session_id": session_id,
            "graph": name or session_id,
            "graph_mode": "serial",
            "start_time": 0.0,
            "class_name": "TaskGraph",
            "is_dag": True,
            "nodes": ["s1"],
            "edges": {"s1": []},
            "source_nodes": ["s1"],
            "node_meta": {"s1": {"class_name": "TaskExecutor", "max_workers": 1}},
        },
    )


def _session_summary(client, session_id: str) -> dict:
    """从会话列表中取出指定会话的摘要。"""
    by_id = {item["session_id"]: item for item in client.get("/api/pull_sessions").json()}
    return by_id[session_id]


def _push_errors(client, session_id: str, errors: list[dict]):
    """逐条推送错误记录，返回最后一次响应。"""
    response = None
    for record in errors:
        response = client.post(
            "/api/push_error", json={"session_id": session_id, **record}
        )
    return response


def test_reporter_graph_meta_auto_creates_session(client):
    """图元信息写入是会话注册入口：会话不存在时自动创建，而不是 409。"""
    session_id = "autocreate@1"
    response = _push_graph_meta(client, session_id)

    assert response.status_code == 200
    ids = {item["session_id"] for item in client.get("/api/pull_sessions").json()}
    assert session_id in ids


def test_reporter_write_refreshes_last_seen(web_server):
    """会话建立后，每次上报写入都应刷新 last_seen（存活证明）。"""
    session_id = "heartbeat@1"
    web_server.update_graph_meta_store(
        session_id,
        {
            "graph": session_id,
            "graph_mode": "serial",
            "start_time": 0.0,
            "class_name": "TaskGraph",
            "is_dag": True,
            "nodes": ["s1"],
            "edges": {"s1": []},
            "source_nodes": ["s1"],
            "node_meta": {},
        },
    )
    session = web_server.get_session(session_id)
    assert session is not None

    session.last_seen = 0.0
    web_server.update_status_store(session_id, 2.0, {"s1": {"status": 1}})

    assert session.last_seen > 0.0


def test_status_push_dedups_unchanged_snapshot(client):
    """相同快照重复推送不推进版本号，前端可继续拿到 data=null。"""
    session_id = "dedup@1"
    _push_graph_meta(client, session_id)

    payload = {
        "session_id": session_id,
        "timestamp": 1.0,
        "snapshot": {"s1": {"status": 0}},
    }
    assert client.post("/api/push_snapshot", json=payload).status_code == 200
    first = client.get(
        f"/api/pull_status?session_id={session_id}&known_rev=-1"
    ).json()
    assert first["data"] == {"s1": {"status": 0}}
    rev = first["rev"]

    # 相同快照再推：版本号不变，已知版本拉取得到 data=null。
    assert client.post(
        "/api/push_snapshot", json={**payload, "timestamp": 2.0}
    ).status_code == 200
    cached = client.get(
        f"/api/pull_status?session_id={session_id}&known_rev={rev}"
    ).json()
    assert cached["rev"] == rev
    assert cached["data"] is None

    # 快照变化：版本号推进，前端拿到新数据。
    assert client.post(
        "/api/push_snapshot",
        json={**payload, "snapshot": {"s1": {"status": 1}}},
    ).status_code == 200
    fresh = client.get(
        f"/api/pull_status?session_id={session_id}&known_rev={rev}"
    ).json()
    assert fresh["rev"] != rev
    assert fresh["data"] == {"s1": {"status": 1}}


def test_store_snapshot_methods_return_isolated_copies(web_server):
    """测试 server 快照接口：返回值不应与内部 store 共享可变引用"""
    session_id = "iso@1000"
    web_server.create_session(session_id)

    raw_status = {"s1": {"tasks_succeeded": 1, "total_remaining_time": 2.0}}
    raw_graph_meta = {
        "graph": session_id,
        "graph_mode": "serial",
        "start_time": 0.0,
        "class_name": "TaskGraph",
        "is_dag": True,
        "nodes": ["s1"],
        "edges": {"s1": []},
        "source_nodes": ["s1"],
        "node_meta": {"s1": {"class_name": "TaskExecutor", "max_workers": 1}},
    }
    raw_errors = [
        {
            "event_id": 1,
            "node": "s1",
            "status": "failed",
            "task_json": None,
        }
    ]

    web_server.update_status_store(session_id, 123.0, raw_status)
    web_server.update_graph_meta_store(session_id, raw_graph_meta)
    web_server.update_errors_store(session_id, raw_errors)

    _, status_timestamp, status_snapshot = web_server.get_status_snapshot(session_id)
    _, graph_meta_snapshot = web_server.get_graph_meta_snapshot(session_id)
    _, errors_snapshot = web_server.get_errors_snapshot(session_id)

    raw_status["s1"]["tasks_succeeded"] = 99
    raw_graph_meta["nodes"].append("s2")
    raw_graph_meta["node_meta"]["s1"]["max_workers"] = 99
    raw_graph_meta["is_dag"] = False
    raw_errors[0]["node"] = "mutated"
    status_snapshot["s1"]["tasks_succeeded"] = 88
    graph_meta_snapshot["nodes"].append("s2")
    graph_meta_snapshot["node_meta"]["s1"]["max_workers"] = 77
    graph_meta_snapshot["is_dag"] = False
    errors_snapshot[0]["node"] = "snapshot-mutated"

    _, status_timestamp_after, status_snapshot_after = web_server.get_status_snapshot(
        session_id
    )
    _, graph_meta_snapshot_after = web_server.get_graph_meta_snapshot(session_id)
    _, errors_snapshot_after = web_server.get_errors_snapshot(session_id)

    assert status_timestamp == 123.0
    assert status_timestamp_after == 123.0
    assert status_snapshot_after["s1"]["tasks_succeeded"] == 1
    assert graph_meta_snapshot_after["nodes"] == ["s1"]
    assert graph_meta_snapshot_after["node_meta"]["s1"]["max_workers"] == 1
    assert graph_meta_snapshot_after["is_dag"] is True
    assert errors_snapshot_after[0]["node"] == "s1"


def test_get_error_type_counts_returns_grouped_stats(web_server):
    """测试 server 层可返回全部节点的错误类型聚合统计。"""
    session_id = "grouped@1000"
    web_server.create_session(session_id)
    web_server.update_errors_store(
        session_id,
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

    rev, items = web_server.get_error_type_counts(session_id)

    assert rev == web_server.get_session(session_id).store_revs["errors"]
    assert items == [
        {"error_type": "ValueError", "count": 2},
        {"error_type": "TypeError", "count": 1},
    ]


def test_get_error_type_counts_supports_node_filter(web_server):
    """测试 server 层错误类型聚合支持按节点过滤。"""
    session_id = "nodefilter@1000"
    web_server.create_session(session_id)
    web_server.update_errors_store(
        session_id,
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

    rev, items = web_server.get_error_type_counts(session_id, "s1")

    assert rev == web_server.get_session(session_id).store_revs["errors"]
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

def test_server_state_seen_flags_track_writes_and_reset(client, web_server):
    """has_status / has_graph_meta 反映服务端是否收到过写入，会话移除后不再列出。"""
    session_id = "seen@1000"
    web_server.create_session(session_id)

    summary = _session_summary(client, session_id)
    assert summary["has_status"] is False
    assert summary["has_graph_meta"] is False

    push_resp = client.post(
        "/api/push_snapshot",
        json={
            "session_id": session_id,
            "timestamp": 1.0,
            "snapshot": {"s1": {"status": 0}},
        },
    )
    assert push_resp.status_code == 200
    assert _push_graph_meta(client, session_id).status_code == 200

    summary = _session_summary(client, session_id)
    assert summary["has_status"] is True
    assert summary["has_graph_meta"] is True

    # 会话被移除后不再出现在会话列表中。
    removed = client.post("/api/remove_session", json={"session_id": session_id})
    assert removed.json() == {"ok": True}
    ids = {item["session_id"] for item in client.get("/api/pull_sessions").json()}
    assert session_id not in ids


def test_empty_graph_meta_still_marks_seen(client):
    """图元信息的 nodes 为空时也应标记为已收到，避免每轮重推。"""
    session_id = "empty@1000"

    response = client.post(
        "/api/push_graph_meta",
        json={
            "session_id": session_id,
            "graph": session_id,
            "graph_mode": "serial",
            "start_time": 0.0,
            "class_name": "TaskGraph",
            "is_dag": True,
            "nodes": [],
            "edges": {},
            "source_nodes": [],
            "node_meta": {},
        },
    )
    assert response.status_code == 200

    assert _session_summary(client, session_id)["has_graph_meta"] is True


def test_push_errors_meta_route_removed(client):
    """`/api/push_errors_meta` 已删除，不应再接受请求。"""
    response = client.post(
        "/api/push_errors_meta",
        json={
            "session_id": "demo@1000",
            "append": False,
        },
    )

    assert response.status_code == 404

def test_status_push_pull(client):
    """测试状态同步链路：验证已知版本号（known_rev）下的增量拉取逻辑"""
    session_id = "demo@1000"
    assert _push_graph_meta(client, session_id).status_code == 200

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
        "/api/push_snapshot",
        json={
            "session_id": session_id,
            "timestamp": test_timestamp,
            "snapshot": test_status,
        },
    )
    assert push_resp.status_code == 200
    assert push_resp.json() == {"ok": True}

    # 2. 拉取状态 (known_rev=-1)
    pull_resp = client.get(f"/api/pull_status?session_id={session_id}&known_rev=-1")
    assert pull_resp.status_code == 200
    pull_data = pull_resp.json()
    assert pull_data["rev"] > 0
    assert pull_data["timestamp"] == test_timestamp
    assert pull_data["data"] == test_status
    assert pull_data["data"]["s1"]["total_remaining_time"] == 8.0

    # 3. 再次拉取相同版本 (known_rev=current_rev)
    current_rev = pull_data["rev"]
    pull_resp_cached = client.get(
        f"/api/pull_status?session_id={session_id}&known_rev={current_rev}"
    )
    assert pull_resp_cached.json()["data"] is None


def test_graph_meta_push_pull(client):
    """测试图元信息同步链路：结构、节点元信息与图级字段应经 push/pull 完整保留"""
    session_id = "demo@1000"

    test_graph_meta = {
        "session_id": session_id,
        "graph": session_id,
        "graph_mode": "serial",
        "start_time": 0.0,
        "class_name": "TaskGraph",
        "is_dag": True,
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
    }
    push_resp = client.post("/api/push_graph_meta", json=test_graph_meta)
    assert push_resp.status_code == 200
    assert push_resp.json() == {"ok": True}

    pull_data = client.get(
        f"/api/pull_graph_meta?session_id={session_id}&known_rev=-1"
    ).json()
    assert pull_data["rev"] > 0
    assert pull_data["data"] == {
        "graph": test_graph_meta["graph"],
        "graph_mode": test_graph_meta["graph_mode"],
        "start_time": test_graph_meta["start_time"],
        "class_name": test_graph_meta["class_name"],
        "is_dag": test_graph_meta["is_dag"],
        "nodes": test_graph_meta["nodes"],
        "edges": test_graph_meta["edges"],
        "source_nodes": test_graph_meta["source_nodes"],
        "node_meta": test_graph_meta["node_meta"],
    }

    # 版本未变时不应重复下发
    pull_cached = client.get(
        f"/api/pull_graph_meta?session_id={session_id}&known_rev={pull_data['rev']}"
    )
    assert pull_cached.json()["data"] is None

def test_task_injection(client):
    """测试任务与终止符注入流程：验证服务端原子返回并在 pull 后清空。"""
    session_id = "inject@1000"
    _push_graph_meta(client, session_id)

    # 1. 注入任务
    injection_data = {
        "StageA": [1, 2, 3],
    }
    push_resp = client.post(
        "/api/push_injection_tasks",
        json={"session_id": session_id, "tasks": injection_data},
    )
    assert push_resp.status_code == 200
    assert push_resp.json() == {"ok": True}
    termination_resp = client.post(
        "/api/push_injection_terminations",
        json={"session_id": session_id, "nodes": ["StageB"]},
    )
    assert termination_resp.status_code == 200
    assert termination_resp.json() == {"ok": True}

    # 2. 拉取注入任务
    pull_resp = client.get(f"/api/pull_injection?session_id={session_id}")
    assert pull_resp.status_code == 200
    tasks = pull_resp.json()
    assert tasks == {
        "tasks": injection_data,
        "terminations": ["StageB"],
    }

    # 3. 再次拉取应为空（已清空）
    pull_again = client.get(f"/api/pull_injection?session_id={session_id}")
    assert pull_again.json() == {"tasks": {}, "terminations": []}


def test_task_injection_isolated_between_sessions(client):
    """不同会话的注入队列相互隔离，不会串台。"""
    graph_a = "iso_a@1000"
    graph_b = "iso_b@1000"
    _push_graph_meta(client, graph_a)
    _push_graph_meta(client, graph_b)

    client.post(
        "/api/push_injection_tasks",
        json={"session_id": graph_a, "tasks": {"StageA": [1]}},
    )
    client.post(
        "/api/push_injection_tasks",
        json={"session_id": graph_b, "tasks": {"StageB": [2]}},
    )

    pulled_a = client.get(f"/api/pull_injection?session_id={graph_a}").json()
    pulled_b = client.get(f"/api/pull_injection?session_id={graph_b}").json()

    assert pulled_a == {"tasks": {"StageA": [1]}, "terminations": []}
    assert pulled_b == {"tasks": {"StageB": [2]}, "terminations": []}


def test_task_injection_overwrites_tasklist_per_node(client):
    """新的 push 会逐个节点更新 task list，终止符单独存储。"""
    session_id = "overwrite@1000"
    _push_graph_meta(client, session_id)

    client.post(
        "/api/push_injection_tasks",
        json={"session_id": session_id, "tasks": {"StageA": [1, 2, 3]}},
    )
    client.post(
        "/api/push_injection_terminations",
        json={"session_id": session_id, "nodes": ["StageB"]},
    )

    client.post(
        "/api/push_injection_tasks",
        json={"session_id": session_id, "tasks": {"StageA": [9], "StageC": ["new"]}},
    )

    pull_resp = client.get(f"/api/pull_injection?session_id={session_id}")

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
    session_id = "badlist@1000"
    _push_graph_meta(client, session_id)
    invalid_payload = {
        "session_id": session_id,
        "tasks": {"StageA": {"user_id": 1}},
    }

    response = client.post("/api/push_injection_tasks", json=invalid_payload)

    assert response.status_code == 422


def test_termination_injection_requires_string_array(client):
    """终止符注入接口要求节点列表为字符串数组。"""
    session_id = "badterm@1000"
    _push_graph_meta(client, session_id)
    response = client.post(
        "/api/push_injection_terminations",
        json={"session_id": session_id, "nodes": {"StageA": True}},
    )

    assert response.status_code == 422


def test_injection_unknown_session_returns_409(client):
    """向未建立会话投递注入时应返回 409，而不是静默丢失。"""
    response = client.post(
        "/api/push_injection_tasks",
        json={"session_id": "ghost@1000", "tasks": {"StageA": [1]}},
    )

    assert response.status_code == 409
    assert response.json()["error"] == "unknown session_id"


def test_errors_pagination(client):
    """测试错误日志分页与过滤 API：验证后端对错误记录的聚合与分页逻辑是否正确"""
    session_id = "demo@1000"
    assert _push_graph_meta(client, session_id).status_code == 200

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
    # 错误同步已统一走 push_error（单条推送）。
    _push_errors(client, session_id, test_errors)

    # 2. 测试分页（第一页，每页10条）
    resp_p1 = client.get(
        f"/api/pull_errors?session_id={session_id}&page=1&page_size=10"
    )
    data_p1 = resp_p1.json()
    assert data_p1["total"] == 15
    assert data_p1["total_pages"] == 2
    assert len(data_p1["data"]) == 10
    assert data_p1["sort_order"] == "newest"
    assert data_p1["data"][0]["event_id"] == 14
    assert data_p1["data"][0]["task_json"] == {"value": 14, "label": "task14"}

    # 3. 测试过滤 (node=s0)
    resp_filter = client.get(f"/api/pull_errors?session_id={session_id}&node=s0")
    data_filter = resp_filter.json()
    # 0, 2, 4, 6, 8, 10, 12, 14 -> 8条
    assert data_filter["total"] == 8

    # 4. 测试关键词过滤（任务名与错误字段都可命中）
    resp_keyword = client.get(f"/api/pull_errors?session_id={session_id}&keyword=task12")
    data_keyword = resp_keyword.json()
    assert data_keyword["total"] == 1
    assert data_keyword["data"][0]["event_id"] == 12

    resp_error_keyword = client.get(
        f"/api/pull_errors?session_id={session_id}&keyword=typeerror"
    )
    data_error_keyword = resp_error_keyword.json()
    assert data_error_keyword["total"] == 7

    # 5. 测试排序（最旧优先）
    resp_oldest = client.get(
        f"/api/pull_errors?session_id={session_id}&sort_order=oldest&page_size=5"
    )
    data_oldest = resp_oldest.json()
    assert data_oldest["sort_order"] == "oldest"
    assert len(data_oldest["data"]) == 5
    assert data_oldest["data"][0]["event_id"] == 0


def test_pull_error_type_counts(client):
    """测试错误类型聚合 API：支持全部节点、单节点和缓存命中。"""
    session_id = "demo@1001"
    assert _push_graph_meta(client, session_id).status_code == 200

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
    _push_errors(client, session_id, test_errors)

    resp_all = client.get(f"/api/pull_error_type_counts?session_id={session_id}")
    assert resp_all.status_code == 200
    all_data = resp_all.json()
    assert all_data["data"] == [
        {"error_type": "ValueError", "count": 2},
        {"error_type": "TypeError", "count": 1},
    ]

    resp_node = client.get(f"/api/pull_error_type_counts?session_id={session_id}&node=s1")
    assert resp_node.status_code == 200
    node_data = resp_node.json()
    assert node_data["data"] == [
        {"error_type": "TypeError", "count": 1},
        {"error_type": "ValueError", "count": 1},
    ]

    rev = node_data["rev"]
    resp_cached = client.get(
        f"/api/pull_error_type_counts?session_id={session_id}&node=s1&known_rev={rev}"
    )
    assert resp_cached.status_code == 200
    assert resp_cached.json()["data"] is None


def test_push_errors_appends_for_same_graph(client, web_server):
    """相同 session_id 下，push_error 只追加新错误。"""
    session_id = "demo@2000"

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

    graph_meta_resp = _push_graph_meta(client, session_id)
    assert graph_meta_resp.status_code == 200
    assert graph_meta_resp.json() == {"ok": True}

    response = _push_errors(client, session_id, first_batch)
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    assert web_server.get_max_event_id_in_fail(session_id) == 2

    response = _push_errors(client, session_id, second_batch)
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    pulled = client.get(f"/api/pull_errors?session_id={session_id}&page=1&page_size=10").json()
    assert pulled["total"] == 3
    assert [item["event_id"] for item in pulled["data"]] == [3, 2, 1]


def test_push_errors_duplicate_append_is_idempotent(client):
    """重复追加相同 event_id 时，错误缓存不应出现重复行。"""
    session_id = "demo@3000"
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

    assert _push_graph_meta(client, session_id).status_code == 200

    first = _push_errors(client, session_id, duplicated_batch)
    second = _push_errors(client, session_id, duplicated_batch)

    assert first.status_code == 200
    assert second.status_code == 200

    pulled = client.get(f"/api/pull_errors?session_id={session_id}&page=1&page_size=10").json()
    assert pulled["total"] == 1
    assert [item["event_id"] for item in pulled["data"]] == [1]


def test_sessions_are_isolated_and_coexist(client):
    """多个会话可同时存在，各自的错误与图元信息互不干扰。"""
    graph_a = "coexist_a@1000"
    graph_b = "coexist_b@1000"

    assert _push_graph_meta(client, graph_a).status_code == 200
    assert _push_graph_meta(client, graph_b).status_code == 200

    _push_errors(
        client,
        graph_a,
        [
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
    )

    pulled_a = client.get(f"/api/pull_errors?session_id={graph_a}&page=1&page_size=10").json()
    pulled_b = client.get(f"/api/pull_errors?session_id={graph_b}&page=1&page_size=10").json()

    assert pulled_a["total"] == 1
    assert pulled_b["total"] == 0

    # 两个会话都仍然存活，不会因为后来者而互相覆盖。
    assert _session_summary(client, graph_a)["has_graph_meta"] is True
    assert _session_summary(client, graph_b)["has_graph_meta"] is True


def test_pull_sessions_lists_all_sessions(client, web_server):
    """会话列表返回全部会话；显示名在 graph_meta 到达后取自 graph 字段。"""
    graph_a = "list_a"
    graph_b = "list_b"
    web_server.create_session(graph_a)
    web_server.create_session(graph_b)

    by_id = {item["session_id"]: item for item in client.get("/api/pull_sessions").json()}
    assert {graph_a, graph_b} <= set(by_id)
    # graph_meta 未到达前，以 session_id 占位。
    assert by_id[graph_a]["name"] == graph_a
    assert by_id[graph_a]["alive"] is True
    assert by_id[graph_a]["created_at"] > 0

    # 推送携带 graph 的 graph_meta 后，显示名被补齐。
    assert _push_graph_meta(client, graph_a, name="list_a_named").status_code == 200
    by_id = {item["session_id"]: item for item in client.get("/api/pull_sessions").json()}
    assert by_id[graph_a]["name"] == "list_a_named"


def test_shutdown_session_marks_not_alive(client):
    """shutdown_session 将会话标记为已结束，但保留其数据。"""
    session_id = "shutdown@1000"
    assert _push_graph_meta(client, session_id).status_code == 200

    resp = client.post("/api/shutdown_session", json={"session_id": session_id})
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}

    summary = _session_summary(client, session_id)
    assert summary["alive"] is False
    # 数据仍然保留，可继续拉取。
    assert summary["has_graph_meta"] is True

    sessions = {item["session_id"]: item for item in client.get("/api/pull_sessions").json()}
    assert sessions[session_id]["alive"] is False
    assert sessions[session_id]["shutdown_reason"] == "reporter_stopped"


def test_shutdown_unknown_session_returns_409(client):
    """对不存在的会话发送 shutdown 应返回 409。"""
    resp = client.post("/api/shutdown_session", json={"session_id": "ghost@1000"})
    assert resp.status_code == 409


def test_remove_session_drops_data_and_unknown_afterwards(client):
    """remove_session 彻底移除会话，之后的拉取与 push 都视为未知会话。"""
    session_id = "removed@1000"
    assert _push_graph_meta(client, session_id).status_code == 200

    remove_resp = client.post("/api/remove_session", json={"session_id": session_id})
    assert remove_resp.status_code == 200
    assert remove_resp.json() == {"ok": True}

    # 会话已不存在：拉取返回 404，数据 push 返回 409。
    assert client.get(f"/api/pull_status?session_id={session_id}").status_code == 404
    assert (
        client.post(
            "/api/push_snapshot",
            json={"session_id": session_id, "timestamp": 1.0, "snapshot": {"s1": {"status": 0}}},
        ).status_code
        == 409
    )

    # 重复移除返回 404。
    assert client.post("/api/remove_session", json={"session_id": session_id}).status_code == 404


def test_unknown_session_pulls_return_404(client):
    """未建立会话时，各前端拉取接口应返回 404 而非 500。"""
    assert client.get("/api/pull_status?session_id=ghost@1000").status_code == 404
    assert client.get("/api/pull_graph_meta?session_id=ghost@1000").status_code == 404
    assert client.get("/api/pull_errors?session_id=ghost@1000").status_code == 404
    assert (
        client.get("/api/pull_error_type_counts?session_id=ghost@1000").status_code == 404
    )
    assert client.get("/api/pull_injection?session_id=ghost@1000").status_code == 404
