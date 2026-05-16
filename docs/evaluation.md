# Evaluation Module

Status: `planned`

## Responsibility
- Measure answer quality, grounding, and retrieval relevance.
- Track fallback rate and confidence distribution.
- Validate regressions after prompt/retrieval changes.

## Expected Assets
- `datasets/`: curated test question sets by domain/lang
- `metrics.py`: scoring logic (precision@k, groundedness, fallback rate)
- `runs/`: timestamped evaluation outputs
- `reports/`: markdown summaries for portfolio/demo

## Initial KPI Targets
- Grounded answer rate > 80% on covered questions
- Hallucination rate < 5%
- Stable fallback behavior on out-of-scope questions
