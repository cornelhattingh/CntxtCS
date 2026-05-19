"""FastAPI web server for CntxtCS — REST API and optional static UI host."""

import json
import os
import threading
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from surreal_storage import SurrealStorage

# ── App setup ─────────────────────────────────────────────────────────────────

app = FastAPI(title="CntxtCS", version="0.1.0", docs_url="/api/docs", redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",
        "http://localhost:8080",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve-mode state ──────────────────────────────────────────────────────────

_web_config: dict[str, str | None] = {
    "directory": None,
}

# Tracks the state of an async full-scan triggered via the UI.
_scan_status: dict[str, Any] = {
    "scanning": False,
    "error": None,
    "last_completed": None,
}

# ── Query helpers ─────────────────────────────────────────────────────────────


def _unwrap(result: Any) -> list:
    """Unwrap a SurrealDB query result into a flat list of records."""
    if isinstance(result, list) and result and isinstance(result[0], list):
        return result[0]
    return result if isinstance(result, list) else []


def _q(project: str, surql: str, params: dict | None = None) -> list:
    """Open a connection, run one SurrealQL query, return unwrapped records."""
    with SurrealStorage(project) as s:
        return _unwrap(s.query(surql, params or {}))


# ── Graph builders ────────────────────────────────────────────────────────────

_NODE_TABLES = [
    "code_file", "namespace", "class_node", "interface_node", "struct_node",
    "enum_node", "enum_member", "method_node", "property_node", "field_node",
    "event_node", "dependency_file", "dependency",
]

_EDGE_TABLES = [
    "uses_namespace", "contains_namespace", "contains_class", "contains_interface",
    "contains_enum", "contains_struct", "has_method", "has_property", "has_event",
    "has_field", "inherits", "inherits_interface", "has_member", "has_dependency",
    "has_locked_dependency",
]


def _build_graph_from_surreal(name: str) -> dict[str, Any]:
    """Query SurrealDB for all nodes and edges in a single connection."""
    nodes: list[dict] = []
    links: list[dict] = []
    seen_ids: set[str] = set()

    with SurrealStorage(name) as s:
        for table in _NODE_TABLES:
            try:
                rows = _unwrap(s.query(
                    f"SELECT id, node_name, node_type, attributes FROM {table}"
                ))
                for row in rows:
                    node_id = str(row.get("id", ""))
                    if not node_id or node_id in seen_ids:
                        continue
                    seen_ids.add(node_id)
                    attrs = row.get("attributes") or {}
                    nodes.append({
                        "id": node_id,
                        "name": (
                            attrs.get("name")
                            or attrs.get("path")
                            or row.get("node_name", node_id)
                        ),
                        "type": row.get("node_type") or table,
                        "attributes": attrs,
                    })
            except Exception:
                pass

        for table in _EDGE_TABLES:
            try:
                rows = _unwrap(s.query(f"SELECT in, out FROM {table}"))
                for row in rows:
                    src = str(row.get("in", ""))
                    dst = str(row.get("out", ""))
                    if src and dst:
                        links.append({"source": src, "target": dst, "type": table})
            except Exception:
                pass

    return {"nodes": nodes, "links": links}


def _build_graph_from_json(path: Path) -> dict[str, Any]:
    """Transform a NetworkX JSON graph export → {nodes, links} for react-force-graph."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    g = data.get("graph", data)
    raw_nodes = g.get("nodes", [])
    raw_edges = g.get("links", g.get("edges", []))

    nodes = [
        {
            "id": n["id"],
            "name": n.get("name") or n.get("path") or n["id"],
            "type": n.get("type", "unknown"),
            "attributes": {k: v for k, v in n.items() if k not in ("id", "type")},
        }
        for n in raw_nodes
        if n.get("id")
    ]
    links = [
        {
            "source": e.get("source") or e.get("from") or e.get("u") or "",
            "target": e.get("target") or e.get("to") or e.get("v") or "",
            "type": e.get("type") or e.get("key", ""),
        }
        for e in raw_edges
        if (e.get("source") or e.get("from") or e.get("u"))
        and (e.get("target") or e.get("to") or e.get("v"))
    ]
    return {"nodes": nodes, "links": links}


# ── API endpoints ─────────────────────────────────────────────────────────────


@app.get("/api/projects")
def get_projects() -> list[str]:
    """List all analysed projects stored in SurrealDB."""
    return SurrealStorage.list_projects()


@app.get("/api/projects/{name}/stats")
def get_stats(name: str) -> dict[str, Any]:
    """Return codebase statistics for a project."""
    rows = _q(name, "SELECT * FROM codebase_stats LIMIT 1")
    if not rows:
        raise HTTPException(status_code=404, detail=f"No stats found for project '{name}'")
    row = rows[0] if isinstance(rows, list) else rows
    return row.get("stats", {})


@app.get("/api/projects/{name}/graph")
def get_graph(name: str) -> dict[str, Any]:
    """Return graph as {nodes, links}. Tries SurrealDB first; falls back to JSON file."""
    # SurrealDB first (efficient — avoids loading multi-MB JSON for large projects)
    try:
        data = _build_graph_from_surreal(name)
        if data["nodes"]:
            return data
    except Exception:
        pass

    # JSON fallback (last generated cs_code_knowledge_graph.json in cwd)
    json_path = Path("cs_code_knowledge_graph.json")
    if json_path.exists():
        return _build_graph_from_json(json_path)

    return {"nodes": [], "links": []}


@app.get("/api/projects/{name}/classes")
def get_classes(name: str) -> list[dict[str, Any]]:
    """List all classes in the project."""
    return _q(
        name,
        "SELECT attributes.name AS name, attributes.access_modifier AS access_modifier, "
        "attributes.modifiers AS modifiers, attributes.inherits AS inherits "
        "FROM class_node ORDER BY name",
    )


@app.get("/api/projects/{name}/interfaces")
def get_interfaces(name: str) -> list[dict[str, Any]]:
    """List all interfaces in the project."""
    return _q(
        name,
        "SELECT attributes.name AS name, attributes.access_modifier AS access_modifier, "
        "attributes.inherits AS inherits FROM interface_node ORDER BY name",
    )


@app.get("/api/projects/{name}/namespaces")
def get_namespaces(name: str) -> list[str]:
    """List all namespaces in the project."""
    rows = _q(name, "SELECT attributes.name AS name FROM namespace ORDER BY name")
    return sorted({r.get("name", "") for r in rows if r.get("name")})


@app.get("/api/projects/{name}/dependencies")
def get_dependencies(name: str) -> list[dict[str, Any]]:
    """List NuGet package dependencies for the project."""
    return _q(
        name,
        "SELECT attributes.name AS name, attributes.version AS version "
        "FROM dependency ORDER BY name",
    )


@app.get("/api/projects/{name}/files")
def get_files(name: str) -> list[dict[str, Any]]:
    """List C# source files in the project."""
    return _q(name, "SELECT node_name, attributes.path AS path FROM code_file ORDER BY path")


@app.post("/api/projects/{name}/reanalyze")
def reanalyze(name: str) -> dict[str, Any]:
    """Trigger a fresh codebase analysis in a background thread."""
    directory = _web_config.get("directory")
    if not directory:
        raise HTTPException(
            status_code=400,
            detail=(
                "Server not started with --directory; reanalyze is unavailable. "
                "Use the MCP reanalyze() tool or restart with --directory."
            ),
        )
    if not os.path.isdir(directory):
        raise HTTPException(status_code=400, detail=f"Directory does not exist: {directory}")
    if _scan_status["scanning"]:
        raise HTTPException(status_code=409, detail="A scan is already in progress.")

    def _run() -> None:
        import datetime
        _scan_status["scanning"] = True
        _scan_status["error"] = None
        try:
            from mcp_server import _run_analysis  # lazy import — avoids circular deps
            _run_analysis(directory, name)
            _scan_status["last_completed"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        except Exception as exc:
            _scan_status["error"] = str(exc)
        finally:
            _scan_status["scanning"] = False

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return {"status": "started"}


@app.get("/api/projects/{name}/scan-status")
def scan_status(name: str) -> dict[str, Any]:  # noqa: ARG001
    """Return the current state of an async full-scan."""
    return dict(_scan_status)


# ── Static UI files ───────────────────────────────────────────────────────────

_UI_DIST = Path(__file__).parent / "ui" / "dist"

if _UI_DIST.exists():
    app.mount("/", StaticFiles(directory=str(_UI_DIST), html=True), name="ui")


# ── Server launch helpers ─────────────────────────────────────────────────────


def start_server(port: int = 8080) -> None:
    """Start the uvicorn server (blocking). Safe to call from a thread."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")


def start_server_thread(port: int = 8080) -> threading.Thread:
    """Start the web server in a background daemon thread."""
    t = threading.Thread(target=start_server, args=(port,), daemon=True)
    t.start()
    return t


# ── Entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    """Entry point for the ``cntxtcs-ui`` script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="CntxtCS web UI server — serves the React dashboard and REST API",
    )
    parser.add_argument(
        "--port", type=int, default=8080, metavar="PORT",
        help="Port to listen on (default: 8080)",
    )
    parser.add_argument(
        "--directory", "-d", metavar="PATH",
        help="C# project directory. Enables the POST /reanalyze endpoint.",
    )
    args = parser.parse_args()

    _web_config["directory"] = args.directory

    print(f"[cntxtcs-ui] Starting on http://localhost:{args.port}", flush=True)
    start_server(port=args.port)


if __name__ == "__main__":
    main()
