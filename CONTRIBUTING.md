# Contributing to Autonomous Spring Boot Documentation Agent

First off, thank you for considering contributing! It's people like you that make this project great.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates.

**When submitting a bug report, include:**
- Clear, descriptive title
- Steps to reproduce the behavior
- Expected vs actual behavior
- Screenshots if applicable
- Environment details (OS, Python version, Node version)
- Error logs

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:
- Clear, descriptive title
- Detailed description of the proposed functionality
- Why this enhancement would be useful
- Examples of how it would work

### Pull Requests

1. **Fork** the repo and create your branch from `main`
2. **Make your changes** following our style guidelines
3. **Test** your changes thoroughly
4. **Update documentation** if needed
5. **Write clear commit messages** (see below)
6. **Submit a pull request**

## Development Setup
```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/springboot-doc-agent.git
cd springboot-doc-agent

# Backend setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Frontend setup
cd springboot-doc-agent-frontend
npm install
cd ..

# Install pre-commit hooks
pre-commit install
```

## Style Guidelines

### Python Code Style

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://github.com/psf/black) for formatting
- Use [pylint](https://pylint.org/) for linting
- Type hints are required for new functions
```bash
# Format code
black .

# Lint code
pylint agents/ tools/ utils/

# Type check
mypy agents/ tools/ utils/
```

### TypeScript/JavaScript Code Style

- Follow the existing code style
- Use ESLint and Prettier
- Functional components with hooks preferred
```bash
# Format and lint
npm run lint
npm run format

# Type check
npm run type-check
```

### Commit Message Format

Use conventional commits:
type(scope): subject
body (optional)
footer (optional)
