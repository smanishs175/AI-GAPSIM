# AI-GAPSIM Frontend Tests

This directory contains tests for the AI-GAPSIM frontend.

## Test Structure

The tests are organized as follows:

```
__tests__/
├── components/         # Component tests
│   ├── auth/           # Authentication component tests
│   ├── map/            # Map component tests
│   └── ui/             # UI component tests
├── pages/              # Page component tests
├── store/              # Store tests
└── utils/              # Utility function tests
```

## Running Tests

To run the tests, use the following command from the frontend directory:

```bash
npm test
```

To run tests with coverage:

```bash
npm test -- --coverage
```

## Writing Tests

When writing tests, follow these guidelines:

1. Use descriptive test names that clearly indicate what is being tested.
2. Test both success and failure cases.
3. Mock external dependencies like API calls.
4. Test user interactions using React Testing Library.
5. Keep tests focused on a single behavior.

## Continuous Integration

Tests are automatically run as part of the CI/CD pipeline defined in `.github/workflows/ci.yml`. The pipeline will fail if any tests fail or if the coverage drops below a certain threshold.
