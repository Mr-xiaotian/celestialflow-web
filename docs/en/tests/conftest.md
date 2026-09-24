# tests/conftest.py

> 📅 Last Updated: 2026/09/24

## Role
Provides Pytest fixtures for the Web server and HTTP client for the test cases under the `tests/` directory, simulating a real frontend-backend interaction environment.

## Core Fixtures
- `web_server`:
  - **Function**: Initializes a `TaskWebServer` instance with the default configuration.
  - **Scope**: A new instance is created before each test function runs.
- `client`:
  - **Function**: Creates a synchronous HTTP client based on `FastAPI.testclient.TestClient`.
  - **Dependency**: Depends on the `web_server` fixture and directly accesses its internal `app` instance.

## Usage Example
```python
def test_index_page(client):
    """Verify that the home page is accessible and contains the key container."""
    response = client.get("/")
    assert response.status_code == 200
    assert 'id="dashboard"' in response.text
```

## Notes
- The tests use FastAPI's built-in TestClient, which does not actually start a port listener, so execution is efficient and there is no risk of port conflicts.
- The related implementation is located in `src/celestialflow_web/server/core_server.py`.
