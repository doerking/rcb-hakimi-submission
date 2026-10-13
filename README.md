# Hakimi · ResearchClawBench Submission

**Agent**: Hakimi · **Runtime**: pi + Hakimi (manual agent harness)
**Models**: `deepseek/deepseek-flash` (foreground) + `sensenova-6.8-flash-lite` (background workers)
**Judge**: `kimi-k3` (image items) + `sensenova-6.8-flash-lite` (text items)
**Submitted**: 2026-10-14

## Summary

**40 / 40 ResearchClawBench tasks completed** (one clean run each).

- Score range **2.6 – 72.2**, mean **36.4**, median **35.7**
- For reference, vs the official leaderboard this places ahead of InnoClaw (2.0) and Ligase.

### Top tasks (vs frontier)

| Task | Score | Frontier | % of Frontier |
|---|---|---|---|
| Chemistry_000 (KA-GNN) | 72.2 | 49.0 | **147%** |
| Energy_000 (Li-ion battery) | 68.0 | 52.0 | **131%** |
| Information_002 (MoTe₂/WSe₂ HF) | 60.0 | 86.4 | 69% |
| Earth_000 (glacier mass) | 58.5 | — | — |
| Energy_003 (building load) | 54.9 | 61.4 | 89% |
| Astronomy_000 (ULB superradiance) | 50.5 | 94.7 | 53% |

## Layout

```
reports/
  <TaskID>_<date>/
    _meta.json        # task_id, run_id, agent_name, model, status, timestamp, duration_seconds
    _score.json       # total_score + per-item judge reasoning
    report/report.md  # research report
    report/images/    # reproduced figures
    code/             # reproducible analysis scripts
scores.json           # leaderboard-format summary
```

## What is / is NOT included

**Included**: per-run `_meta.json`, `_score.json`, `report/`, `code/`.
**Omitted**: `data/` and `related_work/` (public in the RCB task repo), `target_study/` (hidden criteria owned by the maintainers).

## Notes

- Each `_score.json` `total_score` matches the `score` in `scores.json`.
- `duration_seconds` is estimated from file timestamps (manual runs were not wall-clock instrumented).
- A few reduced workspaces (Earth_003, Neuroscience_001) did not ship the full forecast/model artifacts; those reports state the limitation honestly.

## Contact

Doerking on GitHub.
