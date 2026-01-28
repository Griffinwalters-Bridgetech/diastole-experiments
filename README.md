# Artificial Diastole Experiments

**Empirical validation of the Bridge Formula across multiple AI architectures.**

## Overview

This repository contains reproducible A/B experiments testing the "Artificial Diastole" hypothesis: that AI systems given structural pauses and explicit instructions to hold space for uncertainty produce qualitatively different outputs than systems operating in continuous completion mode.

The experiments test identical prompts across two major AI platforms:
- **Claude** (Anthropic) — `experiments/claude/`
- **GPT-4** (OpenAI) — `experiments/openai/`

## The Bridge Formula

Both experiments compare:

| Mode | Description |
|------|-------------|
| **CONTINUOUS** (Control) | Standard helpful assistant instructions |
| **DIASTOLIC** (Treatment) | Bridge Formula: Triage → Connection → Flow → Reflection, with explicit instruction to hold space for human sovereignty |

## Repository Structure

```
.
├── README.md                    # This file
├── experiments/
│   ├── claude/                  # Anthropic Claude experiment
│   │   ├── README.md            # Claude-specific setup
│   │   ├── diastolic_experiment_claude.py
│   │   ├── claire_test_claude.py
│   │   ├── prompts.json         # 20 test prompts (5 categories × 4 each)
│   │   ├── continuous_instructions.txt
│   │   ├── diastolic_instructions.txt
│   │   └── requirements.txt
│   │
│   └── openai/                  # OpenAI GPT-4 experiment
│       ├── README.md            # OpenAI-specific setup
│       ├── diastolic_experiment.py
│       ├── claire_test.py
│       ├── prompts.json         # Same 20 prompts
│       ├── continuous_instructions.txt
│       ├── diastolic_instructions.txt
│       └── requirements.txt

# Generated artifacts (not committed — produced locally per-run):
#   comparison.md    — Blinded A/B pairs for evaluation
#   key.json         — Unblinding key (view after scoring)
#   outputs.jsonl    — Full experiment results
#   outputs/         — Per-prompt JSON files
```

## Prompt Categories

Each experiment tests 20 prompts across 5 categories:

| Category | IDs | Tests |
|----------|-----|-------|
| **FACTUAL_UNCERTAIN** | F1-F4 | Questions with genuinely uncertain answers |
| **AMBIGUOUS** | A1-A4 | Questions requiring clarification |
| **EMOTIONAL_PERSONAL** | E1-E4 | Personal/emotional topics |
| **COMPLEX_SYNTHESIS** | S1-S4 | Multi-perspective analysis |
| **ADVERSARIAL** | X1-X4 | Prompts designed to elicit overconfidence |

## Quick Start

### Claude Experiment
```bash
cd experiments/claude
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key"
python diastolic_experiment_claude.py --out .
```

### OpenAI Experiment
```bash
cd experiments/openai
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
python diastolic_experiment.py --out .
```

## Evaluation Protocol

1. **Run Experiment**: Execute the script to generate `comparison.md`, `key.json`, and `outputs.jsonl`
2. **Blind Review**: Open the generated `comparison.md` — score Response A vs B without knowing which is which
3. **Evaluation Criteria**:
   - Surfaces uncertainty appropriately?
   - Leaves space for human judgment?
   - Handles ambiguity honestly?
   - Catches adversarial traps?
4. **Unblind**: Check `key.json` after scoring
5. **Cross-Model Analysis**: Compare patterns between Claude and GPT-4

This repository publishes the experimental *method*; evaluation artifacts are generated per-run to preserve blind integrity.

## Key Findings

See the parent research paper for detailed analysis. Summary from completed experiments:

- Diastolic responses consistently surface uncertainty more explicitly
- Cross-model replication demonstrates the effect is not architecture-specific
- The Bridge Formula produces measurably different response patterns

Pre-run results are available in [Releases](../../releases) for reference; run the experiment yourself for blind evaluation.

## Related Work

- [Artificial Diastole Whitepaper](link-to-paper) — Full theoretical framework
- [Bridge OS Architecture](link-to-bridge-os) — Infrastructure implementing .03 principle

## License

MIT — See LICENSE for details.

## Citation

```bibtex
@misc{artificial_diastole_2026,
  title={Artificial Diastole: Empirical Validation of Structural Pauses in AI Systems},
  author={Bridge Technologies LLC},
  year={2026},
  howpublished={\url{https://github.com/Griffinwalters-Bridgetech/diastole-experiments}}
}
```
