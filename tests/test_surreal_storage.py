"""Tests for SurrealDB storage layer."""
import pytest
import networkx as nx
from surrealdb import Surreal
from surreal_storage import SurrealStorage, sanitize_id, NODE_TYPE_TO_TABLE


MEM_URL = "mem://"


def make_test_graph() -> tuple[nx.DiGraph, dict]:
    """Build a minimal test graph matching CntxtCS output format."""
    g = nx.DiGraph()
    g.add_node("File: src/MyService.cs", type="file", path="src/MyService.cs", source_file="src/MyService.cs")
    g.add_node("Namespace: MyApp.Services", type="namespace", name="MyApp.Services")  # shared — no source_file
    g.add_node("Class: MyService", type="class", name="MyService", access_modifier="public", modifiers="", inherits=None, source_file="src/MyService.cs")
    g.add_node("Method: DoWork (Class: MyService)", type="method", name="DoWork", access_modifier="public", modifiers="", return_type="void", parameters=[], source_file="src/MyService.cs")
    g.add_edge("File: src/MyService.cs", "Namespace: MyApp.Services", relation="CONTAINS_NAMESPACE", source_file="src/MyService.cs")
    g.add_edge("Namespace: MyApp.Services", "Class: MyService", relation="CONTAINS_CLASS", source_file="src/MyService.cs")
    g.add_edge("Class: MyService", "Method: DoWork (Class: MyService)", relation="HAS_METHOD", source_file="src/MyService.cs")
    metadata = {
        "total_files": 1, "total_classes": 1, "total_methods": 1,
        "total_namespaces": 1, "total_interfaces": 0, "total_enums": 0,
        "total_structs": 0, "total_dependencies": 0, "total_usings": 0,
    }
    return g, metadata


class TestSanitizeId:
    def test_strips_type_prefix(self):
        assert sanitize_id("Class: MyClass") == "myclass"

    def test_handles_file_paths_with_backslash(self):
        result = sanitize_id("File: src\\MyService.cs")
        assert " " not in result
        assert "\\" not in result
        assert result  # non-empty

    def test_handles_method_with_class_qualifier(self):
        result = sanitize_id("Method: DoWork (Class: MyService)")
        assert "(" not in result
        assert ")" not in result
        assert result

    def test_handles_namespace_dots(self):
        result = sanitize_id("Namespace: System.Collections.Generic")
        assert "." not in result
        assert result == "system_collections_generic"

    def test_strips_leading_trailing_underscores(self):
        result = sanitize_id("File: /absolute/path")
        assert not result.startswith("_")
        assert not result.endswith("_")


class TestNodeTypeToTable:
    def test_all_known_types_are_mapped(self):
        known_types = [
            "file", "namespace", "class", "interface", "struct", "enum",
            "enum_member", "method", "property", "event", "field",
            "dependency_file", "dependency",
        ]
        for t in known_types:
            assert t in NODE_TYPE_TO_TABLE, f"Type '{t}' missing from NODE_TYPE_TO_TABLE"

    def test_returns_string_table_names(self):
        for node_type, table in NODE_TYPE_TO_TABLE.items():
            assert isinstance(table, str)
            assert len(table) > 0


class TestSurrealStorageWithMemory:
    def test_connect_and_close_with_mem(self):
        storage = SurrealStorage("test_project", url=MEM_URL)
        storage.connect()
        assert storage._db is not None
        storage.close()
        assert storage._db is None

    def test_context_manager(self):
        with SurrealStorage("test_project", url=MEM_URL) as storage:
            assert storage._db is not None

    def test_store_graph_upserts_records(self):
        graph, metadata = make_test_graph()
        with SurrealStorage("test_project", url=MEM_URL) as storage:
            storage.store_graph(graph, metadata)
            result = storage.query("SELECT * FROM class_node")
            assert isinstance(result, list)
            # Find the class record
            classes = result[0] if result else []
            assert any(
                r.get("node_name") == "Class: MyService"
                for r in (classes if isinstance(classes, list) else [classes])
            )

    def test_store_graph_creates_relations(self):
        graph, metadata = make_test_graph()
        with SurrealStorage("test_project", url=MEM_URL) as storage:
            storage.store_graph(graph, metadata)
            result = storage.query("SELECT * FROM has_method")
            assert isinstance(result, list)
            relations = result[0] if result else []
            assert len(relations if isinstance(relations, list) else [relations]) >= 1

    def test_rerun_merges_without_duplicates(self):
        graph, metadata = make_test_graph()
        with SurrealStorage("test_project", url=MEM_URL) as storage:
            storage.store_graph(graph, metadata)
            storage.store_graph(graph, metadata)  # Run twice
            result = storage.query("SELECT * FROM class_node")
            classes = result[0] if result else []
            class_list = classes if isinstance(classes, list) else [classes]
            # Should still only have 1 MyService class
            myservice_count = sum(1 for r in class_list if r.get("node_name") == "Class: MyService")
            assert myservice_count == 1

    def test_store_stats(self):
        graph, metadata = make_test_graph()
        with SurrealStorage("test_project", url=MEM_URL) as storage:
            storage.store_graph(graph, metadata)
            result = storage.query("SELECT * FROM codebase_stats")
            stats = result[0] if result else []
            stats_list = stats if isinstance(stats, list) else [stats]
            assert len(stats_list) >= 1

    def test_delete_file_data_removes_owned_nodes_and_edges(self):
        graph, metadata = make_test_graph()
        with SurrealStorage("test_project", url=MEM_URL) as storage:
            storage.store_graph(graph, metadata)
            storage.delete_file_data(["src/MyService.cs"])

            # Owned nodes should be gone
            classes = storage.query("SELECT * FROM class_node")[0] if storage.query("SELECT * FROM class_node") else []
            assert not any(
                r.get("node_name") == "Class: MyService"
                for r in (classes if isinstance(classes, list) else [classes])
            )
            methods = storage.query("SELECT * FROM method_node")[0] if storage.query("SELECT * FROM method_node") else []
            assert not any(
                r.get("node_name") == "Method: DoWork (Class: MyService)"
                for r in (methods if isinstance(methods, list) else [methods])
            )
            # Edges from this file should be gone
            has_method = storage.query("SELECT * FROM has_method")[0] if storage.query("SELECT * FROM has_method") else []
            assert len(has_method if isinstance(has_method, list) else [has_method]) == 0
            # Namespace node should still exist (shared)
            namespaces = storage.query("SELECT * FROM namespace")[0] if storage.query("SELECT * FROM namespace") else []
            assert len(namespaces if isinstance(namespaces, list) else [namespaces]) >= 1

    def test_store_graph_update_stats_false_skips_stats(self):
        graph, metadata = make_test_graph()
        with SurrealStorage("test_project", url=MEM_URL) as storage:
            # First store with stats
            storage.store_graph(graph, metadata)
            result_before = storage.query("SELECT * FROM codebase_stats")
            stats_before = (result_before[0] if result_before else []) or []
            stats_before = stats_before if isinstance(stats_before, list) else [stats_before]
            # Now store without updating stats
            storage.store_graph(graph, {}, update_stats=False)
            result_after = storage.query("SELECT * FROM codebase_stats")
            stats_after = (result_after[0] if result_after else []) or []
            stats_after = stats_after if isinstance(stats_after, list) else [stats_after]
            # Stats unchanged — still from first store
            assert len(stats_before) == len(stats_after)
