"""SurrealDB storage layer for CntxtCS knowledge graphs."""

import os
import re
from typing import Any
import networkx as nx
from dotenv import load_dotenv
from surrealdb import Surreal, RecordID

load_dotenv()


# Maps NetworkX node type strings to SurrealDB table names
NODE_TYPE_TO_TABLE = {
    "file": "code_file",
    "namespace": "namespace",
    "class": "class_node",
    "interface": "interface_node",
    "struct": "struct_node",
    "enum": "enum_node",
    "enum_member": "enum_member",
    "method": "method_node",
    "property": "property_node",
    "event": "event_node",
    "field": "field_node",
    "dependency_file": "dependency_file",
    "dependency": "dependency",
}

# Maps NetworkX edge relation strings to SurrealDB relation table names
EDGE_TYPE_TO_TABLE = {
    "USES_NAMESPACE": "uses_namespace",
    "CONTAINS_NAMESPACE": "contains_namespace",
    "CONTAINS_CLASS": "contains_class",
    "CONTAINS_INTERFACE": "contains_interface",
    "CONTAINS_ENUM": "contains_enum",
    "CONTAINS_STRUCT": "contains_struct",
    "HAS_METHOD": "has_method",
    "HAS_PROPERTY": "has_property",
    "HAS_EVENT": "has_event",
    "HAS_FIELD": "has_field",
    "INHERITS": "inherits",
    "INHERITS_INTERFACE": "inherits_interface",
    "HAS_MEMBER": "has_member",
    "HAS_DEPENDENCY": "has_dependency",
    "HAS_LOCKED_DEPENDENCY": "has_locked_dependency",
}


def sanitize_id(node_name: str) -> str:
    """Convert a NetworkX node name to a safe SurrealDB record ID.
    
    Examples:
        "Class: MyClass" -> "myclass"
        "File: path/to/file.cs" -> "path_to_file_cs"
        "Method: DoSomething (Class: MyClass)" -> "dosomething_class_myclass"
        "Namespace: System.Collections.Generic" -> "system_collections_generic"
    """
    # Remove type prefix (e.g., "Class: ", "Method: ", "File: ", etc.)
    result = re.sub(r'^[A-Za-z]+:\s*', '', node_name)
    # Replace path separators, spaces, parens, colons, dots, backslashes with underscore
    result = re.sub(r'[/\\:.()\s]+', '_', result)
    # Remove consecutive underscores
    result = re.sub(r'_+', '_', result)
    # Strip leading/trailing underscores
    result = result.strip('_')
    return result.lower()


class SurrealStorage:
    """Stores and retrieves CntxtCS knowledge graphs in SurrealDB.
    
    SurrealDB namespace is always 'cntxt'. Each project gets its own database.
    """

    NAMESPACE = "cntxt"

    def __init__(
        self,
        project_name: str,
        url: str | None = None,
        user: str | None = None,
        password: str | None = None,
    ):
        self.project_name = project_name
        self.url = url or os.getenv("SURREAL_URL", "ws://localhost:8000")
        self.user = user or os.getenv("SURREAL_USER", "root")
        self.password = password or os.getenv("SURREAL_PASS", "root")
        self._db: Surreal | None = None

    # ── Context manager ────────────────────────────────────────────────────

    def __enter__(self) -> "SurrealStorage":
        self.connect()
        return self

    def __exit__(self, *_) -> None:
        self.close()

    # ── Connection ─────────────────────────────────────────────────────────

    def connect(self) -> None:
        """Open a connection to SurrealDB."""
        self._db = Surreal(self.url)
        self._db.connect()
        # Only sign in when not using embedded mode
        if not self.url.startswith("mem://") and not self.url.startswith("file://") and not self.url.startswith("surrealkv://"):
            self._db.signin({"username": self.user, "password": self.password})
        self._db.use(self.NAMESPACE, self.project_name)

    def close(self) -> None:
        """Close the database connection."""
        if self._db is not None:
            self._db.close()
            self._db = None

    # ── Schema ─────────────────────────────────────────────────────────────

    def define_schema(self) -> None:
        """Create SurrealDB table definitions (idempotent)."""
        assert self._db is not None, "Not connected"
        # Node tables
        for table in NODE_TYPE_TO_TABLE.values():
            self._db.query(f"DEFINE TABLE IF NOT EXISTS {table} SCHEMAFULL TYPE NORMAL")
            self._db.query(f"DEFINE FIELD IF NOT EXISTS node_name ON TABLE {table} TYPE string")
            self._db.query(f"DEFINE FIELD IF NOT EXISTS node_type ON TABLE {table} TYPE string")
            self._db.query(f"DEFINE FIELD IF NOT EXISTS attributes ON TABLE {table} FLEXIBLE TYPE object")
        # Store-level stats table
        self._db.query("DEFINE TABLE IF NOT EXISTS codebase_stats SCHEMAFULL TYPE NORMAL")
        self._db.query("DEFINE FIELD IF NOT EXISTS stats ON TABLE codebase_stats FLEXIBLE TYPE object")
        # Relation tables
        for rel_table in EDGE_TYPE_TO_TABLE.values():
            self._db.query(f"DEFINE TABLE IF NOT EXISTS {rel_table} SCHEMAFULL TYPE RELATION")

    # ── Store ──────────────────────────────────────────────────────────────

    def store_graph(self, graph: nx.DiGraph, metadata: dict[str, Any]) -> None:
        """Upsert all nodes and relations from the NetworkX graph into SurrealDB."""
        assert self._db is not None, "Not connected"

        self.define_schema()
        self._store_nodes(graph)
        self._store_edges(graph)
        self._store_stats(metadata)

    def _store_nodes(self, graph: nx.DiGraph) -> None:
        """Upsert all nodes into their respective tables."""
        for node_name, attrs in graph.nodes(data=True):
            node_type = attrs.get("type", "file")
            table = NODE_TYPE_TO_TABLE.get(node_type, "code_file")
            record_id = sanitize_id(node_name)
            # Collect all extra attributes
            extra = {k: v for k, v in attrs.items() if k != "type"}
            self._db.upsert(
                RecordID(table, record_id),
                {
                    "node_name": node_name,
                    "node_type": node_type,
                    "attributes": extra,
                },
            )

    def _store_edges(self, graph: nx.DiGraph) -> None:
        """Upsert all edges as SurrealDB relations."""
        for src_name, dst_name, edge_attrs in graph.edges(data=True):
            relation = edge_attrs.get("relation", "")
            rel_table = EDGE_TYPE_TO_TABLE.get(relation)
            if rel_table is None:
                continue  # Skip unknown relation types

            src_type = graph.nodes[src_name].get("type", "file")
            dst_type = graph.nodes[dst_name].get("type", "file")
            src_table = NODE_TYPE_TO_TABLE.get(src_type, "code_file")
            dst_table = NODE_TYPE_TO_TABLE.get(dst_type, "code_file")

            src_rid = RecordID(src_table, sanitize_id(src_name))
            dst_rid = RecordID(dst_table, sanitize_id(dst_name))

            # Build a deterministic ID for the relation edge
            edge_id = sanitize_id(src_name) + "_" + sanitize_id(dst_name)
            
            # Use RELATE statement to create the graph edge (idempotent with explicit ID)
            self._db.query(
                f"RELATE $src->{rel_table}->$dst SET relation = $relation, id = type::thing($rel_table, $edge_id)",
                {
                    "src": src_rid,
                    "dst": dst_rid,
                    "relation": relation,
                    "rel_table": rel_table,
                    "edge_id": edge_id,
                },
            )

    def _store_stats(self, metadata: dict[str, Any]) -> None:
        """Upsert codebase statistics."""
        self._db.upsert(
            RecordID("codebase_stats", self.project_name),
            {"stats": metadata},
        )

    # ── Query helpers (used by MCP server) ─────────────────────────────────

    def query(self, surql: str, params: dict | None = None) -> list:
        """Run a SurrealQL query and return results."""
        assert self._db is not None, "Not connected"
        result = self._db.query(surql, params or {})
        if isinstance(result, list):
            return result
        return [result]

    @classmethod
    def list_projects(
        cls,
        url: str | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> list[str]:
        """Return all project names (databases) under the 'cntxt' namespace."""
        load_dotenv()
        _url = url or os.getenv("SURREAL_URL", "ws://localhost:8000")
        _user = user or os.getenv("SURREAL_USER", "root")
        _pass = password or os.getenv("SURREAL_PASS", "root")

        with Surreal(_url) as db:
            if not _url.startswith("mem://"):
                db.signin({"username": _user, "password": _pass})
            db.use(cls.NAMESPACE, "information_schema")
            result = db.query("INFO FOR NS")
            if result and isinstance(result, list) and result[0]:
                info = result[0]
                if isinstance(info, dict):
                    return list(info.get("databases", {}).keys())
        return []
