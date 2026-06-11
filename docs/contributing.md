# Contributing to SpaceEye

Thank you for your interest in contributing to SpaceEye! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Commit Messages](#commit-messages)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

Be respectful, constructive, and inclusive. We're building tools for environmental monitoring — the work matters.

## Getting Started

### Prerequisites

- Python 3.12+ with [uv](https://docs.astral.sh/uv/)
- Node.js 20+ with npm
- Docker + docker-compose
- Git

### Setup

```bash
git clone https://github.com/your-org/spaceeye
cd spaceeye
cp .env.example .env
./make setup
./make dev
```

See [Development Guide](./development.md) for detailed setup instructions.

### First Contribution

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `make test`
5. Commit with a descriptive message
6. Push and create a Pull Request

## Development Workflow

### Branch Naming

Use descriptive branch names with prefixes:

| Prefix | Use Case |
|--------|----------|
| `feature/` | New functionality |
| `fix/` | Bug fixes |
| `refactor/` | Code restructuring without behavior change |
| `docs/` | Documentation only |
| `test/` | Adding or updating tests |
| `chore/` | Maintenance tasks |

Examples:
- `feature/vegetation-timeline-chart`
- `fix/health-check-503-status`
- `refactor/split-processing-service`

### Working on Issues

1. Check existing issues before starting work
2. Comment on the issue to indicate you're working on it
3. Create a branch named `feature/issue-123-description`
4. Reference the issue in your PR

## Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] Tests pass (`make test`)
- [ ] No new linting errors (`make lint`)
- [ ] Documentation updated if needed
- [ ] Commit messages follow conventions

### PR Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Refactoring
- [ ] Documentation
- [ ] Test

## Testing
Describe tests added/updated.

## Screenshots (if applicable)
Before/after screenshots for UI changes.

## Related Issues
Closes #123
```

### Review Process

1. All PRs require at least one review
2. Address review comments
3. Squash commits before merging (if requested)
4. Delete branch after merge

## Code Standards

### Python

- **Formatter**: `ruff format`
- **Linter**: `ruff check`
- **Type hints**: Required for all function signatures
- **Async**: Use `async/await` for I/O operations, sync for CPU-bound math
- **Import order**: stdlib → third-party → local (enforced by ruff)

```python
# Good
async def fetch_weather(lat: float, lon: float) -> dict:
    """Fetch weather data from Open-Meteo."""
    client = await get_http_client()
    resp = await client.get(...)
    return resp.json()
```

### TypeScript / Svelte

- **Svelte 5 runes**: Use `$state`, `$derived`, `$effect`, `$props`
- **No `export let`**: Use `$props()` instead
- **TypeScript**: Strict mode enabled
- **Tailwind**: Use utility classes, avoid inline styles

```svelte
<!-- Good -->
<script lang="ts">
  let { value, label }: { value: number; label: string } = $props();
  let doubled = $derived(value * 2);
</script>

<div class="text-sm font-bold">{label}: {doubled}</div>
```

### SQL

- Use uppercase for keywords: `SELECT`, `FROM`, `WHERE`
- Use snake_case for table and column names
- Add comments for complex queries
- Use parameterized queries (never string interpolation)

## Testing Requirements

### Backend Tests

```bash
make test-backend
# or
uv run pytest backend/tests/ -v
```

- Write tests for new endpoints
- Write tests for new domain logic
- Mock external API calls (Open-Meteo, ISRIC, INPE)
- Aim for >80% coverage on new code

### Frontend Tests

```bash
make test-frontend
# or
cd apps/spaceeye-web && npm test
```

- Write tests for new utility functions
- Write tests for store logic
- Test component interactions where critical

### Test File Naming

- Backend: `test_<module>.py` in `backend/tests/`
- Frontend: `<module>.test.ts` in `__tests__/`

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code restructuring |
| `docs` | Documentation |
| `test` | Adding/updating tests |
| `chore` | Maintenance |
| `perf` | Performance improvement |

### Examples

```
feat(vegetation): add NDVI time-series chart with anomaly markers
fix(health): return 503 when database is disconnected
refactor(api): split router.py into domain-specific modules
docs(api): update endpoint reference for new ESG endpoints
test(backend): add integration tests for soil zonal stats
```

### Scopes

| Scope | Description |
|-------|-------------|
| `api` | Backend API routes |
| `backend` | Backend core |
| `frontend` | Frontend core |
| `dashboard` | Dashboard page |
| `modules` | ESG modules |
| `db` | Database schema |
| `docs` | Documentation |

## Reporting Issues

### Bug Reports

Include:
1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Environment (OS, browser, Python version)
5. Screenshots if applicable

### Feature Requests

Include:
1. Problem statement (what need does this address?)
2. Proposed solution
3. Alternatives considered
4. Use cases

### Security Issues

Report security vulnerabilities privately to [security@spaceeye.dev](mailto:security@spaceeye.dev). Do not open public issues for security bugs.

## Architecture Decisions

For significant architectural changes:

1. Open an issue discussing the change first
2. Get approval from maintainers
3. Create an Architecture Decision Record (ADR) in `docs/adr/`
4. Implement in a feature branch
5. Submit PR with ADR link

## Questions?

- Open a discussion on GitHub
- Check existing documentation in `docs/`
- Review the [Architecture](./architecture.md) doc
