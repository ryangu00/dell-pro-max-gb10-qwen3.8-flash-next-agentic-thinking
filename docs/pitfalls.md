# Pitfalls

Each pitfall is written as symptom → root cause → fix → how we found it. Numbers and conditions are copied unchanged from the source fact sheet.

## 1. Measurement-setting gap mistaken for a model defect

- **Symptom:** NF c7-agentic-if 81.7 median vs DSV4F 95/95/95, a 13-point gap, with a gate of ≥90 — looks like a model defect in agentic tool use.
- **Root cause:** Measurement-setting artifact (supported as a candidate explanation, not the only possible cause). The initial comparison had both models in non-thinking greedy mode, while the HF model card (huggingface.co/Qwen/Qwen3.8-Flash-Next, revision not recorded) notes that every official agentic score was measured in the vendor's agentic harness (named in the card footnote), temp 1.0 / top_p 0.95, 256K, **thinking mode on by default (reasoning effort xhigh)**, with the official serving recipe `--tool-call-parser qwen3_coder --reasoning-parser qwen3`. Our gate ran non-thinking + greedy + `qwen3_xml` — a different measurement setting. Aligning both models to thinking mode + each vendor's official thinking sampling closed the gap in our bank; this supports the configuration-combination explanation for the local score change, and does not by itself prove full alignment with the vendor's official conditions or rule out a model-capability difference.
- **Fix:** Rerun both models at the aligned setting (thinking on + each vendor's official thinking sampling + `qwen3_coder` + 1M YaRN factor 4) — this is the R4 thinking-mode full table; the R2 candidate-fixes run first isolated thinking-on + official sampling as the working fix (NF 93.3 median). Result: NF 81.7 → 93.3 (R2 candidate-fixes run) / 91.7 (R4 full table, median of 5 runs), gate passes; the three restraint-type questions that scored zero in every non-thinking run go to full marks.
- **How we found it:** The "Official-measurement check" step — reading the model card footnotes — revealed the official harness, sampling, and thinking-default, then rerunning under that setting closed the gap.

## 2. Mistaking the gap for an engine bug

- **Symptom:** The c7a gap concentrated in Restraint (2/4 vs 4/4), Parameter (3/6 vs 5/6), and Error-Recovery (17–20/24 vs 22/24), with identical Multi-Step Chains (6/6 vs 6/6).
- **Root cause:** The observed failures are not the runaway loop (zero runaways, wall clock under the gate, multi-step chains at full marks); we did not test other engine-level hypotheses. The signature is act-before-reasoning behavior; lowering reasoning effort below the documented warning level re-introduces failed/repeated retries per the card itself.
- **Fix:** Thinking mode flips exactly those restraint-shaped items (the three restraint-type questions that scored zero in every non-thinking run, from all-zero to full marks).
- **How we found it:** The c7a per-sub-category breakdown (R5) showed the failure shape was mainly restraint-shaped and the multi-step chains were intact, so the focus moved to the measurement setting; other engine-level explanations were not tested.

## 3. Confounding parser and sampling

- **Symptom:** Greedy vs official-sampling comparisons changed when the parser also changed — effects were confounded, not isolated.
- **Root cause:** Two variables (sampling and parser) moved together, so the score deltas could not be attributed to either.
- **Fix:** Run a parser A/B in isolation: `qwen3_xml` greedy 81.7 median vs `qwen3_coder` 85.0; at thinking + official sampling both 93.3 but `qwen3_coder` has smaller variance. Decision: standardize on the official parser `qwen3_coder`.
- **How we found it:** The four-candidate-fixes run made it clear parser and sampling were entangled, prompting the isolated parser A/B (R3).

## 4. Non-comparable wall-clock aggregations

- **Symptom:** The candidate-fixes table (R2) records thinking-mode per-run wall as 81–97 s (NF) / 97–128 s (DSV4F), while R7 records 308–364 s per run (NF thinking) — seemingly contradictory.
- **Root cause:** Cause not fully established. R7 labels its figure as the serial sum of 30 questions per run; R2's table metric aggregation is not defined in the source, and timing start/end and concurrency differ between the two. These are also different runs taken on different days; on this 30-question category one question is 3.3 points, so three-run medians can differ by 5–10 points between sessions, but that score-step argument does not by itself explain a ~4× wall-clock difference.
- **Fix:** Always publish the aggregation (per-run serial sum vs table metric) alongside the number.
- **How we found it:** Cross-checking R2 against R7 surfaced the two wall-clock scales; both are reproduced unchanged and not reconciled.

## 5. Switching adjudication basis moves both sides

- **Symptom:** Moving the gate from non-thinking to thinking changed both models' scores and the derived gates (e.g., c7a gate ≥90.0 → ≥85.0; c9 100.0 → 82.3 for DSV4F), so a single-sided "candidate caught up" reading was invalid.
- **Root cause:** Thinking-mode gates are recomputed from the thinking-mode baseline (critical categories use baseline minus 5 points, other categories baseline minus 10 points), so the gate itself moves when the setting moves; a comparison across settings compares unlike baselines.
- **Fix:** Rerun both sides in one setting before any verdict — the rule-v3 thinking-mode full table (R4) reruns DSV4F and NF together, so the 11/11 pass for NF is a like-for-like verdict.
- **How we found it:** The thinking-mode full table recomputed every gate against the thinking-mode baseline, which made the gate shift visible and forced the two-sided rerun.

## Related pitfalls (out of scope here)

- The MTP draft's 262144 QSA limit despite `--max-model-len 1000000` — see `dell-pro-max-gb10-qwen3.8-flash-next-1m-context` (external report; not independently verified here).
- The async-scheduling × MTP runaway-loop race (3/120) and its `--no-async-scheduling` fix — see `dell-pro-max-gb10-vllm-mtp-async-runaway` (external report; not independently verified here). This loop had been fixed before this investigation started; the non-thinking c7a gate still failed after that fix.
