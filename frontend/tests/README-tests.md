Frontend test instructions (isolated)

1. Change into the test folder and install dev dependencies:

```bash
cd frontend/tests
npm install
```

2. Run the tests:

```bash
npm test
```

Notes:
- Tests are placed in `frontend/tests` so they do not modify the main project.
- These are lightweight render/unit tests using Vitest + Testing Library.
