# Submission Email Draft

**To**: xu_wanghan@sjtu.edu.cn
**Subject**: RCB submission · Hakimi · 6 tasks (partial set)

---

Hi Wanghan,

We'd like to submit a partial agent evaluation on ResearchClawBench. Below are the details.

## Agent

- **Name**: Hakimi
- **Runtime**: pi + Hakimi (manual)
- **Models**: `deepseek/deepseek-flash`, `sensenova-6.8-flash-lite`

## Results (6 of 40 tasks)

| Task | Score | Frontier | % of Frontier |
|---|---|---|---|
| Chemistry_000 (KA-GNN) | 72.2 | 39.8 | 181% |
| Chemistry_001 (AlphaFold 3) | 30.4 | 22.8 | 133% |
| Energy_000 (Li-ion battery) | 68.0 | 51.5 | 132% |
| Astronomy_002 (H0 distance network) | 40.5 | 35.3 | 115% |
| Information_002 (MoTe₂/WSe₂ HF) | 60.2 | 57.9 | 104% |
| Information_000 (Decoupled visual encoding) | 53.2 | 52.6 | 101% |

All 6 tasks exceed the current frontier on those cells.

## Artifacts

- **Full reports**: https://github.com/doerking/rcb-hakimi-submission
  - Per task: `INSTRUCTIONS.md`, `_meta.json`, `_score.json` (with per-item judge reasoning), `report/report.md`, `outputs/`, `code/`
  - `data/`, `related_work/`, and `target_study/` are omitted (publicly available in the RCB repo; hidden criteria are your copy).
- **Leaderboard summary**: `scores.json` at the repo root, structured to match `/api/leaderboard`.

## Notes

- The `total_score` field in each task's `_score.json` matches the score above. Per-item judge reasoning is preserved for audit.
- Runs were completed 2026-10-12 through 2026-10-13.
- Happy to add more tasks or re-run with a different configuration on request.

Best,
doerking
