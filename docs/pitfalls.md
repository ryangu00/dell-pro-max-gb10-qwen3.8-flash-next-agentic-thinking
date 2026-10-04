# Pitfalls

Each pitfall is written as symptom → root cause → fix → how we found it. Numbers and conditions are copied unchanged from the source fact sheet.

## 1. Interpreting the c7a gap without its measurement conditions

- **Symptom:** NF c7-agentic-if 81.7 median vs DSV4F 95/95/95, a 13-point gap, with a gate of >=90 — looks like a model defect in agentic tool use.
- **Root cause:** The score change does not establish a sole cause. The initial comparison had both models in non-thinking greedy mode, while the HF model card (huggingface.co/Qwen/Qwen3.8-Flash-Next, revision not recorded) notes that every official agentic score was measured in the vendor's agentic harness (named in the card footnote), temp 1.0 / top_p 0.95, 256K, **thinking mode on by default (reasoning effort xhigh)**, with the official serving recipe `--tool-call-parser qwen3_coder --reasoning-parser qwen3`. Our gate ran non-thinking + greedy + `qwen3_xml` — a different measurement setting. With thinking on for both models and each vendor's official thinking sampling, the observed c7a gap narrowed from 81.7 vs 95.0 to 93.3 vs 95.0. Their thinking tiers were not equivalent, and the size of that asymmetry's effect was not measured (see Limit 1 in [Limits](../README.md#limits)); these results do not establish full alignment with the vendor's official conditions or rule out a model-capability difference.
- **Fix applied:** We ran both models with thinking on + each vendor's official thinking sampling + `qwen3_coder` + 1M YaRN factor 4 in the R4 full table. They shared the evaluation mode, but NF used its default "xhigh" with effort unset and DSV4F used "high". The earlier R2 candidate-fixes run recorded NF at 93.3 median with thinking on + official sampling. Result: NF 81.7 -> 93.3 (R2 candidate-fixes run) / 91.7 (R4 full table, median of 5 runs), gate passes; the three restraint-type questions that scored zero in every non-thinking run went to full marks. The full-table verdict is subject to all three [Limits](../README.md#limits).
- **How we found it:** Reading the model card footnotes identified the official harness, sampling and thinking default. The subsequent thinking-mode runs recorded the narrower c7a gap described above.

## 2. Mistaking the gap for an engine bug

- **Symptom:** The c7a gap concentrated in Restraint (2/4 vs 4/4), Parameter (3/6 vs 5/6), and Error-Recovery (17-20/24 vs 22/24), with identical Multi-Step Chains (6/6 vs 6/6).
- **Root cause:** The observed failures are not the runaway loop (zero runaways, wall clock under the gate, multi-step chains at full marks); we did not test other engine-level hypotheses. The signature is act-before-reasoning behavior; lowering reasoning effort below the documented warning level re-introduces failed/repeated retries per the card itself.
- **Fix:** Thinking mode flips exactly those restraint-shaped items (the three restraint-type questions that scored zero in every non-thinking run, from all-zero to full marks).
- **How we found it:** The c7a per-sub-category breakdown (R5) showed the failure shape was mainly restraint-shaped and the multi-step chains were intact, so the focus moved to the measurement setting; other engine-level explanations were not tested.

## 3. Confounding parser and sampling

- **Symptom:** Greedy vs official-sampling comparisons changed when the parser also changed — effects were confounded, not isolated.
- **Root cause:** Two variables (sampling and parser) moved together, so the score deltas could not be attributed to either.
- **Fix applied:** We ran a parser A/B in isolation: `qwen3_xml` greedy 81.7 median vs `qwen3_coder` 85.0; at thinking + official sampling both 93.3 but `qwen3_coder` had smaller variance. We adopted the official parser `qwen3_coder`.
- **How we found it:** The four-candidate-fixes run made it clear parser and sampling were entangled, prompting the isolated parser A/B (R3).

## 4. Non-comparable wall-clock aggregations

- **Symptom:** The candidate-fixes table (R2) records thinking-mode per-run wall as 81-97 s (NF) / 97-128 s (DSV4F), while R7 records 308-364 s per run (NF thinking) — seemingly contradictory.
- **Root cause:** Cause not fully established. R7 labels its figure as the serial sum of 30 questions per run; R2's table metric aggregation is not defined in the source, and timing start/end and concurrency differ between the two. These are also different runs taken on different days; on this 30-question category one question is 3.3 points, so three-run medians can differ by 5-10 points between sessions, but that score-step argument does not by itself explain a ~4x wall-clock difference.
- **Fix:** Always publish the aggregation (per-run serial sum vs table metric) alongside the number.
- **How we found it:** Cross-checking R2 against R7 surfaced the two wall-clock scales; both are reproduced unchanged and not reconciled.

## 5. Comparing gates from different adjudication baselines

- **Symptom:** The non-thinking R1 and thinking-mode R4 tables have different baseline scores and derived gates (c7a gate >=90.0 in R1 vs >=85.0 in R4). A gate pass in one table is relative to that table's baseline.
- **Root cause:** R4's gates were recomputed from its thinking-mode baseline (critical categories use baseline minus 5 points, other categories baseline minus 10 points). Its c7a gate was >=85.0, while R1 and R2 used >=90.0; those gate passes refer to different baselines.
- **Fix applied:** Both models were evaluated in thinking mode for the rule-v3 full table (R4), with unequal thinking tiers: NF used its default "xhigh" with effort unset; DSV4F used "high". The 11/11 pass for NF is the recorded verdict for those configurations, subject to all three [Limits](../README.md#limits): unequal thinking tiers, missing c9 reasoning pass-back, and an unverified c9 timeout/throughput contribution.
- **How we found it:** The thinking-mode full table recomputed every gate against the thinking-mode baseline, which made the gate difference visible.

## Related pitfalls (out of scope here)

- The MTP draft's 262144 QSA limit despite `--max-model-len 1000000` — see `dell-pro-max-gb10-qwen3.8-flash-next-1m-context` (external report; not independently verified here).
- The async-scheduling × MTP runaway-loop race (3/120) and its `--no-async-scheduling` fix — see `dell-pro-max-gb10-vllm-mtp-async-runaway` (external report; not independently verified here). This loop had been fixed before this investigation started; the non-thinking c7a gate still failed after that fix.
