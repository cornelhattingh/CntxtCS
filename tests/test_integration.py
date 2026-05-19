"""Integration tests for CntxtCS.py SurrealDB integration."""
from unittest.mock import MagicMock, patch
import pytest
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestRunWithoutSurreal:
    def test_run_without_surreal_does_not_import_storage(self, tmp_path):
        """When --surreal is not set, SurrealStorage should not be called."""
        from CntxtCS import CSCodeKnowledgeGraph
        import networkx as nx

        # Create a minimal graph (no actual C# files needed)
        ckg = CSCodeKnowledgeGraph(str(tmp_path))
        ckg.graph = nx.DiGraph()
        ckg.graph.add_node("File: test.cs", type="file", path="test.cs")
        ckg.total_files = 1
        ckg.total_namespaces = 0
        ckg.total_classes = 0
        ckg.total_methods = 0
        ckg.total_interfaces = 0
        ckg.total_enums = 0
        ckg.total_structs = 0
        ckg.total_usings = 0
        ckg.total_dependencies = set()

        output = tmp_path / "graph.json"
        with patch.object(ckg, 'save_graph') as mock_save, \
             patch('builtins.input', return_value='no'), \
             patch('surreal_storage.SurrealStorage') as mock_storage:
            mock_save.return_value = None
            ckg.run(surreal=False)
            mock_storage.assert_not_called()


class TestRunWithSurreal:
    def test_run_with_surreal_calls_storage(self, tmp_path):
        """When --surreal is set, SurrealStorage.store_graph should be called."""
        from CntxtCS import CSCodeKnowledgeGraph
        import networkx as nx

        ckg = CSCodeKnowledgeGraph(str(tmp_path))
        ckg.graph = nx.DiGraph()
        ckg.graph.add_node("Class: Foo", type="class", name="Foo")
        ckg.total_files = 1
        ckg.total_namespaces = 0
        ckg.total_classes = 1
        ckg.total_methods = 0
        ckg.total_interfaces = 0
        ckg.total_enums = 0
        ckg.total_structs = 0
        ckg.total_usings = 0
        ckg.total_dependencies = set()

        mock_storage_instance = MagicMock()
        mock_storage_instance.__enter__ = MagicMock(return_value=mock_storage_instance)
        mock_storage_instance.__exit__ = MagicMock(return_value=False)

        with patch.object(ckg, 'save_graph'), \
             patch('builtins.input', return_value='no'), \
             patch('CntxtCS.SurrealStorage', return_value=mock_storage_instance) as mock_cls:
            ckg.run(surreal=True, project_name="myproject")
            mock_cls.assert_called_once_with("myproject")
            mock_storage_instance.store_graph.assert_called_once()

    def test_run_with_surreal_no_project_raises(self, tmp_path):
        """--surreal without --project should raise ValueError."""
        from CntxtCS import CSCodeKnowledgeGraph
        import networkx as nx

        ckg = CSCodeKnowledgeGraph(str(tmp_path))
        ckg.graph = nx.DiGraph()
        ckg.total_files = 0
        ckg.total_namespaces = 0
        ckg.total_classes = 0
        ckg.total_methods = 0
        ckg.total_interfaces = 0
        ckg.total_enums = 0
        ckg.total_structs = 0
        ckg.total_usings = 0
        ckg.total_dependencies = set()

        with patch.object(ckg, 'save_graph'), \
             patch('builtins.input', return_value='no'):
            with pytest.raises(ValueError, match="--project is required"):
                ckg.run(surreal=True, project_name=None)
