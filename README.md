# PyTasky

PyTasky is a Pomodoro time management application built with Python to help you organize and complete your tasks efficiently.

## Features
- Customizable Pomodoro timer
- Short (5m) and long (15m) break options
- Task management with title, notes, and tags
- SQLite database for task persistence
- Task report generation in JSON and CSV formats
- About page with version information
- Cross-platform support (Windows, Linux, Mac)

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/<your-username>/pytasky.git
   cd pytasky
   ```
2. Install uv (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   Or use your package manager (e.g., `brew install uv` on macOS).
3. Initialize a virtual environment and install dependencies:
   ```bash
   uv init
   uv add pyinstaller pytest black pylint coverage pre-commit
   ```
4. Activate the virtual environment:
   - On Unix/Linux/Mac:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
5. Run the app:
   ```bash
   python src/pytasky.py
   ```

## Development

Developed by Elephanta Technology and Design Inc.

### Development Commands

- **Initialize Project and Install Dependencies**:
  ```bash
  uv init
  uv add pyinstaller pytest black pylint coverage pre-commit
  ```
  Initializes a virtual environment and installs all dependencies.

- **Run the Application**:
  ```bash
  uv run python src/pytasky.py
  ```
  Runs the PyTasky application using uv (no need to activate the venv manually).

- **Run Tests**:
  ```bash
  uv run pytest
  ```
  Executes all unit tests in the `tests/` directory.

- **Check Test Coverage**:
  ```bash
  uv run coverage run -m pytest && uv run coverage report
  ```
  Runs tests and generates a coverage report. Add `--fail-under=80` to enforce a minimum coverage.

- **Format Code with Black**:
  ```bash
  uv run black .
  ```
  Formats all Python files with Black using a line length of 88.

- **Lint Code with Pylint**:
  ```bash
  uv run pylint src tests
  ```
  Runs Pylint on the source and test files. Customize with a `.pylintrc` file if needed.

- **Install Pre-Commit Hooks**:
  ```bash
  uv run pre-commit install
  ```
  Sets up pre-commit hooks to run automatically on `git commit`.

- **Run Pre-Commit Hooks Manually**:
  ```bash
  uv run pre-commit run --all-files
  ```
  Executes all pre-commit hooks (Black, Pylint, Pytest, Coverage) on all files.

- **Build Executables**:
  ```bash
  chmod +x build_app.sh && ./build_app.sh
  ```
  Generates standalone executables for your platform (run on each target OS). Update `build_app.sh` to use `uv run pyinstaller`.

- **Update Dependencies**:
  ```bash
  uv sync
  ```
  Updates all dependencies to their latest compatible versions based on `pyproject.toml`.

## Pre-commit Hooks
This project uses pre-commit hooks for:
- `black`: Code formatting
- `pytest`: Running tests
- `coverage`: Test coverage reporting
- `pylint`: Code linting

To install hooks: `uv run pre-commit install`

## Releases
Stable releases and their downloadable executables (for Windows, Linux, and macOS) are available on the [GitHub Releases page](https://github.com/<your-username>/pytasky/releases). Check there for the latest version and release notes.

## License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
