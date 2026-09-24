# src/celestialflow_web/runtime/util_config.py

> 📅 最終更新日: 2026/09/24

Web モジュールの設定ファイル読み書きユーティリティで、`config.json` の永続化管理を担当します。スレッドロックによる保護はありません——スレッド安全性は上位の呼び出し側（`routes/core_push.py` の `push_config` ルートと `server.TaskWebServer.config_lock`）が保証します。

## load_config

```python
def load_config(config_path: str) -> dict[str, Any]:
    """指定パスからフロントエンド設定を読み込んで検証し、辞書を返す。"""
```

- **ファイルが存在しない場合**：直接 `ConfigurationError` をスローし、デフォルトテンプレートからの初期化は行いません。
- `os.path.exists()` でファイルの存在を判定した後、UTF-8 エンコーディングで JSON を読み込みます。

## save_config

```python
def save_config(config: dict[str, Any], config_path: str) -> bool:
    """フロントエンド設定を JSON ファイルに保存し、成否を返す。"""
```

- `w` モードで書き込み、`indent=4`、`ensure_ascii=False` で可読性と中国語サポートを確保します。
- 組み込みのスレッドロックはなく、多重並行の安全性は呼び出し側 `routes/core_push.py` の `push_config` ルート（`TaskWebServer.config_lock` を使用）が処理します。
- すべての `Exception` を捕捉し、失敗時はエラーメッセージを出力して `False` を返します。

## 呼び出し関係

```mermaid
flowchart LR
    A[push_config<br/>routes/core_push.py] --> B[save_config]
    B --> C["config.json"]
    A --> D[TaskWebServer.config_lock<br/>スレッドセーフ]
```

| 関数 | スレッドセーフ | 例外処理 |
|------|---------|---------|
| `load_config` | 対象外（読み取り専用） | ファイルが存在しない → `ConfigurationError`；JSON 解析失敗 → 上位へ伝播 |
| `save_config` | ❌ ロックなし、呼び出し側が保証 | 書き込み例外 → エラーを出力し `False` を返す |

## 使用例

### load_config / save_config の完全な使用例

```python
from celestialflow_web.runtime.util_config import load_config, save_config

# config.json が新しいネストされたグループ構造であると仮定：
# {
#     "global": {
#         "theme": "dark",
#         "refreshInterval": 5000,
#         "language": "zh-CN"
#     },
#     "dashboard": {
#         "historyLimit": 20,
#         "layout": {
#             "left": ["mermaid"],
#             "middle": ["status"],
#             "right": ["progress"]
#         }
#     }
# }

config_path = "/path/to/celestialflow_web/config.json"

# --- 設定を読み込む ---
try:
    config = load_config(config_path)
    print(f"読み込み成功、テーマ: {config['global']['theme']}")
    print(f"リフレッシュ間隔: {config['global']['refreshInterval']}ms")
    print(f"言語: {config['global']['language']}")
    print(f"左パネルのカード: {config['dashboard']['layout']['left']}")
except Exception as e:
    print(f"設定の読み込みに失敗: {e}")

# --- 設定を変更して保存 ---
config["global"]["theme"] = "light"
config["global"]["refreshInterval"] = 3000
config["global"]["language"] = "en"

success = save_config(config, config_path)
if success:
    print("設定の保存に成功")
else:
    print("設定の保存に失敗")

# --- 保存結果を検証 ---
reloaded = load_config(config_path)
print(f"再読み込み後のテーマ: {reloaded['global']['theme']}")  # light
print(f"再読み込み後の言語: {reloaded['global']['language']}")  # en
```

### WebConfigModel と組み合わせて使用

```python
from celestialflow_web.runtime.util_config import load_config, save_config

# config.json の完全な構造は WebConfigModel Pydantic モデルに適合する
# 保存前/読み込み後に Pydantic モデルで検証することを推奨

try:
    raw_config = load_config("/path/to/config.json")

    # Pydantic モデルで検証（core_server.py 内を想定）
    from celestialflow_web.runtime.util_models import WebConfigModel

    validated = WebConfigModel.model_validate(raw_config)

    print(
        f"検証成功: テーマ={validated.global_.theme}, リフレッシュ={validated.global_.refreshInterval}ms"
    )

    # 変更して保存
    validated.global_.theme = "dark"
    save_config(validated.model_dump(by_alias=True), "/path/to/config.json")
except Exception as e:
    print(f"設定の処理に失敗: {e}")
```
