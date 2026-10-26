# QA Command Center

A Python test automation framework that tests a real-time web application end to end: UI, REST API, WebSocket and performance, with HTML reporting and a Jenkins CI pipeline.

## What is tested

| Layer | Tools | Target |
|-------|-------|--------|
| UI | Selenium, Pytest, Page Object Model | saucedemo.com (login flows) |
| REST API | Pytest, requests, jsonschema | FastAPI service in `app_under_test/` |
| WebSocket | Pytest, Python websocket client | Python WebSocket chat server in `app_under_test/` |
| Performance | Apache JMeter 5.6.3 | FastAPI service in `app_under_test/` |
| CI | Jenkins (declarative pipeline), GitHub Actions | `Jenkinsfile`, `.github/workflows/ci.yml` |

31 automated tests in total across the UI, API and WebSocket suites.

## Project structure

```
QA-Command-Center/
├── app_under_test/   # WebSocket chat server and FastAPI REST API used as test targets
├── pages/            # Page Object Model classes (LoginPage)
├── tests/            # Selenium UI tests (parametrized)
├── api_tests/        # REST API tests with JSON schema validation
├── ws_tests/         # WebSocket tests
├── performance/      # JMeter test plans
├── conftest.py       # Shared fixtures: browser driver, WebSocket server, screenshot on failure
├── pytest.ini        # Markers and HTML report settings
├── Jenkinsfile       # CI pipeline
└── requirements.txt
```

## Features

- Page Object Model for UI tests, with a shared browser fixture and parametrized login tests.
- Headless browser mode through the `HEADLESS=1` environment variable, used in CI.
- API tests validate status codes, response bodies and JSON schemas.
- The WebSocket chat server is started by a session-scoped fixture on a free port, so the WebSocket tests need no manual setup.
- Pytest markers: `smoke`, `regression`, `ui`, `api`, `websocket`.
- A self-contained HTML report is written to `reports/report.html` on every run, and a screenshot is saved to `reports/screenshots/` when a UI test fails.

## Setup

Requirements: Python 3, Google Chrome, and Apache JMeter 5.6.3 for the load tests.

```bash
git clone https://github.com/adarshpj09/QA-Command-Center.git
cd QA-Command-Center
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the tests

```bash
pytest                      # everything
pytest -m smoke             # quick checks of critical paths
pytest -m ui                # browser tests
pytest -m api               # API tests
pytest -m websocket         # WebSocket tests

HEADLESS=1 pytest           # run the browser without a window (Windows: set HEADLESS=1)
```

## Performance testing

JMeter test plans live in `performance/`. All runs were made against the local FastAPI service, with 0% errors in every run.

| Run | Users | Requests | Throughput | Avg response | 95th percentile |
|-----|-------|----------|------------|--------------|-----------------|
| Baseline | 20 | 3,000 | 311.82 req/s | 1.91 ms | 3 ms |
| Stress | 100 | 30,000 | 1,115 req/s | 58 ms | 91 ms |
| Stress | 300 | 90,000 | 936 req/s | 285 ms | 482 ms |
| Stress | 600 | 180,000 | 998 req/s | 568 ms | 565 ms |

Throughput stops growing at around 1,000 req/s while average response time rises with the number of users. The cause has not been isolated yet. The next step is to compare against multiple server workers.

Start the API, then run a plan in non-GUI mode:

```bash
# TODO: command you use to start the FastAPI service
jmeter -n -t performance/<plan>.jmx -l results.jtl -e -o report/    # TODO: .jmx filename
```

## CI

- **Jenkins:** the `Jenkinsfile` runs on a Windows agent with `HEADLESS=1`. Stages: setup (virtual environment and dependencies), smoke tests, full regression. It publishes JUnit results and archives everything under `reports/`.
- **GitHub Actions:** `.github/workflows/ci.yml` runs the same smoke and full suites on every push.

## Screenshots

TODO: add images to `docs/` and link them here:
- Pytest HTML report
- Jenkins pipeline, green build
- JMeter report dashboard

## Tech stack

Python, Pytest, Selenium, requests, jsonschema, FastAPI, Apache JMeter, Jenkins, GitHub Actions
