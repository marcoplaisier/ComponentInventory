# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working in this repository.

## Build and Run Commands
- Run application: `python main.py`
- Run with Docker: `docker build -t component-inventory . && docker run -p 5000:5000 component-inventory`
- Initialize database: `python -c "from main import db; db.create_all()"`
- Run tests: `pytest`
- Run single test: `pytest tests/test_file.py::test_function`
- Lint code: `flake8 .`

## Code Style Guidelines
- **Imports**: Group imports in order: standard library, third-party, local application
- **Formatting**: Follow PEP 8 conventions, 4 spaces for indentation
- **Types**: Use type hints for function parameters and return values
- **Naming**: Use snake_case for functions/variables, PascalCase for classes
- **Error Handling**: Use specific exceptions, properly handle input validation
- **Documentation**: Docstrings for all classes and functions
- **API Endpoints**: Follow RESTful design principles as shown in existing code

## Project Structure
- Flask-based REST API for component inventory management
- SQLAlchemy for database ORM
- SQLite local database in instance/components.db