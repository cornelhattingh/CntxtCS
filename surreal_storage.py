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
        self._surreal: Surreal | None = None  # holds the raw Surreal context for ws:// connections

    # ── Context manager ────────────────────────────────────────────────────

    def __enter__(self) -> "SurrealStorage":
        self.connect()
        return self

    def __exit__(self, *_) -> None:
        self.close()

    # ── Connection ─────────────────────────────────────────────────────────

    _EMBEDDED_SCHEMES = ("mem://", "memory", "file://", "surrealkv://")

    def _is_embedded(self) -> bool:
        return any(self.url.startswith(s) for s in self._EMBEDDED_SCHEMES)

    def connect(self) -> None:
        """Open a connection to SurrealDB.

        Uses the context-manager protocol on the Surreal object, which works
        for both embedded backends (mem://, file://) and remote WebSocket
        backends (ws://, wss://).  The legacy .connect() method is not
        available on BlockingWsSurrealConnection in surrealdb 2.x.
        """
        self._surreal = Surreal(self.url)
        self._db = self._surreal.__enter__()
        if not self._is_embedded():
            self._db.signin({"username": self.user, "password": self.password})
        self._db.use(self.NAMESPACE, self.project_name)

    def close(self) -> None:
        """Close the database connection."""
        if self._surreal is not None:
            try:
                self._surreal.__exit__(None, None, None)
            except Exception:
                pass
            self._surreal = None
            self._db = None

    # ── Schema ─────────────────────────────────────────────────────────────

    def define_schema(self) -> None:
        """Create strongly-typed SurrealDB table and field definitions (idempotent via OVERWRITE)."""
        assert self._db is not None, "Not connected"

        def _f(table: str, field: str, type_: str) -> None:
            """DEFINE FIELD OVERWRITE shorthand."""
            self._db.query(  # type: ignore[union-attr]
                f"DEFINE FIELD OVERWRITE {field} ON TABLE {table} TYPE {type_}"
            )

        # ── Common fields shared by every node table ────────────────────────
        for table in NODE_TYPE_TO_TABLE.values():
            self._db.query(f"DEFINE TABLE OVERWRITE {table} SCHEMAFULL TYPE NORMAL")
            _f(table, "node_name",  "string")
            _f(table, "node_type",  "string")
            _f(table, "attributes", "object")
            # namespace is shared across files; all other tables are file-owned
            if table != "namespace":
                _f(table, "attributes.source_file", "option<string>")

        # ── Table-specific attribute sub-fields ─────────────────────────────
        # code_file  (type = "file")
        _f("code_file", "attributes.path", "string")

        # namespace
        _f("namespace", "attributes.name", "string")

        # class_node / interface_node / struct_node  (same shape)
        for table in ("class_node", "interface_node", "struct_node"):
            _f(table, "attributes.name",             "string")
            _f(table, "attributes.access_modifier",  "option<string>")
            _f(table, "attributes.modifiers",        "option<string>")
            _f(table, "attributes.inherits",         "option<string>")

        # enum_node
        _f("enum_node", "attributes.name",            "string")
        _f("enum_node", "attributes.access_modifier", "option<string>")

        # enum_member
        _f("enum_member", "attributes.name", "string")

        # method_node
        _f("method_node", "attributes.name",                       "string")
        _f("method_node", "attributes.access_modifier",            "option<string>")
        _f("method_node", "attributes.modifiers",                  "option<string>")
        _f("method_node", "attributes.return_type",                "option<string>")
        _f("method_node", "attributes.parameters",                 "array")
        _f("method_node", "attributes.parameters[*]",              "object")
        _f("method_node", "attributes.parameters[*].definition",   "option<string>")
        _f("method_node", "attributes.parameters[*].type",         "option<string>")
        _f("method_node", "attributes.parameters[*].name",         "option<string>")
        _f("method_node", "attributes.parameters[*].modifier",     "option<string>")
        _f("method_node", "attributes.parameters[*].default",      "option<string>")

        # property_node
        _f("property_node", "attributes.name",            "string")
        _f("property_node", "attributes.access_modifier", "option<string>")
        _f("property_node", "attributes.modifiers",       "option<string>")
        _f("property_node", "attributes.property_type",   "option<string>")
        _f("property_node", "attributes.accessors",       "option<string>")

        # event_node
        _f("event_node", "attributes.name",            "string")
        _f("event_node", "attributes.access_modifier", "option<string>")
        _f("event_node", "attributes.modifiers",       "option<string>")
        _f("event_node", "attributes.event_type",      "option<string>")

        # field_node
        _f("field_node", "attributes.name",            "string")
        _f("field_node", "attributes.access_modifier", "option<string>")
        _f("field_node", "attributes.modifiers",       "option<string>")
        _f("field_node", "attributes.field_type",      "option<string>")

        # dependency_file
        _f("dependency_file", "attributes.path", "string")

        # dependency
        _f("dependency", "attributes.name",    "string")
        _f("dependency", "attributes.version", "option<string>")

        # ── Stats table (SCHEMALESS — stats dict is heterogeneous) ──────────
        self._db.query("DEFINE TABLE OVERWRITE codebase_stats SCHEMALESS TYPE NORMAL")

        # ── Relation tables ─────────────────────────────────────────────────
        for rel_table in EDGE_TYPE_TO_TABLE.values():
            self._db.query(f"DEFINE TABLE OVERWRITE {rel_table} SCHEMAFULL TYPE RELATION")
            _f(rel_table, "relation",    "string")
            _f(rel_table, "source_file", "option<string>")

    # ── Store ──────────────────────────────────────────────────────────────

    def store_graph(
        self,
        graph: nx.DiGraph,
        metadata: dict[str, Any],
        *,
        update_stats: bool = True,
    ) -> None:
        """Upsert all nodes and relations from the NetworkX graph into SurrealDB."""
        assert self._db is not None, "Not connected"

        self.define_schema()
        self._store_nodes(graph)
        self._store_edges(graph)
        if update_stats:
            self._store_stats(metadata)

    def _store_nodes(self, graph: nx.DiGraph) -> None:
        """Upsert all nodes into their respective tables."""
        for node_name, attrs in graph.nodes(data=True):
            node_type = attrs.get("type", "file")
            table = NODE_TYPE_TO_TABLE.get(node_type, "code_file")
            record_id = sanitize_id(node_name)
            # Collect all extra attributes, dropping None values so SurrealDB
            # never tries to coerce NONE into a non-optional schema field.
            extra = {k: v for k, v in attrs.items() if k != "type" and v is not None}
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
            edge_rid = RecordID(rel_table, edge_id)

            source_file = edge_attrs.get("source_file", "")

            # Use RELATE statement to create the graph edge (idempotent with explicit ID)
            self._db.query(
                f"RELATE $src->{rel_table}->$dst "
                f"SET relation = $relation, source_file = $source_file, id = $edge_rid",
                {
                    "src": src_rid,
                    "dst": dst_rid,
                    "relation": relation,
                    "source_file": source_file,
                    "edge_rid": edge_rid,
                },
            )

    def _store_stats(self, metadata: dict[str, Any]) -> None:
        """Upsert codebase statistics."""
        self._db.upsert(
            RecordID("codebase_stats", self.project_name),
            {"stats": metadata},
        )

    def delete_file_data(self, file_paths: list[str]) -> None:
        """Delete all owned nodes and relation edges that originated from the given
        source files.  Namespace nodes are shared and are intentionally left in place."""
        assert self._db is not None, "Not connected"
        for path in file_paths:
            # Remove owned node records
            for node_type, table in NODE_TYPE_TO_TABLE.items():
                if node_type == "namespace":
                    continue
                self._db.query(
                    f"DELETE {table} WHERE attributes.source_file = $path",
                    {"path": path},
                )
            # Remove relation edges
            for rel_table in EDGE_TYPE_TO_TABLE.values():
                self._db.query(
                    f"DELETE {rel_table} WHERE source_file = $path",
                    {"path": path},
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
            # SurrealDB 2.x returns the INFO dict directly (not wrapped in a list)
            info: dict | None = None
            if isinstance(result, dict):
                info = result
            elif isinstance(result, list) and result and isinstance(result[0], dict):
                info = result[0]
            if info:
                return [
                    name for name in info.get("databases", {}).keys()
                    if name != "information_schema"
                ]
        return []
