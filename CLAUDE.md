# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**jinja2-component-macros** is a Python package that provides a Jinja2 extension for converting HTML tags into Jinja macro calls. It allows developers to write component-like HTML that gets preprocessed into proper Jinja macro invocations.

## Core Architecture

The main implementation of the Jinja extension is in `src/jinja2_component_macros/jinja.py` containing:

- **ComponentsExtension**: A Jinja2 Extension that preprocesses templates to convert HTML-like component tags into macro calls
- **Regex-based preprocessing**: Uses multiple compiled regex patterns to identify and transform:
  - Macro definitions (`{% macro ... %}`)
  - Import statements (`{% from ... import ... %}`)
  - Component tags (`<ComponentName>` → `{% call ComponentName() %}`)
  - Attributes handling with proper escaping and parameter conversion

An additional module `src/jinja2_component_macros/helpers.py` contains:
- **Helper functions** (automatically registered as Jinja globals/filters):
  - `jcm_attr()`: Converts dictionaries to HTML attribute strings with proper escaping and handling some special cases
  - `classx()`: Joins CSS classes conditionally, similar to the `clsx` library in JavaScript

## Key Implementation Details

### Tag Transformation Logic
- **Self-closing tags** (`<Component />`) → `{{ ComponentName() }}`
- **Container tags** (`<Component>...</Component>`) → `{% call ComponentName() %}...{% endcall %}`
- **Attribute handling**: Converts HTML attributes to macro parameters, with special handling for parameter names not valid in macro arguments (stored in `_` key)
- **Quote semantics**: Double quotes = strings, single quotes/unquoted = expressions

### File Structure
```
src/jinja2_component_macros/
├── __init__.py          # Public API exports (ComponentsExtension)
├── jinja.py             # Main extension
├── helpers.py           # Helper functions
└── py.typed             # Type hints marker

tests/
├── test_helpers.py      # Tests for helper functions
└── test_components.py   # Tests for the extension
```

## Development Commands

This project uses **uv** for dependency management and **just** for task running. All commands should be run via `just`:

### Essential Commands
- `just bootstrap` - Set up development environment (installs uv, tox, pre-commit)
- `just install` - Install project dependencies with all groups included
- `just test` - Run tox test suite to test on all configured python versions
- `just pr-checks` - Run all PR validation (format, lint, types, tests)

### Testing & Quality
- `just test <file.whl> <env> [args]` - Run tests with optional pytest arguments, using specific wheel and tox env
- `just check-format` - Verify code formatting with ruff
- `just fix-format` - Auto-fix code formatting
- `just check-lint` - Run linting checks
- `just fix-lint` - Auto-fix linting issues
- `just check-types` - Run mypy type checking
- `just check-coverage` - Combine coverage results from tox runs and check the coverage %

### Development Workflow
- `just run <command>` - Execute any command in the project's virtual environment
- `just update` - Update dependencies and lock file
- `just bump [patch|minor|major]` - Bump version (defaults to patch)

## Testing Framework

Uses **pytest** with these key features:
- Tests in `tests/test_helpers.py` cover the helper functions
- Tests in `tests/test_components.py` cover the core transformation logic
- Uses `jinja2.DictLoader` for in-memory template testing
- Tests cover both container and self-closing tag scenarios
- Tests validate attribute handling for strings, integers, and objects
- Quote handling tests ensure proper string vs expression semantics

## Dependencies

### Runtime
- `jinja2>=3.1.0` - Core template engine

### Development Groups
- **testing**: pytest>=8.3.3 with plugins (github-actions-annotate-failures, randomly, xdist, cov)
- **linting**: ruff>=0.12.0 for code formatting and linting
- **type-checking**: mypy>=1.13.0 for static type analysis (includes testing group)

### Build System
- Uses `uv_build>=0.8.5,<0.9.0` as build backend
- Project version follows calendar versioning (e.g., "2025.1")

## Configuration Files

- **pyproject.toml**: Project metadata, dependencies, and tool configuration
- **justfile**: Task definitions for development workflow
- **uv.lock**: Locked dependency versions
- **tox.ini**: Multi-environment testing configuration (py310-py314, mypy)
