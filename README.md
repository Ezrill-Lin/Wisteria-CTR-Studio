Silicon Sampling CTR Demo

Overview
- Generates synthetic identities from a configurable identity bank JSON.
- Queries an LLM to predict binary clicks (1/0) for a given advertisement.
- Computes CTR from the predictions and optionally saves detailed results.

Files
- `data/identity_bank.json`: Identity category definitions and sampling distributions.
- `sampler.py`: Sampling utilities to generate identities.
- `llm_click_model.py`: LLM predictor with a mock fallback for offline use.
- `demo.py`: CLI entry point to run experiments and compute CTR.

Quick Start
1) Create/activate a Python 3.10+ environment.
2) (Optional) Install `openai` if you want real LLM calls:
   - `pip install openai`
3) Run with mock LLM (no network required):
   - `python demo.py --ad "Special 0% APR credit card offer for travel rewards" --population-size 1000 --use-mock --out results.csv`
   - Outputs CTR and saves per-identity predictions in `results.csv`.

Real LLM Calls (optional)
- Set `OPENAI_API_KEY` in your environment, or pass `--api-key`.
- Example:
  - `setx OPENAI_API_KEY "<your_key>"` (Windows, new shell required)
  - `python demo.py --ad "Affordable health insurance plans" --population-size 500 --model gpt-4o-mini --batch-size 50 --out results.csv`

Notes
- The program samples identities according to distributions in `data/identity_bank.json`.
- Region is stored as a string `City, ST`.
- Health status includes an `illness` field only when `health_status` is true.
- The mock predictor uses a heuristic over ad keywords and identity attributes for reproducible results.

CLI Options
- `--ad`: The advertisement text to evaluate.
- `--population-size`: Number of identities to sample.
- `--identity-bank`: Path to the identity bank JSON (default `data/identity_bank.json`).
- `--seed`: Random seed for reproducibility (default `42`).
- `--provider`/`--model`: LLM provider/model (OpenAI by default).
- `--batch-size`: Profiles per LLM call (default `50`).
- `--use-mock`: Force mock predictions (recommended without network/API key).
- `--api-key`: Override provider API key.
- `--out`: Optional CSV output path for detailed results.

