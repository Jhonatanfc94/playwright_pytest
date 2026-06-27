---
trigger: always_on
---

# Rules for Pytest-BDD Step Definitions

When working with End-to-End tests, follow this structure:

1. Always import `scenarios`, `given`, `when`, `then`, and `parsers` from `pytest_bdd`.
2. Use the `shared_data` fixture (a dictionary) to pass state and dynamic data between different steps.
3. Never directly instantiate POM classes within logical tests without passing them through `shared_data` or a dedicated fixture.
4. All sensitive data or base URLs must be consumed from environment variables (`os.getenv`).
