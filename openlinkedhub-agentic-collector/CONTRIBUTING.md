# Contributing guide

Thank you for your interest in contributing to the OpenLinkedHub Agentic Collector! This project aims to provide a reliable, open-source data ingestion stack for Vietnam's digital transformation ecosystem. Contributions of code, documentation, and datasets are welcome.

## Development workflow

1. Fork the repository and clone your fork.
2. Create a feature branch (`git checkout -b feature/my-update`).
3. Install dependencies with `pip install -r requirements.txt`.
4. Run tests with `pytest` and lint if available.
5. Commit with clear messages and open a pull request describing your changes, including affected data sources.

## Coding standards

- Follow Python best practices and PEP 8.
- Prefer type hints and docstrings for public functions.
- Do not wrap imports in try/except blocks.
- Keep Scrapy spiders deterministic and respect robots.txt.

## Testing

- Provide unit tests for new features or bug fixes.
- Tests should not rely on external network calls; use fixtures or mocked responses.

## Release process

1. Update `CHANGELOG.md` with a summary of changes.
2. Bump version constants if applicable.
3. Tag the release (`git tag vX.Y.Z`) and push tags.

## Code of conduct

By participating you agree to abide by the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).
