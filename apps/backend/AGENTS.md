# Repository Guidelines

## Project Structure & Module Organization
- `src/` contains application code (set as `PYTHONPATH` root).
- `src/main.py` is the FastAPI entrypoint; routes live in `src/api/routes/`.
- Agent orchestration is in `src/agent/` (`graph.py`, `nodes/`, `tools/`).
- Data models are in `src/models/`; database helpers are in `src/db/`; shared utilities are in `src/utils/`.
- Tests live in `tests/` with shared fixtures in `tests/conftest.py`.

## Build, Test, and Development Commands
- `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt` installs dependencies.
- `PYTHONPATH=src venv/bin/uvicorn main:app --reload --port 8000` runs the API locally.
- `docker-compose up --build` starts the API plus MongoDB for local integration.
- `pytest` runs all tests.
- `pytest --cov=src --cov-report=term-missing` shows coverage details.
- `pytest --cov=src --cov-fail-under=80` enforces the CI coverage gate.
- `ruff check src` runs lint checks; `ruff format src` formats code.

## Coding Style & Naming Conventions
- Python 3.12 target, 4-space indentation, max line length `100` (Ruff config).
- Use `snake_case` for modules/functions/variables, `PascalCase` for Pydantic models, and `UPPER_SNAKE_CASE` for constants.
- Keep route handlers thin; place business logic in `agent/`, `db/`, or `utils/`.
- Group imports and keep first-party modules consistent with Ruff isort settings (`models`, `api`, `agent`, `db`, `utils`).

## Testing Guidelines
- Framework: `pytest` with `pytest-asyncio` (`asyncio_mode = auto`).
- Test discovery: files `test_*.py`, classes `Test*`, functions `test_*`.
- Add tests for new routes, agent nodes/tools, and model validation paths.
- Prefer mocking external dependencies (OpenAI, HardCover, Tavily, MongoDB) to keep tests deterministic.

## Commit & Pull Request Guidelines
- Local `.git` history is not available in this workspace snapshot, so no commit pattern could be verified directly.
- Use clear, imperative commit subjects (example: `Add retries for HardCover search timeout`).
- PRs should include: scope summary, test evidence (`pytest`/coverage), env/config changes, and linked issue/ticket.
- Target branch flow follows docs/CI: develop work lands via PR, with `main` used for production-facing merges.

## Security & Configuration Tips
- Copy `.env.example` to `.env`; never commit secrets.
- Keep `APP_ENV=prod` behavior strict: no debug auth bypass headers.
- Validate new config keys in `src/config.py` and document them in `README.md`.

## Collaboration Preference (Approval Before File Changes)
- Before modifying any file, present the proposed diff and wait for explicit user approval.
- Do not edit, create, delete, or overwrite files until approval is given.
- If scope changes after approval, present an updated diff and request approval again.
