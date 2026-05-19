"""Tests for MCP server tools — uses mem:// in-process SurrealDB."""
import os
import sys
import pytest
import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from surreal_storage import SurrealStorage

MEM_URL = "mem://"
TEST_PROJECT = "mcp_test_project"

# Shared storage instance for all tests
_shared_storage = None


def _seed_storage(project: str = TEST_PROJECT) -> SurrealStorage:
    g = nx.DiGraph()
    g.add_node("File: src/UserService.cs", type="file", path="src/UserService.cs")
    g.add_node("Namespace: MyApp.Services", type="namespace", name="MyApp.Services")
    g.add_node("Class: UserService", type="class", name="UserService",
               access_modifier="public", modifiers="", inherits="IUserService")
    g.add_node("Interface: IUserService", type="interface", name="IUserService",
               access_modifier="public", modifiers="", inherits=None)
    g.add_node("Method: GetUser (Class: UserService)", type="method", name="GetUser",
               access_modifier="public", modifiers="", return_type="User",
               parameters=[{"name": "id", "type": "int"}])
    g.add_node("Method: CreateUser (Class: UserService)", type="method", name="CreateUser",
               access_modifier="public", modifiers="async", return_type="Task",
               parameters=[])
    g.add_node("Dependency: Newtonsoft.Json", type="dependency",
               name="Newtonsoft.Json", version="13.0.1")
    g.add_edge("Namespace: MyApp.Services", "Class: UserService", relation="CONTAINS_CLASS")
    g.add_edge("Namespace: MyApp.Services", "Interface: IUserService", relation="CONTAINS_INTERFACE")
    g.add_edge("Class: UserService", "Method: GetUser (Class: UserService)", relation="HAS_METHOD")
    g.add_edge("Class: UserService", "Method: CreateUser (Class: UserService)", relation="HAS_METHOD")
    g.add_edge("Class: UserService", "Interface: IUserService", relation="INHERITS")
    metadata = {"stats": {"total_files": 1, "total_classes": 1, "total_methods": 2,
                          "total_interfaces": 1, "total_enums": 0, "total_structs": 0,
                          "total_namespaces": 1, "total_dependencies": 1, "total_usings": 0}}
    storage = SurrealStorage(project, url=MEM_URL)
    storage.connect()
    storage.store_graph(g, metadata)
    return storage


@pytest.fixture(autouse=True)
def patch_storage(monkeypatch):
    """Patch mcp_server._q to use shared in-memory DB."""
    global _shared_storage
    if _shared_storage is None:
        _shared_storage = _seed_storage()
    
    def patched_q(project: str, surql: str, params: dict | None = None) -> list:
        """Patched _q that uses the shared storage."""
        result = _shared_storage.query(surql, params or {})
        if result and isinstance(result[0], list):
            return result[0]
        return result if isinstance(result, list) else []
    
    monkeypatch.setattr("mcp_server._q", patched_q)
    
    # Also patch list_projects to return our test project
    monkeypatch.setattr("mcp_server.SurrealStorage.list_projects", lambda: [TEST_PROJECT])


@pytest.fixture(scope="module")
def seeded():
    global _shared_storage
    _shared_storage = _seed_storage()
    yield _shared_storage
    if _shared_storage:
        _shared_storage.close()
        _shared_storage = None


class TestListClasses:
    def test_returns_list(self, seeded):
        import mcp_server
        result = mcp_server.list_classes(TEST_PROJECT)
        assert isinstance(result, list)

    def test_contains_expected_class(self, seeded):
        import mcp_server
        names = [r.get("name") for r in mcp_server.list_classes(TEST_PROJECT)]
        assert "UserService" in names


class TestGetClassDetails:
    def test_returns_dict(self, seeded):
        import mcp_server
        result = mcp_server.get_class_details(TEST_PROJECT, "UserService")
        assert isinstance(result, dict)

    def test_name_field_present(self, seeded):
        import mcp_server
        result = mcp_server.get_class_details(TEST_PROJECT, "UserService")
        assert result.get("name") == "UserService"


class TestSearchCodeElements:
    def test_finds_results(self, seeded):
        import mcp_server
        result = mcp_server.search_code_elements(TEST_PROJECT, "user")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_type_filter_restricts(self, seeded):
        import mcp_server
        result = mcp_server.search_code_elements(TEST_PROJECT, "user", type_filter="class")
        for r in result:
            assert r.get("node_type") == "class"


class TestGetCodbaseStats:
    def test_returns_dict(self, seeded):
        import mcp_server
        result = mcp_server.get_codebase_stats(TEST_PROJECT)
        assert isinstance(result, dict)


class TestListDependencies:
    def test_returns_list(self, seeded):
        import mcp_server
        result = mcp_server.list_dependencies(TEST_PROJECT)
        assert isinstance(result, list)

    def test_contains_package(self, seeded):
        import mcp_server
        names = [r.get("name") for r in mcp_server.list_dependencies(TEST_PROJECT)]
        assert "Newtonsoft.Json" in names


class TestFindImplementations:
    def test_returns_list(self, seeded):
        import mcp_server
        result = mcp_server.find_implementations(TEST_PROJECT, "IUserService")
        assert isinstance(result, list)

    def test_finds_userservice(self, seeded):
        import mcp_server
        result = mcp_server.find_implementations(TEST_PROJECT, "IUserService")
        assert "UserService" in result
