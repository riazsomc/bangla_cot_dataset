# Bangla CoT Dataset — Record Schema (v1.0)

Every record is one JSON object on one line of `data/cot_bangla.jsonl` (UTF-8, no BOM).
Records are append-only. IDs are never reused. Retired records keep their line with
`"status": "retired"` — never delete.

Run `python3 scripts/validate_cot.py data/cot_bangla.jsonl` before every commit.
A commit that fails validation must not be merged.

## Fields

| Field | Type | Required | Rules |
|---|---|---|---|
| `id` | string | yes | `bn-cot-NNNNNN`, zero-padded, monotonic, never reused |
| `domain` | string | yes | One of the controlled vocabulary below |
| `register` | string | yes | `cholito` \| `sadhu` \| `mixed` — register of the *reasoning text*. Reasoning is written in cholito unless the item is specifically about sadhu text |
| `difficulty` | integer | yes | 1–5, honest calibration (see guide below) |
| `question` | string | yes | Self-contained; answerable using only `question` + `context` |
| `context` | string \| null | yes (nullable) | Passage/table the question depends on. **Self-contained** — no external references. Must be original or paraphrased text, never verbatim rights-reserved material |
| `reasoning_steps` | array | yes | ≥2 steps; each `{"step": n, "type": t, "text": s}`; numbering sequential from 1 |
| `reasoning_steps[].type` | string | yes | `recall` \| `deduce` \| `calculate` \| `eliminate` \| `verify` |
| `final_answer` | string | yes | Canonical, short, gradable without reading the reasoning |
| `answer_type` | string | yes | `numeric` \| `mcq` \| `short_text` \| `yes_no` |
| `wrong_paths` | array | yes | ≥1 entry; each `{"answer": a, "error": e}` — a *plausible* wrong answer and one sentence naming which step breaks and why |
| `author` | string | yes | Handle of the human who authored or corrected the item. Must be truthful. AI-drafted seed items use `claude-seed` |
| `drafted_by` | string | no | If an AI drafted and a human corrected: the drafting model (e.g. `qwen2.5-14b-local`). `author` is then the human corrector |
| `status` | string | no | `active` (default) \| `retired` |
| `license` | string | yes | `CC-BY-4.0` (this repository accepts no other license) |
| `created` | string | yes | `YYYY-MM-DD` |

## Controlled vocabulary: `domain`

`public_health` · `law` · `math` · `civics` · `linguistics` · `general_science` ·
`daily_reasoning` · `document_reasoning` · `misinformation_rebuttal`

Adding a domain = one-line change in `scripts/validate_cot.py` **plus** a row here,
in the same commit, with a one-line justification in the commit message.

## Difficulty guide

1. Single recall or one obvious inference
2. Two–three inferences, no traps
3. Requires combining rules/evidence, or resisting one tempting misreading
4. Multi-constraint reasoning with a plausible competing conclusion
5. Expert-level: domain knowledge + multi-step elimination + verification

## Authoring rules

1. **One inference per step.** If a step contains "এবং তাই" doing double duty, split it.
2. **Include a `verify` step** where possible — checking the conclusion against an
   independent fact. The validator warns (not errors) when absent.
3. **Wrong paths must be plausible** — the mistake a smart but careless reader would
   make, not a strawman. Right-answer-wrong-reasoning entries are encouraged.
4. **Contexts are paraphrased, never copied.** Extract the logical structure of a
   source passage and rewrite it in your own words. Verbatim rights-reserved text
   (textbooks, novels, news) is rejected at review regardless of quality.
5. **Reasoning idiom is natural deliberative cholito** — লক্ষ করি, মিলিয়ে দেখি,
   উল্টো দিক থেকে যাচাই করি — not calqued English scaffolding.
6. **Final answers are gradable.** Prefer numeric / mcq / yes_no where the item allows;
   a `short_text` answer must still have one defensible canonical form.
7. **Truthful attribution.** You may use an AI to draft; you must then correct it,
   own the item as `author`, and record the model in `drafted_by`.
