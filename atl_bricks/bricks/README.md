# Concept Brick Families

Each folder here is a portable concept family, not an app-specific module bucket.

Current families:
- `runtime.core`
- `storage.sqlite`
- `registry.settings`
- `config.assembly`
- `fetch.http_sync`
- `fetch.freqtrade_api`
- `analytics.trades`
- `analytics.rankings`
- `math.stats`
- `math.signals`
- `workflow.timeline`
- `runtime.sessions`
- `assembly.genome`
- `orchestration.lobby`
- `universe.market`
- `backtest.calibration`
- `research.ml_registry`
- `ui.routes`
- `ui.shell`

Extraction rule:
- pull one concept at a time out of `source_snapshot/main.py`
- name the result for the concept, not the source app
- make the hand-in and hand-off explicit
- keep the copied source as the audit trail until the concept graph is stable
