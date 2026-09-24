# src/celestialflow_web/runtime/util_config.py

> 📅 Last Updated: 2026/09/24

Configuration file read/write utilities for the Web module, responsible for persistent management of `config.json`. There is no thread lock protection — thread safety is guaranteed by the upper-level caller (the `push_config` route in `routes/core_push.py`, together with `server.TaskWebServer.config_lock`).

## load_config

```python
def load_config(config_path: str) -> dict[str, Any]:
    """Load and validate the frontend configuration from the specified path, returning a dictionary."""
```

- **File does not exist**: throws `ConfigurationError` directly, and does not initialize from a default template.
- Checks file existence with `os.path.exists()` and then reads the JSON with UTF-8 encoding.

## save_config

```python
def save_config(config: dict[str, Any], config_path: str) -> bool:
    """Save the frontend configuration to a JSON file, returning whether it succeeded."""
```

- Writes in `w` mode, with `indent=4` and `ensure_ascii=False` to ensure readability and Chinese support.
- Has no built-in thread lock; multi-concurrency safety is handled by the caller — the `push_config` route in `routes/core_push.py` (using `TaskWebServer.config_lock`).
- Catches all `Exception`s and, on failure, prints the error message and returns `False`.

## Call Relationships

```mermaid
flowchart LR
    A[push_config<br/>routes/core_push.py] --> B[save_config]
    B --> C["config.json"]
    A --> D[TaskWebServer.config_lock<br/>thread safety]
```

| Function | Thread safety | Exception handling |
|------|---------|---------|
| `load_config` | Not applicable (read-only) | File does not exist → `ConfigurationError`; JSON parse failure → propagates upward |
| `save_config` | ❌ No lock, guaranteed by the caller | Write exception → prints the error and returns `False` |

## Usage Examples

### Complete Usage Example of load_config / save_config

```python
from celestialflow_web.runtime.util_config import load_config, save_config

# Assume config.json uses the new nested grouped structure:
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

# --- Read configuration ---
try:
    config = load_config(config_path)
    print(f"Loaded successfully, theme: {config['global']['theme']}")
    print(f"Refresh interval: {config['global']['refreshInterval']}ms")
    print(f"Language: {config['global']['language']}")
    print(f"Left panel cards: {config['dashboard']['layout']['left']}")
except Exception as e:
    print(f"Failed to load configuration: {e}")

# --- Modify and save the configuration ---
config["global"]["theme"] = "light"
config["global"]["refreshInterval"] = 3000
config["global"]["language"] = "en"

success = save_config(config, config_path)
if success:
    print("Configuration saved successfully")
else:
    print("Failed to save configuration")

# --- Verify the save result ---
reloaded = load_config(config_path)
print(f"Theme after reload: {reloaded['global']['theme']}")  # light
print(f"Language after reload: {reloaded['global']['language']}")  # en
```

### Using It Together with WebConfigModel

```python
from celestialflow_web.runtime.util_config import load_config, save_config

# The full structure of config.json conforms to the WebConfigModel Pydantic model
# It is recommended to validate with the Pydantic model before saving / after reading

try:
    raw_config = load_config("/path/to/config.json")

    # Validate using the Pydantic model (assumed to be in core_server.py)
    from celestialflow_web.runtime.util_models import WebConfigModel

    validated = WebConfigModel.model_validate(raw_config)

    print(
        f"Validation passed: theme={validated.global_.theme}, refresh={validated.global_.refreshInterval}ms"
    )

    # Save after modification
    validated.global_.theme = "dark"
    save_config(validated.model_dump(by_alias=True), "/path/to/config.json")
except Exception as e:
    print(f"Configuration processing failed: {e}")
```
