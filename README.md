# The Balanced Books Challenge

The Balanced Books Challenge is a student-facing Streamlit activity in which students follow one fictional business from economic events through transaction analysis and the preparation of financial statements.

## Learning flow

1. **Transaction Inbox** — distinguish accounting transactions from events that do not yet affect the accounts.
2. **Equation Lab** — identify the dual effect of ten introductory business transactions.
3. **Statement Builder** — drag correct account balances into a multi-step income statement, retained earnings calculation, and classified balance sheet while totals update live.
4. **Debrief** — trace how accounting information moves from source events to financial statements.

The app uses one approachable first-month case and provides item-level feedback after every submission. It does not collect, store, or transmit student names or responses.

## Project structure

```text
.
├── .github/workflows/tests.yml
├── .streamlit/config.toml
├── balanced_books/
│   ├── __init__.py
│   ├── case_data.py
│   ├── engine.py
│   ├── scroll_to_top_frontend/index.html
│   ├── statement_builder_component.py
│   └── statement_builder_frontend/index.html
├── tests/
│   └── test_engine.py
├── .python-version
├── requirements.txt
└── streamlit_app.py
```

## Run locally

Python 3.12 is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open `http://localhost:8501`.

## Run tests

```bash
python -m unittest discover -s tests -v
python -m py_compile streamlit_app.py balanced_books/*.py
```

## Deployment

- **Live app:** [the-balanced-books-challenge.streamlit.app](https://the-balanced-books-challenge.streamlit.app/)
- **Source:** [github.com/cybercrs/the-balanced-books-challenge](https://github.com/cybercrs/the-balanced-books-challenge)

Streamlit Community Cloud deploys the `main` branch using `streamlit_app.py` as the entrypoint. No secrets or external services are required. The included GitHub Actions workflow runs the unit tests and compiles the application on pushes and pull requests.

## Visual direction

The interface uses a logo-free red, blue, and white visual system inspired by the University of Dayton. It does not bundle or alter an official university logo.
