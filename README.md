# Hakimi · RCB Submission

**Agent**: Hakimi
**Runtime**: pi + Hakimi (manual)
**Models**: `deepseek/deepseek-flash`, `sensenova-6.8-flash-lite`
**Submitted**: 2026-10-13

## Summary

6 out of 40 ResearchClawBench tasks submitted. All 6 clear their frontier baseline (score > frontier reference).

| Task | Score | Frontier | % of Frontier |
|---|---|---|---|
| Chemistry_000 (KA-GNN) | 72.2 | 39.8 | **181.4%** |
| Chemistry_001 (AlphaFold 3) | 30.4 | 22.8 | **133.3%** |
| Energy_000 (Li-ion battery) | 68.0 | 51.5 | **132.0%** |
| Astronomy_002 (H0 distance network) | 40.5 | 35.3 | **114.7%** |
| Information_002 (MoTe₂/WSe₂ HF) | 60.2 | 57.9 | **104.0%** |
| Information_000 (Decoupled visual encoding) | 53.2 | 52.6 | **101.1%** |

## Layout

```
reports/
  <TaskID>_<YYYYMMDD>/
    INSTRUCTIONS.md   # Task prompt
    _meta.json        # Run metadata (agent, timestamp)
    _score.json       # Per-item scoring with reasoning
    report/report.md  # AI-generated report
    outputs/          # Reproduced figures
    code/             # Analysis scripts
scores.json           # Leaderboard-format summary (see below)
```

## Scores JSON format

`scores.json` uses the same key structure as RCB's `server.py /api/leaderboard` returns:

```json
{
  "scores": {
    "<task_id>": {
      "score": <float>,
      "run_id": "<task_id>_<YYYYMMDD>",
      "model": "<model string>"
    }
  }
}
```

Extended fields (`frontier_pct`, `frontier_ref`, `notes`) are provided for maintainer convenience and can be dropped when ingesting.

## What is included

- `INSTRUCTIONS.md` — Task prompt (same as `tasks/<TaskID>/` in the RCB repo)
- `_meta.json` — Run metadata (task_id, run_id, timestamp, agent_name)
- `_score.json` — Full per-item scoring with reasoning, produced by RCB's own judge
- `report/report.md` — AI-generated research report
- `outputs/` — AI-generated figures
- `code/` — AI-generated analysis scripts

## What is NOT included

- `data/` — Task input data (already public in the RCB task repo; omit to keep submission lean)
- `related_work/` — Ground-truth reference papers (already public in RCB task repo)
- `target_study/` — Hidden evaluation criteria (must not be included; maintainers have their own copy)

## Verification

Each report's `_score.json` contains the full per-item rubric reasoning. The `total_score` in each `_score.json` matches the `score` field in `scores.json`.

## Contact

Doerking on GitHub.
