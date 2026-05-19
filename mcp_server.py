"""MCP server exposing CntxtCS C# knowledge graph tools for AI agents."""

import os
from typing import Any
from mcp.server.fastmcp import FastMCP
from surreal_storage import SurrealStorage

mcp = FastMCP(
    "cntxtcs",
    instructions=(
        "This server provides tools to explore a C# codebase knowledge graph. "
        "Call list_projects() first to discover available projects, then pass the "
        "project name to other tools."
    ),
)


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


def main():
    """Entry point for the cntxtcs-mcp script."""
    mcp.run()


if __name__ == "__main__":
    main()
