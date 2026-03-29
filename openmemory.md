## Components

- **MainView step-1 layout**: `.log-content` is a **direct** child of `.panel-wrapper.right` (sibling of `.right-panel-step1`, index 1). It wraps the dashboard header and a `.log-scroll` region for lines; it is not inside `Step1GraphBuild`'s `.workbench-panel`.

- **Graph backends (PR #374)**: `GRAPH_BACKEND` in `.env` selects `zep_cloud` (Zep Cloud + `ZEP_API_KEY`) or `graphiti_local` (Neo4j + Graphiti via `graphiti-core`). `create_graph_provider()` in `backend/app/services/graph_provider/factory.py` returns `ZepCloudGraphProvider` or `GraphitiLocalGraphProvider`. `GraphBuilderService`, `ZepEntityReader`, `OasisProfileGenerator`, and `zep_tools` use the provider abstraction. `Config.validate_graph_backend()` returns a list of config errors (empty if valid).

- **API i18n**: `backend/app/utils/messages.py` keys include `graph_backend_not_configured` for misconfigured graph env. Simulation `/prepare` captures `get_request_language()` before the worker thread and passes `language` into `SimulationManager.prepare_simulation` → `OasisProfileGenerator` / `SimulationConfigGenerator`.
