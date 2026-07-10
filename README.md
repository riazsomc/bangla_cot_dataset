# বাংলা Chain-of-Thought ডেটাসেট / Bangla Chain-of-Thought Dataset

Native, human-authored Bangla reasoning data: questions paired with explicit
step-by-step reasoning traces, verifiable answers, and annotated wrong paths.

## Why this exists

Bangla is spoken by over 230 million people yet holds a vanishingly small share
of web text, and almost none of that text *reasons out loud*. Newspapers assert,
literature narrates, laws declare — step-by-step deliberative prose barely exists
as a written genre. Models fine-tuned on machine-translated English CoT reason in
a Bangla that reads like dubbed audio: the connective tissue of thought comes out
as calqued English scaffolding.

This dataset is an attempt to author that missing genre directly: reasoning
written natively in Bangla, grounded where possible in Bangladeshi domains
(public health, law, civics, language), with process-level annotation that
supports supervised fine-tuning, preference training, verifier training, and
evaluation from the same records.

Everything here is legally clean by construction: contexts are original or
paraphrased, authorship is truthful and per-record, and the entire dataset is
CC BY 4.0. Rights-reserved text is rejected at review, regardless of quality.

## What a record contains

Each line of `data/cot_bangla.jsonl` is one item:

- a self-contained **question** (plus optional **context** passage)
- **reasoning_steps** — atomic, typed inferences
  (`recall` / `deduce` / `calculate` / `eliminate` / `verify`)
- a canonical, gradable **final_answer**
- **wrong_paths** — plausible incorrect answers, each with one sentence naming
  which step breaks and why (usable as preference pairs and hard distractors)
- provenance: `author`, optional `drafted_by`, `license`, `created`, `status`

Full field specification and authoring rules: [SCHEMA.md](SCHEMA.md).

## Usage

```python
from datasets import load_dataset
ds = load_dataset("json", data_files="data/cot_bangla.jsonl", split="train")
```

Filter AI-drafted seed items from human-authored ones:

```python
human = ds.filter(lambda r: r["author"] != "claude-seed")
```

## Contributing

1. Read [SCHEMA.md](SCHEMA.md), especially the authoring rules.
2. Write your item(s); append as single-line JSON records.
3. Run the gate — it must pass clean:

   ```bash
   python3 scripts/validate_cot.py data/cot_bangla.jsonl
   ```

4. Open a pull request. Review checks three things: schema validity,
   reasoning correctness, and provenance (no verbatim rights-reserved text,
   truthful `author`).

Contributions of *effort* are what this project runs on: authoring items in
your domain of expertise, correcting AI drafts, reviewing others' reasoning.
Contributions of copied text are out of scope by charter.

## Status

Actively growing. Every item passes the same gate before commit: human review,
correction, and finalization against the authoring rules in SCHEMA.md. Records
drafted with AI assistance carry a `drafted_by` field alongside the human
`author` — drafting history is never erased, so downstream users can weight
or filter on it:

```python
ai_assisted = ds.filter(lambda r: "drafted_by" in r and r["drafted_by"])
```

## License

Data: [CC BY 4.0](LICENSE) · Scripts: Apache 2.0
