# Zep Cloud to Local Migration Plan

Date: 2026-03-28

Status: Planning document only. No runtime changes are included in this document.

## Executive summary

MiroFish is not using Zep Cloud in just one place. It depends on Zep Cloud for:

- Graph creation and deletion
- Ontology registration
- Text ingestion and episode processing
- Full graph reads for visualization and simulation prep
- Semantic and hybrid search for the report agent
- Live simulation memory updates back into the graph

Because of that, migrating from Zep Cloud to a local setup is not a simple API-key swap.

As of 2026-03-28, Zep’s current docs say that Zep Community Edition is deprecated and no longer supported, and point self-hosted users to Graphiti or BYOC instead. That means the safest “Zep local” target for this repo is:

- `graphiti-core` running inside the backend
- A local Neo4j instance for graph storage
- A provider abstraction layer so MiroFish can run `zep_cloud` and `graphiti_local` side by side during rollout

This plan assumes that target.

## Official references

- Zep FAQ: https://help.getzep.com/faq
- Zep open-source direction announcement, published April 2, 2025: https://blog.getzep.com/announcing-a-new-direction-for-zeps-open-source-strategy/
- Graphiti quick start: https://help.getzep.com/graphiti/getting-started/quick-start
- Graphiti Neo4j configuration: https://help.getzep.com/graphiti/configuration/neo-4-j-configuration
- Graphiti custom entity and edge types: https://help.getzep.com/graphiti/core-concepts/custom-entity-and-edge-types
- Graphiti graph namespacing: https://help.getzep.com/graphiti/core-concepts/graph-namespacing
- Graphiti search: https://help.getzep.com/graphiti/working-with-data/searching
- Graphiti CRUD operations: https://help.getzep.com/graphiti/working-with-data/crud-operations
- Graphiti fact triples: https://help.getzep.com/graphiti/working-with-data/adding-fact-triples

## Current MiroFish dependency map

These files are the main Zep Cloud touch points in the repo today:

- `backend/app/config.py`
  - Requires `ZEP_API_KEY`
- `backend/requirements.txt`
  - Pins `zep-cloud==3.13.0`
- `backend/pyproject.toml`
  - Pins `zep-cloud==3.13.0`
- `backend/app/services/graph_builder.py`
  - Creates graphs, sets ontology, ingests batches, waits for episode processing, reads graph data, deletes graphs
- `backend/app/services/zep_entity_reader.py`
  - Reads all nodes and edges, enriches entities with edge context
- `backend/app/services/zep_tools.py`
  - Runs graph search and powers report-agent retrieval
- `backend/app/services/zep_graph_memory_updater.py`
  - Pushes live simulation activity back into the graph
- `backend/app/services/oasis_profile_generator.py`
  - Uses graph search to enrich agent profiles
- `backend/app/utils/zep_paging.py`
  - Implements graph-wide pagination on Zep node and edge list APIs
- `backend/app/api/graph.py`
  - Exposes graph build, read, and delete flows
- `backend/app/api/simulation.py`
  - Exposes graph entity read flows used by simulation setup
- `backend/app/api/report.py`
  - Exposes report search/statistics endpoints
- `.env.example`, `README.md`, `README-EN.md`
  - Document Zep Cloud setup
- `docker-compose.yml`
  - Does not currently start any local graph database

## What must keep working after migration

The migration is successful only if these user-visible flows still work:

- Build a graph from uploaded source material
- Store and reuse a project-level `graph_id`
- Load graph nodes and edges in the UI
- Read entities from the graph to prepare simulation agents
- Search the graph for report generation
- Keep live simulation memory updates enabled
- Delete graph data when a project is removed or rebuilt

## Recommended target architecture

### 1. Keep the existing product-level `graph_id`

Do not change the frontend contract if we can avoid it.

- Keep storing `graph_id` in project and simulation JSON
- In the new local provider, keep `graph_id` as the app-level identifier
- Reuse `graph_id` as the primary Graphiti `group_id`
- This preserves almost all frontend behavior and avoids a database migration in the UI layer

Reason:

- Graphiti uses `group_id` for isolated graph namespaces
- In the currently targeted `graphiti-core` release, MiroFish can stay on a single Neo4j database and isolate graphs by `group_id`
- MiroFish already thinks in terms of one graph per project
- `graph_id -> group_id` is the cleanest compatibility bridge for this repo

### 2. Add a graph provider abstraction in the backend

Create a small internal interface, for example:

- `create_graph(name) -> graph_id`
- `delete_graph(graph_id)`
- `set_ontology(graph_id, ontology)`
- `add_text_batch(graph_id, chunks)`
- `wait_for_ingestion(graph_id, job_ref)`
- `get_all_nodes(graph_id)`
- `get_all_edges(graph_id)`
- `get_node(graph_id, node_uuid)`
- `get_node_edges(graph_id, node_uuid)`
- `search_graph(graph_id, query, scope, limit)`
- `append_activity(graph_id, text)`
- `get_graph_statistics(graph_id)`

Implement two providers:

- `ZepCloudGraphProvider`
- `GraphitiLocalGraphProvider`

Add a factory selected by an env var such as:

- `GRAPH_BACKEND=zep_cloud`
- `GRAPH_BACKEND=graphiti_local`

### 3. Embed Graphiti in the backend first

For the first migration, do not introduce a second application service unless it becomes necessary.

Recommended first version:

- Flask backend remains the API server
- Graphiti runs as a Python library inside the backend process
- Neo4j runs as a local service in Docker Compose

Why this is the safest first move:

- Fewer moving parts
- Easier local debugging
- Lower operational complexity
- Faster path to dual-run and rollback

### 4. Treat async Graphiti calls as a real design task

This is an important implementation detail.

Current MiroFish backend code is mostly synchronous Flask code. Graphiti’s documented API is async-first. That means we need one of these approaches:

- Wrap Graphiti calls in a sync adapter using a controlled event-loop helper
- Move graph operations into a worker or async service

Recommendation:

- Phase 1 and Phase 2 should use a thin sync adapter around Graphiti
- Only move to a separate async service if latency or concurrency becomes a real problem

## API and data-model mapping

### Current Zep Cloud behavior to replace

| Current behavior | Current MiroFish usage | Local replacement strategy |
| --- | --- | --- |
| `graph.create` | Creates one graph per project | No separate graph object in Graphiti; create and reserve a `group_id` namespace |
| `graph.set_ontology` | Registers project ontology before ingestion | Pass custom entity types, edge types, and edge maps during episode ingestion |
| `graph.add_batch` | Sends document chunks for extraction | Loop over `graphiti.add_episode(...)` or bulk helper if adopted |
| `episode.get(...processed)` | Polls until ingestion finishes | Track ingestion at app level; treat Graphiti call completion as local completion, or store background job state |
| `graph.node.get_by_graph_id` | Reads all nodes | Query by `group_id`, using Graphiti CRUD utilities or direct Neo4j Cypher |
| `graph.edge.get_by_graph_id` | Reads all edges | Query by `group_id`, using Graphiti CRUD utilities or direct Neo4j Cypher |
| `graph.search(scope="edges" / "nodes")` | Report and simulation retrieval | Use `graphiti.search()` or `graphiti._search()` recipes for edge-only and node-only search |
| `graph.add(type="text", data=...)` | Live simulation memory writeback | Convert activity batches into Graphiti text episodes |
| `graph.delete` | Removes a graph | Delete all nodes, edges, and episodes for the namespace |

### Ontology compatibility notes

Graphiti supports custom entity and edge types using Pydantic models, which matches MiroFish’s current ontology-generation approach well. It also has similar protected attribute names, including:

- `uuid`
- `name`
- `group_id`
- `labels`
- `created_at`
- `summary`
- `attributes`
- `name_embedding`

This is good news for MiroFish because `backend/app/services/graph_builder.py` already normalizes ontology names and protected attributes for Zep-style constraints. That logic should be reused, not rewritten from scratch.

### Search compatibility notes

Graphiti supports:

- Hybrid search
- Node distance reranking
- Configurable `_search()` recipes for node-only and edge-only search

The main migration work is not “can Graphiti search,” but:

- matching the result shape expected by `zep_tools.py`
- preserving edge facts, node summaries, and score ordering closely enough for report quality

### Full graph reads

The current UI and simulation setup rely on full-graph reads, not just search.

That means the local provider must expose:

- list all nodes for a namespace
- list all edges for a namespace
- get one node by UUID
- get related edges for a node

Recommendation:

- Use direct Neo4j reads by `group_id` for graph-wide list endpoints
- Keep Graphiti itself focused on ingestion and search

This is simpler than trying to force every UI read through search APIs.

## Migration phases

## Phase 0: Lock the target and scope

Goal:

- Avoid starting implementation against the wrong “local Zep” target

Tasks:

- Confirm the target is `Graphiti + Neo4j`, not deprecated Zep Community Edition
- Decide whether the migration must cover:
  - existing historical graphs
  - only newly created graphs
  - both
- Decide whether local graph storage is the only goal, or whether local LLM/embedding providers are also required
- Define feature parity as:
  - required for launch
  - acceptable with minor quality drift
  - allowed to defer

Exit criteria:

- One agreed target architecture
- One agreed feature-parity list
- One agreed data-migration scope

## Phase 1: Prepare infrastructure

Goal:

- Make the repo able to run a local graph backend

Tasks:

- Add Neo4j service to `docker-compose.yml`
- Add persistent Neo4j volume
- Add backend env vars:
  - `GRAPH_BACKEND`
  - `NEO4J_URI`
  - `NEO4J_USER`
  - `NEO4J_PASSWORD`
  - optional `GRAPHITI_TELEMETRY_ENABLED=false`
  - optional `SEMAPHORE_LIMIT`
- Add Graphiti-compatible runtime deps to `backend/requirements.txt` and `backend/pyproject.toml`
- Install `graphiti-core` separately with `uv pip install --no-deps ...` to avoid the `neo4j` version conflict with `camel-oasis`
- Keep `zep-cloud` installed during dual-run
- Add backend startup initialization:
  - connect to Graphiti
  - call `build_indices_and_constraints()` once
- Update `.env.example`, `README.md`, and `README-EN.md`

Recommended first Docker addition:

- Neo4j 5.26+ image
- For this repo, keeping the enterprise variant in `docker-compose.yml` is the safer default if you may reuse volumes that were created with Neo4j block format
- Ports `7474` and `7687`
- Persistent `/data` and `/logs` volumes
- One shared Neo4j database with Graphiti `group_id` isolation per MiroFish graph

Exit criteria:

- Local `docker compose up` starts Neo4j and MiroFish
- Backend can connect to Neo4j
- Graphiti indices are created successfully

## Phase 2: Add the provider abstraction without changing behavior

Goal:

- Isolate Zep-specific code before swapping implementations

Tasks:

- Create `graph_provider` interface and factory
- Move Zep client construction behind the provider
- Keep existing Zep behavior as the default implementation
- Refactor these services to depend on the provider instead of importing `zep_cloud` directly:
  - `graph_builder.py`
  - `zep_entity_reader.py`
  - `zep_tools.py`
  - `zep_graph_memory_updater.py`
  - `oasis_profile_generator.py`
- Refactor `zep_paging.py` into provider-neutral graph read helpers or retire it in favor of provider methods

Important rule:

- Do not change API response shapes in this phase

Exit criteria:

- App still works exactly as before with `GRAPH_BACKEND=zep_cloud`
- Zep-specific imports are limited to the Zep provider module

## Phase 3: Implement the local Graphiti provider

Goal:

- Support the same MiroFish workflows on a local graph backend

Tasks:

- Map `graph_id` to Graphiti `group_id`
- Implement `create_graph` as namespace bootstrap
- Reuse ontology normalization logic from current graph builder
- Convert MiroFish ontology into:
  - Graphiti custom entity types
  - Graphiti custom edge types
  - Graphiti edge type map
- Implement chunk ingestion with `add_episode`
- Implement live simulation memory writes with `add_episode`
- Implement search using:
  - edge-focused `_search()` recipe for fact retrieval
  - node-focused `_search()` recipe for entity retrieval
- Implement graph-wide reads by `group_id`
- Implement delete-by-namespace logic

Important local-behavior differences to handle:

- Graphiti is namespace-based, not graph-object-based
- Ingestion lifecycle is different from Zep Cloud polling
- Search result objects will not be identical to Zep Cloud result objects

Exit criteria:

- A new graph can be built locally
- The UI can render graph nodes and edges
- Simulation prep can read filtered entities
- Report agent search returns usable facts

## Phase 4: Data migration and backfill

Goal:

- Move old project graphs, not just new ones

Recommended order of preference:

### Option A: Re-ingest from original source documents

This is the best option when the original uploaded material still exists.

Why it is preferred:

- It preserves the intended extraction pipeline
- It preserves ontology-guided classification
- It avoids lossy conversion from already-extracted node and edge summaries back into raw text

Use this when:

- the original uploaded text or PDF is still available
- the project ontology is still stored

### Option B: Rebuild from exported facts and nodes

Use this only for projects where the original source text is missing.

Approach:

- Export Zep Cloud nodes and edges with existing MiroFish read code
- Convert important edges into fact triples or synthetic episodes
- Rebuild the namespace in Graphiti

Tradeoff:

- Faster for stranded data
- Lower fidelity than re-ingesting original source material

### Required migration script

Create a script such as:

- `backend/scripts/migrate_zep_cloud_to_graphiti.py`

Suggested responsibilities:

- list existing projects with `graph_id`
- detect whether original source text is available
- choose migration mode per project
- create local namespace
- ingest data
- validate node and edge counts
- write migration report JSON

Suggested validation fields per project:

- old graph id
- new group id
- migration mode used
- old node count
- new node count
- old edge count
- new edge count
- top 10 search comparison queries
- status
- error details if failed

Exit criteria:

- A representative sample of old projects has been migrated and validated

## Phase 5: Dual-run and comparison

Goal:

- Prove that local results are good enough before cutover

Tasks:

- Add a temporary comparison mode
- For selected projects:
  - build or migrate graph in both backends
  - run the same search queries against both
  - compare:
    - returned facts
    - node summaries
    - graph statistics
    - report quality
- Log mismatches for manual review

Recommended comparison set:

- graph build from a medium-size document
- entity list for simulation setup
- 10 report-agent queries from real historical runs
- live memory update during a short simulation

Exit criteria:

- No blocker regressions in core flows
- Search quality is acceptable for report generation

## Phase 6: Cutover

Goal:

- Move production behavior to the local backend with low risk

Tasks:

- Keep both backends available behind `GRAPH_BACKEND`
- Start with local backend in dev only
- Then test on a small set of staging projects
- Then switch default backend for new graphs only
- After confidence is high, migrate old projects and switch all reads to local

Safe cutover order:

1. New graph builds go to local
2. New simulation live updates go to local
3. Report/search reads go to local
4. Historical projects are backfilled
5. Zep Cloud becomes fallback only

Rollback:

- Flip `GRAPH_BACKEND` back to `zep_cloud`
- Leave dual-write or dual-read disabled unless specifically needed

## Phase 7: Cleanup

Goal:

- Remove cloud-only assumptions after the local backend is stable

Tasks:

- Remove `ZEP_API_KEY` from required config if no longer needed
- Remove `zep-cloud` dependency
- Remove Zep-specific code paths and helpers
- Rename files and classes so they are provider-neutral
  - example: `zep_tools.py` -> `graph_tools.py`
  - example: `ZepEntityReader` -> `GraphEntityReader`
- Update docs to describe local-first setup

Exit criteria:

- No runtime path depends on Zep Cloud
- Local setup is the documented default

## File-level implementation plan

### Config and infra

- `backend/app/config.py`
  - add `GRAPH_BACKEND`
  - add `NEO4J_URI`
  - add `NEO4J_USER`
  - add `NEO4J_PASSWORD`
  - stop hard-failing on missing `ZEP_API_KEY` when local backend is selected
- `.env.example`
  - document both cloud and local modes
- `docker-compose.yml`
  - add Neo4j service and volume
- `backend/requirements.txt`
  - add Graphiti dependency
- `backend/pyproject.toml`
  - add Graphiti dependency

### New provider layer

Recommended new files:

- `backend/app/services/graph_provider/base.py`
- `backend/app/services/graph_provider/factory.py`
- `backend/app/services/graph_provider/zep_cloud_provider.py`
- `backend/app/services/graph_provider/graphiti_local_provider.py`
- `backend/app/services/graph_provider/models.py`

### Existing service refactors

- `backend/app/services/graph_builder.py`
  - use provider for graph lifecycle and ingestion
- `backend/app/services/zep_entity_reader.py`
  - make provider-neutral
- `backend/app/services/zep_tools.py`
  - make provider-neutral
- `backend/app/services/zep_graph_memory_updater.py`
  - write activities through provider
- `backend/app/services/oasis_profile_generator.py`
  - search via provider
- `backend/app/api/graph.py`
  - leave API shape stable
- `backend/app/api/simulation.py`
  - leave API shape stable
- `backend/app/api/report.py`
  - leave API shape stable

### Frontend impact

Frontend changes should be minimal if backend response shapes stay stable.

Likely no required frontend changes beyond wording updates in docs or setup screens.

## Testing plan

### Unit tests

- provider factory selection
- ontology normalization compatibility
- graph-id to group-id mapping
- node and edge shape normalization
- search result shape normalization

### Integration tests

- create graph locally
- ingest text chunks
- read all nodes and edges
- retrieve filtered entities
- run report search
- push live simulation activity and confirm graph updates
- delete namespace and confirm cleanup

### Regression tests

Use at least one real project fixture and compare:

- node count difference stays within an agreed threshold
- edge count difference stays within an agreed threshold
- top search results are semantically comparable
- report output remains acceptable to a human reviewer

## Risks and mitigation

### Risk 1: Search quality differs from Zep Cloud

Mitigation:

- dual-run search comparisons
- tune Graphiti search recipes
- add fallback local keyword search only as backup, not primary behavior

### Risk 2: Full graph reads are harder than search

Mitigation:

- use direct Neo4j namespace queries for UI graph rendering and entity listing

### Risk 3: Async Graphiti calls complicate Flask integration

Mitigation:

- start with a sync adapter
- isolate async logic inside the provider

### Risk 4: Old graphs cannot be migrated losslessly from summaries alone

Mitigation:

- prefer original source-document re-ingestion
- use fact-triple fallback only where necessary

### Risk 5: Config sprawl during rollout

Mitigation:

- one `GRAPH_BACKEND` switch
- one local env block
- keep cloud env vars optional once local mode is supported

## Acceptance criteria

The migration can be called complete when all of the following are true:

- MiroFish can build a project graph locally without Zep Cloud
- The graph viewer loads local nodes and edges correctly
- Simulation setup reads local graph entities correctly
- Report generation can retrieve relevant facts from the local graph
- Live simulation memory updates work against the local graph
- Existing important projects are migrated or rebuildable
- Zep Cloud is no longer required for normal operation

## Recommended execution order

If this work is implemented as an engineering project, the lowest-risk order is:

1. Add infra and config
2. Add provider abstraction
3. Keep Zep Cloud as the default provider
4. Implement local Graphiti provider
5. Validate new graph creation locally
6. Validate report search locally
7. Validate simulation entity loading and live updates locally
8. Add migration/backfill script
9. Dual-run and compare
10. Cut over new graphs
11. Migrate old graphs
12. Remove Zep Cloud dependency

## Bottom line

This migration is very feasible, but it should be treated as a backend provider replacement project, not a config tweak.

The key decisions that make it safe are:

- use Graphiti plus local Neo4j as the supported local target
- keep `graph_id` as the app-level identifier and reuse it as Graphiti `group_id`
- add a provider abstraction before changing behavior
- prefer re-ingesting original source documents for old projects
- dual-run before cutover
