![banner](docs/assets/banner.png)

# Agentic gap is a measurement setting, not a bug — Qwen3.8-Flash-Next on two Dell Pro Max with GB10

> We ran a two-node Qwen3.8-Flash-Next (NF) build against our private 11-category eval bank (questions not published) under our rule-v3 adjudication and it failed exactly one gate: c7-agentic-if scored 81.7 median (runs 85.0 / 80.0 / 81.7) against the comparison model 95/95/95 with a gate of ≥90. We tested four candidate fixes, of which one (thinking mode) worked: thinking mode + each vendor's official thinking sampling, taking NF to 93.3/91.7/95 (median 93.3) at passing wall clock, with the three restraint-type questions that scored zero in every non-thinking run going to full marks. The point of this cookbook is the **evidence**: the "agentic gap" was a measurement setting — the initial comparison had both models in non-thinking greedy mode, while the vendor's published agentic scores were taken in thinking mode; aligning both models to thinking mode + each vendor's official thinking sampling closed the gap — not a model defect, and the full thinking-mode rule-v3 table flips the whole bank to 11/11 gates passed for NF. The comparison model is DeepSeek V4 Flash Vision-Exp on the same two nodes (its own speculative-decoding stack, async scheduling on); it produced zero runaway loops in 330 questions.

## Why this matters

A 13-point gap on an agentic-tool category is the kind of number that gets a model rejected. Here the initial comparison had both models in non-thinking greedy mode, while the vendor's published scores were taken in thinking mode; aligning both models to thinking mode + each vendor's official thinking sampling closed the gap. The lesson is general: when a comparison gate flips the verdict from "keep status quo" to "candidate/win" solely by aligning the measurement setting, the earlier number was never about the model.

The runaway agent loop that had once depressed this category had already been fixed with `--no-async-scheduling` before this investigation started, and the non-thinking c7a gate still failed after that fix — so the gap that remained was a measurement-setting question, not an engine question. This cookbook records the four candidate fixes (of which one, thinking mode, worked), the parser A/B, the thinking-mode full table, the per-sub-category breakdown, the reasoning-effort ladder, and the conditions under which every number was taken.

Two things are deliberately out of scope here and live in their own cookbooks (see Related cookbooks): the 1M build recipe with the MTP-draft `max_model_len` discovery, and the async-scheduling × MTP runaway-loop isolation.

## Hardware and stack

- Two nodes, each a **Dell Pro Max with GB10** (referred to below as "head node" / "worker node").
- Serving: the community two-node cluster recipe —
  - vLLM b12x MoE backend;
  - TP2 over RoCE;
  - fp8 KV cache;
  - MTP-4 speculative decoding;
  - static YaRN factor 4 to 1M context.
  - (The 1M build recipe and the MTP-draft `max_model_len` discovery are a separate cookbook; see Related cookbooks.)
- Parser flags used here: `--tool-call-parser qwen3_coder --reasoning-parser qwen3`. Earlier runs used the cluster recipe's `qwen3_xml`; we adopted `qwen3_coder` after the parser A/B (see [Results](docs/results.md) R3).
- Evaluation harness: our private 11-category eval bank (questions not published; category names c1-kbqa … c10-sre-ops are public in this sheet), run under rule v3 —
  - c7a median of 3 runs;
  - agentic/tool wall clock ≤ 1.5× baseline;
  - c7a in the critical-category set;
  - one comparison tool as the adjudicator.
  - Thinking-mode runs used `max_tokens 16384` and each vendor's official thinking sampling.
- Comparison model: DeepSeek V4 Flash Vision-Exp (DSV4F) on the same two nodes (its own speculative-decoding stack, async scheduling on); it produced zero runaway loops in 330 questions, i.e., not affected by the NF loop bug.

## Versions and images

- Community two-node recipe: `qwen3.8-flash-next-nvfp4-cluster` in github.com/eugr/spark-vllm-docker; image `vllm-node-b12x` (digest prefix `d6fb7a6a277d`).
- vLLM build: `v0.1.dev20759+gb40673cd0`.
- Weights: `local-inference-lab/Qwen3.8-Flash-Next-NVFP4` (revision not recorded).
- Driver: `580.178.04`.
- Kernel: `7.0.0-1019`.

## Reproducibility

Quality scores in this cookbook come from a private eval bank and are reported here, not reproducible by readers. What is reproducible is the measurement-setting alignment itself — thinking mode on, each vendor's official thinking sampling, and the `qwen3_coder` parser — which any reader can apply to their own harness to test their own model against their own baseline under matched settings.

Request fields used for the candidate (NF), thinking mode on: `chat_template_kwargs {"enable_thinking": true}`, `reasoning_effort` (low / medium in the reasoning-effort ladder, xhigh elsewhere), `temperature 1.0`, `top_p 0.95`, `top_k 20`, `presence_penalty 0.0`, `max_tokens 16384`, served with `--tool-call-parser qwen3_coder --reasoning-parser qwen3`. For the comparison model (DSV4F): `chat_template_kwargs {"thinking": true}` and its vendor's documented thinking sampling (values per its model card; not restated here). Model card reference: huggingface.co/Qwen/Qwen3.8-Flash-Next (revision not recorded); its footnote is quoted only as "agentic scores measured with thinking on, reasoning effort xhigh, temp 1.0 / top_p 0.95, 256K, in the vendor-named agent harness".

## How to reproduce

Steps in the order actually run. Every number and flag below comes from the source fact sheet; where a prerequisite is internal to our setup (the eval bank, the comparison tool) we say so explicitly rather than guessing a public substitute.

1. **Re-adjudicate the full rule-v3 table** (non-thinking, greedy, the runaway loop already fixed with `--no-async-scheduling`): 11-category run × 2 + c7a × 3 + performance probes for NF vs the comparison DSV4F baseline. This is the R1 headline: NF failed only c7-agentic-if; every other category passed its gate.
2. **Break c7a down per sub-category** for that run (30 questions × 2 points = 60 max, both models, 3 runs) to locate the failure shape. The gap turned out to be mainly restraint-shaped, with the multi-step chains intact — pointing at the measurement setting.
3. **Check the official measurement setting**: the HF model card (huggingface.co/Qwen/Qwen3.8-Flash-Next, revision not recorded) notes that every official agentic score was measured in the vendor's agentic harness (named in the card footnote), temp 1.0 / top_p 0.95, 256K, thinking mode on by default (reasoning effort xhigh), with the official serving recipe `--tool-call-parser qwen3_coder --reasoning-parser qwen3`. Our c7a numbers were non-thinking + greedy + `qwen3_xml` — a different measurement setting.
4. **Test four candidate fixes, each c7a × 3, both models under identical conditions** (see R2 in [Results](docs/results.md)):
   - restraint system prompt (three hard rules);
   - each vendor's official non-thinking sampling (DSV4F: t1.0/top_p0.95; NF: t0.7/top_p0.8/top_k20/rep_pen1.5);
   - thinking on + each vendor's official thinking sampling;
   - framework-layer tool-loop guardrails (retry-denial guard).
5. **Run the parser A/B** (c7a × 3): `qwen3_xml` vs official `qwen3_coder`, at greedy non-thinking and at thinking + official sampling (see R3 in [Results](docs/results.md)). This isolates the parser variable from the sampling variable, which the four-candidate run had entangled. Decision: adopt `qwen3_coder`.
6. **Run the overnight thinking-mode rule-v3 full table**: both models, thinking on + official thinking sampling + `max_tokens 16384` + `qwen3_coder` + 1M YaRN factor 4; 11 categories × 2 + c7a × 3 per model, plus a reasoning-effort ladder on c7a (see R4 and R8 in [Results](docs/results.md)). Gates in this table are recomputed from the thinking-mode baseline, not carried over from R1.
7. **Break c7a down per sub-category** under both non-thinking and thinking (see R5 in [Results](docs/results.md)). This is what shows the three restraint-type questions that scored zero in every non-thinking run scoring full marks in thinking mode.

## Results

All tables, with a one-line note of the measurement conditions above each, are in [docs/results.md](docs/results.md). Headline numbers, copied unchanged with their conditions:

- **R1 (non-thinking + greedy, runaway loop already fixed):** 2 runs/category, c7a = 3 runs, both models on the same two-node engine with different speculative-decoding stacks. NF failed only c7-agentic-if — 81.7 median (runs 85.0/80.0/81.7) vs DSV4F 95/95/95, gate ≥90.0. Δ own (common categories) +6.7. Verdict: negative result (keep status quo), only c7a failed.
- **R2 (four candidate fixes, c7a × 3, both models):** identical conditions per fix. Only thinking on + each vendor's official thinking sampling passed — NF 93.3/91.7/95 (median 93.3, wall 81–97 s), DSV4F 95/95/95 (wall 97–128 s), gate ≥90 and wall clock both pass. The restraint prompt and the official non-thinking sampling both had zero median effect on NF.
- **R3 (parser A/B, c7a × 3, NF):** `qwen3_xml` vs `qwen3_coder` at greedy non-thinking and at thinking + official sampling. Decision: adopt `qwen3_coder` (equal median, smaller variance, matches official recipe).
- **R4 (thinking-mode full table):** both models thinking on, `max_tokens 16384`, `qwen3_coder`, NF at 1M YaRN factor 4. 11/11 categories passed for NF; wall 3/3; perf 4/4. Δ own +3.8. Verdict: candidate/win. c7-agentic-if 91.7 vs 90 (median of 5 runs), gate ≥85.0. Tightest pass: c10 70 vs gate 66.7 (non-critical).
- **R5 (c7a per-sub-category, non-thinking):** 30 questions × 2 = 60 max, both models, 3 runs. The gap is mainly restraint-shaped (Restraint 2/4 vs 4/4, Parameter 3/6 vs 5/6, Error-Recovery 17–20/24 vs 22/24; Multi-Step Chains identical 6/6); totals 51/48/49 (NF) vs 57/57/57 (DSV4F). The three restraint-type questions that scored zero in every non-thinking run score full marks in thinking mode.
- **R7 (same questions under thinking mode):** thinking on + official thinking sampling. Thinking mode flips the three restraint-type questions that scored zero in every non-thinking run to full marks. Wall per run (serial sum of 30): NF thinking 308–364 s, DSV4F thinking 330–365 s.
- **R8 (reasoning-effort ladder, c7a × 3, NF):** thinking on + official sampling, three effort levels. On this category the three effort levels tied (91.7 median each); we chose low for the fast tier and medium for the quality tier; other categories were not re-run per effort level.

Thinking-mode gates are recomputed from the thinking-mode baseline (critical categories use baseline minus 5 points, other categories baseline minus 10 points), which is why the c7a gate is ≥85.0 there vs ≥90.0 in non-thinking mode. own-mean = mean of the 8 non-pack categories in percentage points.

Two stated source disagreements are reproduced unchanged (not reconciled): these are different runs taken on different days; on this 30-question category one question is 3.3 points, so three-run medians can differ by 5–10 points between sessions — (i) the no-async c7a median is recorded as 91.7 in the isolation note and 81.7 in the same-condition full-table re-adjudication, and the decision used the 81.7 full-table value (R1); (ii) thinking-mode per-run wall is 81–97 s in the candidate-fixes table (R2) vs 308–364 s per run in R7.

## What did not work

- **Restraint system prompt (three hard rules):** zero effect on NF — 81.7/81.7/78.3 (median 81.7), identical to baseline non-thinking greedy 85/80/81.7 (median 81.7); on DSV4F the median was unchanged (95) with one lower run (91.7). Recorded verdict: ✗.
- **Each vendor's official non-thinking sampling** (DSV4F t1.0/top_p0.95; NF t0.7/top_p0.8/top_k20/rep_pen1.5): no median improvement in three runs; larger spread — NF 76.7/81.7/85 (median 81.7, same as baseline) — and it hurt the control: DSV4F 95/81.7/88.3 (median 88.3, down from 95/95/95). Recorded verdict: ✗.
- **Framework-layer tool-loop guardrails (deny-and-retry guard):** not applicable in the measured failure shape — NF produced zero engine errors and chose a *different* tool at each extra step, so retry-cap guards never triggered. Recorded verdict: ✗.
- **`--no-async-scheduling` fixes the engine, not the gate:** it eliminated runaway loops (0/120; wall back to 48–52 s from 212–217 s) but the non-thinking c7a gate still failed (81.7 vs ≥90), so the original negative verdict stood on c7a alone.
- **Switching adjudication basis:** moving from non-thinking to thinking moved *both* models' scores and the derived gates (e.g., c7a gate ≥90.0 → ≥85.0; c9 100.0 → 82.3 for DSV4F), so single-sided comparisons across settings are meaningless — both sides must be rerun in one setting.
- **YaRN factor 2 / KV bf16 / indexer / MTP off:** the engine-shape levers were tested in a separate A/B and are out of scope here; see `dell-pro-max-gb10-qwen3.8-flash-next-engine-ab`.

## Pitfalls

Symptom → root cause → fix → how we found it, in [docs/pitfalls.md](docs/pitfalls.md). Summary: a measurement-setting gap mistaken for a model defect; mistaking it for an engine bug; confounding parser and sampling; non-comparable wall-clock aggregations; and switching adjudication basis.

## Related cookbooks

- `dell-pro-max-gb10-qwen3.8-flash-next-1m-context` — the 1M-context build recipe and the MTP-draft `max_model_len` discovery.
- `dell-pro-max-gb10-vllm-mtp-async-runaway` — the async-scheduling × MTP runaway-loop isolation table and root-cause paragraph (the loop fixed with `--no-async-scheduling` before this investigation started).
- `dell-pro-max-gb10-qwen3.8-flash-next-engine-ab` — the engine-shape A/B (native 262K / YaRN factor 2 / KV bf16 / indexer / MTP off).

## Footnote on how the vendor measured agentic scores

The model card footnote states that every published agentic score was taken in the vendor's agentic harness (named in the card), at temp 1.0 / top_p 0.95, 256K context, with thinking on by default at reasoning effort xhigh. Our rule-v3 gate ran at the opposite setting (non-thinking, greedy, a different parser). Aligning to the card's setting — not changing the model — is what closed the gap.

## Files

- `README.md` — this document.
- `docs/results.md` — the R1–R8 tables, with a one-line note of the measurement conditions above each table.
- `docs/pitfalls.md` — the pitfalls expanded (symptom / root cause / fix / how we found it).
- `docs/make_banner.py` — banner generator, pure PIL (house style); change only the wordmark/tagline strings to fit this cookbook.
- `docs/assets/banner.png` — the rendered banner (generated by `docs/make_banner.py`).

## License

Apache-2.0.
