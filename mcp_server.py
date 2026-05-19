"""MCP server exposing CntxtCS C# knowledge graph tools for AI agents."""

import os
import sys
import threading
from typing import Any
from mcp.server.fastmcp import FastMCP
from surreal_storage import SurrealStorage

# ── Serve-mode state ───────────────────────────────────────────────────────────
# Set at startup when --directory / --project are passed to main().
_serve_config: dict[str, str | None] = {
    "directory": None,
    "project": None,
}

mcp = FastMCP(
    "cntxtcs",
    instructions=(
        "This server provides tools to explore C# codebase knowledge graphs stored in SurrealDB. "
        "Call list_projects() first to see available projects, then use the project name in other tools. "
        "Call reanalyze() to refresh data after the codebase changes. "
        "The server can be started with --directory and --project to auto-analyse at startup, "
        "and --watch to auto-refresh whenever .cs files change."
    ),
)


# ── Analysis helper ────────────────────────────────────────────────────────────

def _run_analysis(directory: str, project: str) -> dict[str, Any]:
    """Run codebase analysis and upsert the result into SurrealDB.
    
    Returns a stats dict with totals for files, classes, methods, etc.
    """
    from CntxtCS import CSCodeKnowledgeGraph  # imported here to avoid circular deps

    print(f"[cntxtcs] Analysing '{directory}' → project '{project}'...", file=sys.stderr, flush=True)
    ckg = CSCodeKnowledgeGraph(directory=directory)
    ckg.analyze_codebase()

    stats = {
        "total_files": ckg.total_files,
        "total_namespaces": ckg.total_namespaces,
        "total_classes": ckg.total_classes,
        "total_methods": ckg.total_methods,
        "total_interfaces": ckg.total_interfaces,
        "total_enums": ckg.total_enums,
        "total_structs": ckg.total_structs,
        "total_dependencies": len(ckg.total_dependencies),
        "total_usings": ckg.total_usings,
    }
    with SurrealStorage(project) as storage:
        storage.store_graph(ckg.graph, stats)

    print(
        f"[cntxtcs] Analysis complete: {stats['total_classes']} classes, "
        f"{stats['total_methods']} methods",
        file=sys.stderr,
        flush=True,
    )
    return stats


def _run_analysis_incremental(
    directory: str,
    project: str,
    changed_paths: list[str],
    deleted_paths: list[str],
) -> None:
    """Delete stale data for affected files then re-index only the changed ones.

    Stats are not updated here; they remain from the last full analysis.
    """
    relative_all = [
        os.path.relpath(p, directory)
        for p in changed_paths + deleted_paths
    ]

    with SurrealStorage(project) as storage:
        if relative_all:
            storage.delete_file_data(relative_all)

    if not changed_paths:
        print(
            f"[cntxtcs] Incremental: removed {len(deleted_paths)} file(s) from index.",
            file=sys.stderr, flush=True,
        )
        return

    from CntxtCS import CSCodeKnowledgeGraph
    ckg = CSCodeKnowledgeGraph(directory=directory)
    ckg.analyze_files(changed_paths)

    with SurrealStorage(project) as storage:
        storage.store_graph(ckg.graph, {}, update_stats=False)

    print(
        f"[cntxtcs] Incremental: re-indexed {len(changed_paths)} file(s), "
        f"removed {len(deleted_paths)} file(s).",
        file=sys.stderr, flush=True,
    )


# ── File watcher ───────────────────────────────────────────────────────────────

_WATCHED_EXTENSIONS = {".cs", ".csproj"}
_DEBOUNCE_SECONDS = 3.0


def _start_watcher(directory: str, project: str) -> None:
    """Start a background daemon thread that watches *directory* for .cs/.csproj
    changes and triggers a debounced re-analysis.
    
    Requires the ``watchdog`` package (included in project dependencies).
    """
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print(
            "[cntxtcs] watchdog not installed — file watching disabled. "
            "Run: uv sync",
            file=sys.stderr,
        )
        return

    _timer_ref: list[threading.Timer | None] = [None]
    _lock = threading.Lock()
    _changed: set[str] = set()
    _deleted: set[str] = set()

    def _debounced_trigger() -> None:
        with _lock:
            changed = list(_changed)
            deleted = list(_deleted)
            _changed.clear()
            _deleted.clear()
        try:
            _run_analysis_incremental(directory, project, changed, deleted)
        except Exception as exc:
            print(f"[cntxtcs] Auto re-analysis error: {exc}", file=sys.stderr, flush=True)

    class _CSharpHandler(FileSystemEventHandler):
        def on_any_event(self, event) -> None:  # type: ignore[override]
            if event.is_directory:
                return
            src = getattr(event, "src_path", "")
            if not any(src.endswith(ext) for ext in _WATCHED_EXTENSIONS):
                return
            with _lock:
                if event.event_type == "deleted":
                    _deleted.add(src)
                    _changed.discard(src)
                else:
                    _changed.add(src)
                    _deleted.discard(src)
                if _timer_ref[0] is not None:
                    _timer_ref[0].cancel()
                t = threading.Timer(_DEBOUNCE_SECONDS, _debounced_trigger)
                t.daemon = True
                _timer_ref[0] = t
                t.start()

    observer = Observer()
    observer.schedule(_CSharpHandler(), directory, recursive=True)
    observer.daemon = True  # type: ignore[assignment]
    observer.start()
    print(f"[cntxtcs] Watching '{directory}' for changes (debounce {_DEBOUNCE_SECONDS}s)...", file=sys.stderr, flush=True)


def _q(project: str, surql: str, params: dict | None = None) -> list:
    """Run a SurrealQL query and unwrap the first statement result."""
    with SurrealStorage(project) as s:
        result = s.query(surql, params or {})
    if result and isinstance(result[0], list):
        return result[0]
    return result if isinstance(result, list) else []


@mcp.tool()
def list_projects() -> list[str]:
    """List all analysed C# projects available in SurrealDB. Call this first."""
    return SurrealStorage.list_projects()


@mcp.tool()
def get_codebase_stats(project: str) -> dict[str, Any]:
    """Return statistics about the C# codebase (file count, class count, etc).
    
    Args:
        project: Project name from list_projects().
    """
    rows = _q(project, "SELECT * FROM codebase_stats LIMIT 1")
    if rows:
        row = rows[0] if isinstance(rows, list) else rows
        return row.get("stats", {})
    return {}


@mcp.tool()
def get_file_structure(project: str) -> list[dict[str, Any]]:
    """Return the list of C# source files in the project.
    
    Args:
        project: Project name from list_projects().
    """
    return _q(project, "SELECT node_name, attributes.path AS path FROM code_file ORDER BY path")


@mcp.tool()
def list_namespaces(project: str) -> list[str]:
    """List all namespaces in the project.
    
    Args:
        project: Project name from list_projects().
    """
    rows = _q(project, "SELECT attributes.name AS name FROM namespace ORDER BY name")
    return sorted(set(r.get("name", "") for r in rows if r.get("name")))


@mcp.tool()
def list_classes(
    project: str,
    access_modifier: str | None = None,
) -> list[dict[str, Any]]:
    """List all classes in the project.
    
    Args:
        project: Project name from list_projects().
        access_modifier: Optional filter, e.g. 'public' or 'internal'.
    
    Returns list of {name, access_modifier, modifiers, inherits}.
    """
    surql = "SELECT attributes.name AS name, attributes.access_modifier AS access_modifier, attributes.modifiers AS modifiers, attributes.inherits AS inherits FROM class_node"
    params: dict = {}
    if access_modifier:
        surql += " WHERE attributes.access_modifier = $am"
        params["am"] = access_modifier
    surql += " ORDER BY name"
    return _q(project, surql, params)


@mcp.tool()
def get_class_details(project: str, class_name: str) -> dict[str, Any]:
    """Get full details of a class: methods, properties, fields, events, inheritance.
    
    Args:
        project: Project name from list_projects().
        class_name: Class name, e.g. 'UserService'.
    """
    # Fetch class record
    rows = _q(project, "SELECT * FROM class_node WHERE attributes.name = $n LIMIT 1", {"n": class_name})
    if not rows:
        return {}
    cls = rows[0] if isinstance(rows, list) else rows
    cls_id = str(cls.get("id"))

    # Fetch related members - simplified queries without relation traversal
    # Since mem:// may not support advanced graph traversal, use simpler approach
    all_methods = _q(project, "SELECT * FROM method_node")
    all_properties = _q(project, "SELECT * FROM property_node")
    all_fields = _q(project, "SELECT * FROM field_node")
    all_events = _q(project, "SELECT * FROM event_node")
    
    # Filter by class name in node_name
    methods = [
        {"name": m.get("attributes", {}).get("name"),
         "return_type": m.get("attributes", {}).get("return_type"),
         "access_modifier": m.get("attributes", {}).get("access_modifier"),
         "parameters": m.get("attributes", {}).get("parameters")}
        for m in all_methods if class_name in m.get("node_name", "")
    ]
    properties = [
        {"name": p.get("attributes", {}).get("name"),
         "property_type": p.get("attributes", {}).get("property_type")}
        for p in all_properties if class_name in p.get("node_name", "")
    ]
    fields = [
        {"name": f.get("attributes", {}).get("name"),
         "field_type": f.get("attributes", {}).get("field_type")}
        for f in all_fields if class_name in f.get("node_name", "")
    ]
    events = [
        {"name": e.get("attributes", {}).get("name"),
         "event_type": e.get("attributes", {}).get("event_type")}
        for e in all_events if class_name in e.get("node_name", "")
    ]

    return {
        "name": cls.get("attributes", {}).get("name", class_name),
        "access_modifier": cls.get("attributes", {}).get("access_modifier"),
        "modifiers": cls.get("attributes", {}).get("modifiers"),
        "inherits": cls.get("attributes", {}).get("inherits"),
        "methods": methods,
        "properties": properties,
        "fields": fields,
        "events": events,
    }


@mcp.tool()
def get_class_hierarchy(project: str, class_name: str) -> dict[str, list[str]]:
    """Return the inheritance hierarchy for a class.
    
    Args:
        project: Project name from list_projects().
        class_name: Class name, e.g. 'UserService'.
    
    Returns {parents: [...], children: [...]}.
    """
    # Find the class's inherits field (stored as string)
    rows = _q(project, "SELECT attributes.inherits AS inherits FROM class_node WHERE attributes.name = $n LIMIT 1", {"n": class_name})
    parents: list[str] = []
    if rows:
        row = rows[0] if isinstance(rows, list) else rows
        inherits_str = row.get("inherits") or ""
        if inherits_str:
            parents = [p.strip() for p in inherits_str.split(",") if p.strip()]

    # Find children (classes that inherit this one)
    children_rows = _q(project, "SELECT attributes.name AS name FROM class_node WHERE attributes.inherits CONTAINS $n", {"n": class_name})
    children = [r.get("name", "") for r in children_rows if r.get("name")]

    return {"parents": parents, "children": children}


@mcp.tool()
def list_interfaces(project: str) -> list[dict[str, Any]]:
    """List all interfaces in the project.
    
    Args:
        project: Project name from list_projects().
    
    Returns list of {name, access_modifier, inherits}.
    """
    return _q(project, "SELECT attributes.name AS name, attributes.access_modifier AS access_modifier, attributes.inherits AS inherits FROM interface_node ORDER BY name")


@mcp.tool()
def find_implementations(project: str, interface_name: str) -> list[str]:
    """Find all classes that implement (inherit from) an interface.
    
    Args:
        project: Project name from list_projects().
        interface_name: Interface name, e.g. 'IUserService'.
    
    Returns list of implementing class names.
    """
    rows = _q(
        project,
        "SELECT attributes.name AS name FROM class_node WHERE attributes.inherits CONTAINS $iface",
        {"iface": interface_name},
    )
    return [r.get("name", "") for r in rows if r.get("name")]


@mcp.tool()
def list_methods(
    project: str,
    name_filter: str | None = None,
    return_type: str | None = None,
) -> list[dict[str, Any]]:
    """List and search methods across the project.
    
    Args:
        project: Project name from list_projects().
        name_filter: Optional substring to match against method names.
        return_type: Optional exact return type to filter by (e.g. 'void', 'Task').
    
    Returns list of {node_name, name, return_type, access_modifier, parameters}.
    """
    surql = "SELECT node_name, attributes.name AS name, attributes.return_type AS return_type, attributes.access_modifier AS access_modifier, attributes.parameters AS parameters FROM method_node"
    params: dict = {}
    if return_type:
        surql += " WHERE attributes.return_type = $rt"
        params["rt"] = return_type
    surql += " ORDER BY name"
    rows = _q(project, surql, params)
    if name_filter:
        rows = [r for r in rows if name_filter.lower() in (r.get("name") or "").lower()]
    return rows


@mcp.tool()
def list_dependencies(project: str) -> list[dict[str, Any]]:
    """List all NuGet package dependencies.
    
    Args:
        project: Project name from list_projects().
    
    Returns list of {name, version}.
    """
    return _q(project, "SELECT attributes.name AS name, attributes.version AS version FROM dependency ORDER BY name")


@mcp.tool()
def search_code_elements(
    project: str,
    query: str,
    type_filter: str | None = None,
) -> list[dict[str, Any]]:
    """Search for code elements by name substring.
    
    Args:
        project: Project name from list_projects().
        query: Case-insensitive substring to find in element names.
        type_filter: Optional type restriction — one of: file, namespace, class,
                     interface, struct, enum, method, property, field, event, dependency.
    
    Returns list of {node_name, node_type, name}.
    """
    type_to_table = {
        "file": "code_file",
        "namespace": "namespace",
        "class": "class_node",
        "interface": "interface_node",
        "struct": "struct_node",
        "enum": "enum_node",
        "method": "method_node",
        "property": "property_node",
        "field": "field_node",
        "event": "event_node",
        "dependency": "dependency",
    }
    tables = [type_to_table[type_filter]] if type_filter and type_filter in type_to_table else list(type_to_table.values())
    results = []
    q_lower = query.lower()
    for table in tables:
        # Do Python-side filtering since string::lowercase() not available in mem://
        rows = _q(project, f"SELECT node_name, node_type, attributes.name AS name FROM {table}")
        filtered = [r for r in rows if q_lower in r.get("node_name", "").lower()]
        results.extend(filtered)
    return results


# ── Reanalyze tool ────────────────────────────────────────────────────────────

@mcp.tool()
def reanalyze(
    project: str | None = None,
    directory: str | None = None,
) -> dict[str, Any]:
    """Re-analyse a C# codebase and refresh the SurrealDB knowledge graph.
    
    Use this after the codebase has changed to get up-to-date results from all
    other tools. Can also be called from CI/CD pipelines or git hooks.
    
    If the server was started with --directory and --project those values are
    used as defaults, so you can call reanalyze() with no arguments in that case.
    
    Args:
        project: Project name to update. Falls back to the server startup value.
        directory: Absolute path to the C# codebase. Falls back to server startup value.
    
    Returns a stats dict: total_files, total_classes, total_methods, etc.
    """
    _project = project or _serve_config["project"]
    _directory = directory or _serve_config["directory"]

    if not _project:
        return {"error": "project name required — pass 'project' or start the server with --project"}
    if not _directory:
        return {"error": "directory required — pass 'directory' or start the server with --directory"}
    if not os.path.isdir(_directory):
        return {"error": f"directory does not exist: {_directory}"}

    try:
        return _run_analysis(_directory, _project)
    except Exception as exc:
        return {"error": str(exc)}


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    """Entry point for the cntxtcs-mcp script.
    
    Without arguments: start the MCP server (tools query pre-existing SurrealDB data).
    With --directory + --project: analyse the codebase first, then start the server.
    With --watch: also watch for .cs file changes and auto re-analyse.
    With --skip-scan: skip the initial full analysis (use existing SurrealDB data).
    
    Examples::
    
        uv run python mcp_server.py
        uv run python mcp_server.py --directory ./MyProject --project my-api
        uv run python mcp_server.py --directory ./MyProject --project my-api --watch
        uv run python mcp_server.py --directory ./MyProject --project my-api --watch --skip-scan
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="CntxtCS MCP server — exposes C# knowledge graph tools to AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--directory", "-d",
        metavar="PATH",
        help="Path to the C# codebase. When combined with --project, analyses the codebase at startup.",
    )
    parser.add_argument(
        "--project", "-p",
        metavar="NAME",
        help="SurrealDB project name (database). Required when --directory is used.",
    )
    parser.add_argument(
        "--skip-scan",
        action="store_true",
        help=(
            "Skip the initial full analysis on startup. The server connects to existing "
            "SurrealDB data immediately. Use the Full Scan button in the UI (or the "
            "reanalyze() MCP tool) to trigger a scan manually."
        ),
    )
    parser.add_argument(
        "--watch", "-w",
        action="store_true",
        help="Watch the directory for .cs/.csproj changes and auto re-analyse. Requires --directory and --project.",
    )
    parser.add_argument(
        "--ui",
        action="store_true",
        help="Also start the web UI server (React dashboard + REST API).",
    )
    parser.add_argument(
        "--ui-port",
        type=int,
        default=8080,
        metavar="PORT",
        help="Port for the web UI server (default: 8080). Implies --ui.",
    )
    args = parser.parse_args()

    if args.directory and not args.project:
        parser.error("--project NAME is required when --directory is specified")
    if args.watch and not args.directory:
        parser.error("--watch requires --directory and --project")

    # Store for use by the reanalyze() tool at runtime
    _serve_config["directory"] = args.directory
    _serve_config["project"] = args.project

    # Run initial analysis before binding the MCP transport
    if args.directory and args.project:
        if args.skip_scan:
            print(
                f"[cntxtcs] --skip-scan: using existing data for project '{args.project}'. "
                "Use Full Scan in the UI or reanalyze() to index the codebase.",
                file=sys.stderr, flush=True,
            )
        else:
            try:
                _run_analysis(args.directory, args.project)
            except Exception as exc:
                print(f"[cntxtcs] Initial analysis failed: {exc}", file=sys.stderr, flush=True)
                sys.exit(1)

    # Start background file watcher
    if args.watch:
        _start_watcher(args.directory, args.project)  # type: ignore[arg-type]

    # Start web UI server in a background thread when requested
    if args.ui or args.ui_port != 8080:
        from web_server import start_server_thread
        from web_server import _web_config as _wc
        _wc["directory"] = args.directory
        start_server_thread(port=args.ui_port)
        print(
            f"[cntxtcs] Web UI available at http://localhost:{args.ui_port}",
            file=sys.stderr,
            flush=True,
        )

    mcp.run()


if __name__ == "__main__":
    main()
