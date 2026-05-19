# Plan: Add SurrealDB Storage and MCP Server to CntxtCS

CntxtCS currently analyzes C# codebases and saves a knowledge graph as a flat JSON file. We will add a SurrealDB persistence layer so the graph is stored as queryable records and relations, then expose an MCP server that agents can use to query code structure — scoped per project, so multiple codebases can coexist.

The project will be converted to a proper UV-managed project (`pyproject.toml`) to handle Python and dependencies without requiring a system Python install.

## Phases

1. **Phase 1: UV Project Setup & Configuration**
2. **Phase 2: SurrealDB Storage Layer**
3. **Phase 3: Integrate Storage into CntxtCS.py**
4. **Phase 4: MCP Server**
5. **Phase 5: Documentation**

## Decisions

- SurrealDB connection: WebSocket to running server (`ws://localhost:8000`)
- Trigger: Explicit `--surreal` flag + `--project <name>` argument
- No raw query passthrough tool — named tools only
- Re-run behaviour: Upsert/Merge (no duplicates)
- Scoping: SurrealDB namespace = `cntxt`, database = project name
