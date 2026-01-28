# Artificial Diastole Experiment — Claude API Version (v0.1.0)

This package runs a clean A/B experiment using the Anthropic Claude API:

- **Control**: CONTINUOUS mode (neutral instructions)
- **Treatment**: DIASTOLIC mode (Bridge Formula: Triage → Connection → Flow → Reflection + explicit holding space)

It saves:
- raw per-prompt JSON outputs (`outputs/continuous`, `outputs/diastolic`)
- a lean `outputs.jsonl` (one record per prompt per mode, without raw API response)
- `comparison.md` (blinded side-by-side pairs for evaluation)
- `key.json` (unblinding key)

## Prerequisites

- Python 3.10+
- Anthropic Python SDK
- Anthropic API key in environment

## Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade anthropic

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"
```

## Files Required

Make sure these files are in the same directory:
- `diastolic_experiment_claude.py` (this script)
- `prompts.json` (the 20 test prompts)
- `continuous_instructions.txt` (neutral control prompt)
- `diastolic_instructions.txt` (Bridge Formula prompt)

## Run

```bash
python diastolic_experiment_claude.py --out .
```

### Optional Controls

```bash
# Specify a different model
python diastolic_experiment_claude.py --model claude-sonnet-4-20250514 --out .

# Adjust temperature
python diastolic_experiment_claude.py --temperature 0.3 --out .

# Increase sleep between calls (if hitting rate limits)
python diastolic_experiment_claude.py --sleep 1.0 --out .

# Use environment variables
DIASTOLIC_MODEL="claude-sonnet-4-20250514" DIASTOLIC_TEMPERATURE="0.2" python diastolic_experiment_claude.py --out .
```

## Output Files

After running, you'll have:

| File | Purpose |
|------|---------|
| `outputs.jsonl` | Lean transcript (one line per prompt per mode) |
| `comparison.md` | Blinded A/B pairs for evaluation |
| `key.json` | Unblinding key (reveals which was continuous vs diastolic) |
| `outputs/continuous/*.json` | Full records for continuous mode |
| `outputs/diastolic/*.json` | Full records for diastolic mode |

## Evaluation Workflow

1. **Blind evaluation**: Open `comparison.md` and score Response A vs Response B for each prompt
   - Which surfaces uncertainty better?
   - Which leaves appropriate space for human judgment?
   - Which handles ambiguity more honestly?
   - Which catches adversarial traps?

2. **Record your scores** before unblinding

3. **Unblind**: Open `key.json` to reveal which was continuous vs diastolic

4. **Analyze**: Summarize results by category:
   - FACTUAL_UNCERTAIN (F1-F4)
   - AMBIGUOUS (A1-A4)
   - EMOTIONAL_PERSONAL (E1-E4)
   - COMPLEX_SYNTHESIS (S1-S4)
   - ADVERSARIAL (X1-X4)

## Cross-Model Comparison

This Claude version uses the same prompts and evaluation framework as the OpenAI version. Run both and compare:

- Do both models show the same pattern?
- Is the diastolic effect consistent across architectures?
- Where do the models differ?

Cross-model replication strengthens the evidence.

## Notes

- Default model: `claude-sonnet-4-20250514`
- Default temperature: `0.2` (low, for reproducibility)
- Default sleep: `0.5s` between calls (rate limiting)
- Blinding uses deterministic hashing — same prompt always gets same A/B assignment for given seed
