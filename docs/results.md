# Results

All numbers copied verbatim from the source fact sheet with their conditions unchanged. NF = Qwen3.8-Flash-Next; B/DSV4F = DeepSeek V4 Flash Vision-Exp comparison baseline. Scores are eval-bank percentages; gates are rule-v3 minimums. own-mean = mean of the 8 non-pack categories (c1-kbqa, c2-longctx, c4-code, c5-extract, c6-vision, c7-zhif, c9-long-coding, c10-sre-ops) in percentage points.

R4's thinking-mode gates were recomputed from its thinking-mode baseline (critical categories use baseline minus 5 points, other categories baseline minus 10 points), giving a c7a gate of >=85.0 in R4. R1's non-thinking c7a gate and R2's candidate-fixes c7a gate were >=90.0.

**Aggregation rule (applied consistently to every table below):** each category score is the median of two runs; when the two runs differ by more than 5 points the lower run is used and the cell is marked ⚠. c7-agentic-if uses the median of all runs listed. c2-longctx is the 30-item set including the 200K tier.

## R1 — Rule v3, non-thinking + greedy, NF (runaway loop already fixed) vs DSV4F

Condition: 2 runs per category, c7a = 3 runs; bank: our private 11-category eval bank (questions not published); the runaway agent loop had been fixed with `--no-async-scheduling` before this run.

| cat | B | cand (NF) | runs(cand) | gate | ok |
|---|---|---|---|---|---|
| c1-kbqa | 83.3 | 90.0 ⚠ | [90.0, 96.66666666666667] | ≥73.3 | ✓ |
| c2-longctx (crit) | 87.5 | 100.0 | [100.0, 100.0] | ≥82.5 | ✓ |
| c3-tool (crit) | 66.7 | 85.0 | [83.33333333333333, 86.66666666666667] | ≥61.7 | ✓ |
| c4-code | 87.5 | 95.8 | [95.83333333333333, 95.83333333333333] | ≥77.5 | ✓ |
| c5-extract | 92.2 | 91.1 | [92.27777777777779, 89.83333333333333] | ≥82.2 | ✓ |
| c6-vision (crit) | 82.5 | 85.0 | [85.0, 85.0] | ≥77.5 | ✓ |
| c7-zhif | 73.3 | 85.0 | [86.66666666666667, 83.33333333333333] | ≥63.3 | ✓ |
| c7-agentic-if (crit) | 95.0 | 81.7 | [85.0, 80.0, 81.66666666666667] | ≥90.0 | ✗ |
| c8-judgment (crit) | 78.3 | 75.0 | [73.33333333333333, 76.66666666666667] | ≥73.3 | ✓ |
| c9-long-coding (crit) | 100.0 | 98.3 | [100.0, 96.52777777777779] | ≥95.0 | ✓ |
| c10-sre-ops | 73.3 | 88.3 | [86.66666666666667, 90.0] | ≥63.3 | ✓ |

Same run, wall-clock gates (<=1.5x baseline): c3-tool B 39s vs cand 46s (limit 59s) pass; c6-vision 18s vs 17s (limit 27s) pass; c7-agentic-if 42s vs 52s (limit 63s) pass. Performance gates (units/conditions: decode tok/s = single stream on a 400-token prose completion; cold prefill tok/s = on a ~2.3K-token prompt; six-stream tok/s = aggregate of six concurrent streams; KV = engine-reported KV pool tokens for the two-node engine): decode 32.8 vs 51.2 tok/s (>=33) pass; prefill 2129 vs 3159 tok/s (>=2000) pass; six-stream 82.8 vs 87.6 tok/s (>=75) pass; KV tokens 1492180 vs 3455574 (>=1.5e6) pass. Errors 0 vs 0. (errors = requests that returned an HTTP error or timed out; they score zero for that item and are counted in the denominator.) change own (common categories) = 91.7 - 85.0 = **+6.7**. Verdict recorded: **negative result (keep status quo)** — only c7a failed.

**Source disagreement (must be stated):** these are different runs taken on different days; on this 30-question category one question is 3.3 points, so three-run medians can differ by 5-10 points between sessions. The isolation note records the no-async c7a median as **91.7** (120-question single-variable isolation), while the same-condition rule-v3 re-adjudication records **81.7** (runs 85.0/80.0/81.7, run totals 51/48/49 of 60). Both figures appear in the sources; the decision used the 81.7 full-table value.

## R2 — Four candidate fixes, c7-agentic-if x 3, both models

Condition: c7a x 3 runs per fix, with both models in the same evaluation mode per fix. Their thinking tiers were not equivalent; the 2026-09-19 DSV4F c7a thinking-mode runs used "high" (see Limit 1 in [Limits](../README.md#limits)).

| fix / condition | DSV4F 3 runs (median) | NF-B 3 runs (median) | verdict |
|---|---|---|---|
| baseline: non-thinking + greedy (v3) | 95/95/95 (95) | 85/80/81.7 (81.7) | fail |
| restraint system prompt (three hard rules) | 91.7/95/95 (95) | 81.7/81.7/78.3 (81.7) | fail no median improvement in three runs |
| each vendor's official non-thinking sampling (DS t1.0/0.95; NF t0.7/0.8/top_k20/rep_pen1.5) | 95/81.7/88.3 (88.3) | 76.7/81.7/85 (81.7) | fail no median improvement in three runs; larger spread |
| **thinking on + each vendor's official thinking sampling** | 95/95/95 (wall 97-128 s) | **93.3/91.7/95 (93.3, wall 81-97 s)** | **pass passes gate >=90 and wall clock** |
| framework-layer guardrails (tool-loop guard / deny-retry) | - | - | fail guard shape mismatched the failure (zero errors; a different tool each step) |

## R3 — Parser comparison (c7a x 3, NF)

Condition: c7a x 3 runs, NF, two parsers at two settings.

| condition | qwen3_xml (cluster recipe) | qwen3_coder (official recipe) |
|---|---|---|
| greedy, non-thinking | 85/80/81.7 (81.7) | 86.7/83.3/85.0 (85.0) |
| thinking + official sampling | 93.3/91.7/95.0 (93.3) | 95.0/93.3/93.3 (93.3) |

Decision in sources: adopt `qwen3_coder` (in the thinking row, equal median with smaller variance; matches official recipe).

## R4 — Rule v3 full table under thinking mode + official thinking sampling

Condition: both models thinking on, `max_tokens 16384`, `qwen3_coder`, NF at 1M YaRN factor 4; 2 runs/category, c7a = 5 runs for cand after merging reruns. This shared evaluation mode did not mean equivalent thinking tiers: NF left effort unset and used its default "xhigh", while DSV4F explicitly used "high" (see Limit 1 in [Limits](../README.md#limits)).

| cat | B (DSV4F) | cand (NF) | runs(cand) | gate | ok |
|---|---|---|---|---|---|
| c1-kbqa | 91.7 | 88.3 | [90.0, 86.66666666666667] | ≥81.7 | ✓ |
| c2-longctx (crit) | 82.5 | 87.5 ⚠ | [86.66666666666667, 93.33333333333333] | ≥77.5 | ✓ |
| c3-tool (crit) | 56.7 | 76.7 | [76.66666666666667, 76.66666666666667] | ≥51.7 | ✓ |
| c4-code | 79.2 | 95.8 | [95.83333333333333, 95.83333333333333] | ≥69.2 | ✓ |
| c5-extract | 89.4 | 84.2 | [84.55555555555556, 83.8888888888889] | ≥79.4 | ✓ |
| c6-vision (crit) | 86.2 | 87.5 | [87.5, 87.5] | ≥81.2 | ✓ |
| c7-zhif | 85.0 | 90.0 ⚠ | [96.66666666666667, 90.0] | ≥75.0 | ✓ |
| c7-agentic-if (crit) | 90.0 | 91.7 | [90.0, 93.33333333333333, 88.33333333333333, 91.66666666666667, 91.66666666666667] (5 runs) | ≥85.0 | ✓ |
| c8-judgment (crit) | 81.7 | 98.3 | [100.0, 96.66666666666667] | ≥76.7 | ✓ |
| c9-long-coding (crit) | 82.3 | 100.0 | [100.0, 100.0] | ≥77.3 | ✓ |
| c10-sre-ops | 76.7 | 70.0 ⚠ | [76.66666666666667, 70.0] | ≥66.7 | ✓ |

Same run: wall c3-tool 94s vs 96s (limit 141s) pass; c6-vision 305s vs 266s (limit 458s) pass; c7-agentic-if 107s vs 88s (limit 160s) pass. Performance: decode 32.8 vs 51.2 tok/s (>=33) pass; prefill 2129 vs 3159 tok/s (>=2000) pass; six-stream 82.8 vs 87.6 tok/s (>=75) pass; KV 1492180 vs 3455574 (>=1.5e6) pass. Errors 34 vs 2 (the 34 vs 2 refers to this thinking-mode full table; the comparison model's engine died once during this run and the affected categories were re-run). change own = 87.9 - 84.1 = **+3.8**. Verdict recorded: **candidate/win** (11/11 categories, wall 3/3, perf 4/4). Read this full-table verdict and own-mean change together with all three [Limits](../README.md#limits): unequal thinking tiers, missing c9 reasoning pass-back, and an unverified c9 timeout/throughput contribution. Key-category margins: c8-judgment NF 98.3 vs 81.7; c9 100 vs 82.3 (the c9 figures are subject to Limits 2 and 3: reasoning not passed back; DSV4F errors and timeouts not separated); c7a 91.7 vs 90 (median of 5 runs); c2 87.5 vs 82.5; c3 76.7 vs 56.7; tightest pass: c10 70 vs gate 66.7 (non-critical).

## R5 — c7a per-sub-category, non-thinking, no-async

Condition: 30 questions x 2 = 60 max; NF runs r1/r2/r3 vs DSV4F r1/r2/r3.

| sub-category | NF r1/r2/r3 | DSV4F r1/r2/r3 |
|---|---|---|
| A Tool Selection | 20/20 / 20/20 / 18/20 | 20/20 / 20/20 / 20/20 |
| B Parameter Precision | 3/6 / 3/6 / 3/6 | 5/6 / 5/6 / 5/6 |
| C Multi-Step Chains | 6/6 / 6/6 / 6/6 | 6/6 / 6/6 / 6/6 |
| D Restraint & Refusal | 2/4 / 2/4 / 2/4 | 4/4 / 4/4 / 4/4 |
| E Error Recovery | 20/24 / 17/24 / 20/24 | 22/24 / 22/24 / 22/24 |
| **total** | **51 / 48 / 49** | **57 / 57 / 57** |

The three restraint-type questions that scored zero in every non-thinking run score full marks in thinking mode. The failure signature in the non-thinking runs is mainly restraint-shaped (extra tool call after ENOENT, following a second reference, one more count-loop) — "act first without reasoning" behavior, consistent with the model card's own warning that lowering reasoning effort increases failures and repeated retries.

## R7 — Same questions under thinking mode (wall clock and token cost)

Condition: c7a questions under thinking on + official thinking sampling, NF non-thinking shown for contrast.

**Wall clock and token cost for R7 condition** (per run = serial sum of 30 questions): NF thinking [364, 338, 308] s; DSV4F thinking [330, 355, 365] s; NF non-thinking [195, 183, 212] s; DSV4F non-thinking [154, 153, 157] s. Completion tokens/run: NF thinking [7742, 7014, 6054]; DSV4F thinking [6609, 7327, 8030]; NF non-thinking [2072, 1860, 2652]; DSV4F non-thinking [2652, 2592, 2608]. Cost verdict in source: NF 6.0-7.7K vs DSV4F 6.6-8.0K tokens/run -- same output-token order of magnitude.

**Note on wall figures:** these are different runs taken on different days; on this 30-question category one question is 3.3 points, so three-run medians can differ by 5-10 points between sessions. The candidate-fixes table (R2) records thinking-mode per-run wall as 81-97 s (NF) / 97-128 s (DSV4F), while R7 records 308-364 s per run (NF thinking) -- the sources state these as different measurements; both are reproduced here and not reconciled.

## R8 — Reasoning-effort ladder, c7a x 3, NF, thinking + official sampling

Condition: c7a x 3 runs, NF, thinking on + official thinking sampling, three effort levels.

| effort | median score | completion tokens | wall |
|---|---|---|---|
| xhigh (default) | 91.7 | 6.3-9.2K | 313-433 s |
| medium | 91.7 | 5.6-6.0K | 290-306 s |
| low | 91.7 | 4.6-5.2K | 252-271 s |

Source conclusion: on this category the three effort levels tied (91.7 median each); we chose low for the fast tier and medium for the quality tier; other categories were not re-run per effort level.
