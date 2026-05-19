"""Tests for the CntxtCS web server API endpoints."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient


# ── Mock storage ───────────────────────────────────────────────────────────────


class MockStorage:
    """In-memory SurrealStorage stub that returns canned data."""

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def query(self, surql: str, params: dict | None = None) -> list:
        if "codebase_stats" in surql:
            return [[{"stats": {"total_files": 10, "total_classes": 5, "total_methods": 20}}]]
        if "class_node" in surql:
            return [[{"name": "MyClass", "access_modifier": "public", "modifiers": None, "inherits": None}]]
        if "interface_node" in surql:
            return [[{"name": "IService", "access_modifier": "public", "inherits": None}]]
        if "namespace" in surql:
            return [[{"name": "MyApp.Services"}]]
        if "dependency" in surql:
            return [[{"name": "Newtonsoft.Json", "version": "13.0.1"}]]
        if "code_file" in surql:
            return [[{"node_name": "File: Service.cs", "path": "Service.cs"}]]
        # Graph table queries return empty by default
        return [[]]

    @classmethod
    def list_projects(cls, **kwargs) -> list[str]:
        return ["test-project"]


# ── Fixtures ───────────────────────────────────────────────────────────────────


@pytest.fixture()
def client():
    from web_server import app
    with TestClient(app) as c:
        yield c


# ── Tests ──────────────────────────────────────────────────────────────────────


def test_list_projects(client):
    with patch("web_server.SurrealStorage", MockStorage):
        r = client.get("/api/projects")
    assert r.status_code == 200
    assert r.json() == ["test-project"]


def test_get_stats(client):
    with patch("web_server.SurrealStorage", MockStorage):
        r = client.get("/api/projects/test-project/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["total_files"] == 10
    assert data["total_classes"] == 5


def test_get_stats_not_found(client):
    class EmptyStorage(MockStorage):
        def query(self, *a, **kw):
            return []

    with patch("web_server.SurrealStorage", EmptyStorage):
        r = client.get("/api/projects/missing/stats")
    assert r.status_code == 404


def test_get_graph_from_surreal(client, monkeypatch):
    """Returns nodes from SurrealDB when available."""
    import web_server

    fake_graph = {
        "nodes": [{"id": "class_node:foo", "name": "Foo", "type": "class", "attributes": {}}],
        "links": [],
    }
    monkeypatch.setattr(web_server, "_build_graph_from_surreal", lambda _name: fake_graph)

    r = client.get("/api/projects/test-project/graph")
    assert r.status_code == 200
    data = r.json()
    assert len(data["nodes"]) == 1
    assert data["nodes"][0]["type"] == "class"


def test_build_graph_from_json(tmp_path):
    """_build_graph_from_json correctly transforms NetworkX JSON format."""
    from web_server import _build_graph_from_json

    sample = {
        "graph": {
            "nodes": [{"id": "Class: Foo", "type": "class", "name": "Foo"}],
            "links": [{"source": "Class: Foo", "target": "Namespace: Bar"}],
        }
    }
    p = tmp_path / "graph.json"
    p.write_text(json.dumps(sample))

    result = _build_graph_from_json(p)
    assert len(result["nodes"]) == 1
    assert result["nodes"][0]["type"] == "class"
    assert len(result["links"]) == 1


def test_get_classes(client):
    with patch("web_server.SurrealStorage", MockStorage):
        r = client.get("/api/projects/test-project/classes")
    assert r.status_code == 200
    assert any(c.get("name") == "MyClass" for c in r.json())


def test_get_interfaces(client):
    with patch("web_server.SurrealStorage", MockStorage):
        r = client.get("/api/projects/test-project/interfaces")
    assert r.status_code == 200
    assert any(i.get("name") == "IService" for i in r.json())


def test_get_namespaces(client):
    with patch("web_server.SurrealStorage", MockStorage):
        r = client.get("/api/projects/test-project/namespaces")
    assert r.status_code == 200
    assert "MyApp.Services" in r.json()


def test_get_dependencies(client):
    with patch("web_server.SurrealStorage", MockStorage):
        r = client.get("/api/projects/test-project/dependencies")
    assert r.status_code == 200
    assert any(d.get("name") == "Newtonsoft.Json" for d in r.json())


def test_get_files(client):
    with patch("web_server.SurrealStorage", MockStorage):
        r = client.get("/api/projects/test-project/files")
    assert r.status_code == 200
    assert len(r.json()) > 0


def test_reanalyze_no_directory(client):
    """Returns 400 when no --directory is configured at startup."""
    import web_server

    original = web_server._web_config.copy()
    web_server._web_config["directory"] = None
    try:
        r = client.post("/api/projects/test-project/reanalyze")
        assert r.status_code == 400
    finally:
        web_server._web_config.update(original)
