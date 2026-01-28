# Artificial Diastole Experiment (v0.1.0)

This package runs a clean A/B experiment:

- **Control**: CONTINUOUS mode (neutral instructions)
- **Treatment**: DIASTOLIC mode (Bridge Formula: Triage → Connection → Flow → Reflection + explicit holding space)

It saves:
- raw per-prompt JSON outputs (`outputs/continuous`, `outputs/diastolic`)
- a lean `outputs.jsonl` (one record per prompt per mode, without raw API response)
- `comparison.md` (blinded side-by-side pairs for evaluation)
- `key.json` (unblinding key)

## Prereqs

- Python 3.10+
- OpenAI Python SDK
- OpenAI API key in environment

Install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade openai
export OPENAI_API_KEY="YOUR_KEY"
```

## Run

From this folder:

```bash
python diastolic_experiment.py --out .
```

Optional controls:

```bash
# pin model / temperature
DIASTOLIC_MODEL="gpt-4.1" DIASTOLIC_TEMPERATURE="0.2" python diastolic_experiment.py --out .

# add a small sleep between calls to reduce rate-limit risk
python diastolic_experiment.py --out . --sleep 0.2
```

## Review workflow

1. Open `comparison.md` and score Response A vs Response B per prompt.
2. Once scoring is complete, open `key.json` to reveal which was continuous vs diastolic.
3. Summarize results by category (factual / ambiguous / emotional / synthesis / adversarial).
