# tests/__init__.py

> 📅 Last Updated: 2026/09/24

## Role
`tests/` covers the interface and page integration behavior of the CelestialFlow Web layer, ensuring that state snapshot isolation, status pull/push, graph meta information synchronization, configuration pulling, task injection, error pagination/filtering, graph context switching, and ignoring of stale pushes remain stable.

## Files Included
- `__init__.py`: An empty file, used only to mark `tests/` as a Python package; it contains no test code or shared logic.
- `conftest.py`: Provides the two Pytest fixtures `web_server` and `client`.
- `test_server.py`: Covers Web API integration tests such as snapshot isolation, the dashboard home page, frontend module evaluation order, the configuration API, status and graph meta information synchronization, task injection, and error pagination.

## How to Run

```bash
# Run everything
uv run pytest tests -v

# Run only the server integration tests
uv run pytest tests/test_server.py -v
```
