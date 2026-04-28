# SMS Client

![python](https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white)
![poetry](https://img.shields.io/badge/poetry-2.0+-60A5FA?logo=poetry&logoColor=white)
![isort](https://img.shields.io/badge/isort-imports-EF8336)
![ruff](https://img.shields.io/badge/ruff-lint-D7FF64?logo=ruff&logoColor=black)
![mypy](https://img.shields.io/badge/mypy-typed-2A6DB2)
![pytest](https://img.shields.io/badge/pytest-tested-0A9EDC?logo=pytest&logoColor=white)

A CLI tool for sending SMS messages via an HTTP API. Communicates over raw TCP sockets with a hand-rolled `HTTP/1.1` implementation.

## Installation & Configuration

1. Clone the repository: `git clone <repository-url>`
2. Create a virtual environment and install dependencies: `poetry install --no-root`
3. Configure the application by creating a `config.toml` file in the root directory:
```toml
api_url  = "http://localhost:8888/sms"
username = "your_username"
password = "your_password"
```

| Key        | Type     | Description                      |
|------------|----------|----------------------------------|
| `api_url`  | `string` | Full URL of the SMS API endpoint |
| `username` | `string` | HTTP Basic Auth username         |
| `password` | `string` | HTTP Basic Auth password         |

## Usage

```sh
python -m app.main \
  --sender "+12025550001" \
  --recipient "+12025550002" \
  --message "Hello!"
```

| Argument      | Description            |
|---------------|------------------------|
| `--sender`    | Sender phone number    |
| `--recipient` | Recipient phone number |
| `--message`   | SMS text content       |

Phone numbers must be 10–15 digits, optionally prefixed with `+`.

### Example output

```
               SMS Response               
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Status Code ┃ Response Body            ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 200         │ {                        │
│             │   "status": "success",   │
│             │   "message_id": "123456" │
│             │ }                        │
└─────────────┴──────────────────────────┘
```

## Makefile commands

| Command         | Description                                     |
|-----------------|-------------------------------------------------|
| `make test`     | Run the test suite with `pytest`                |
| `make test-cov` | Run tests with coverage report                  |
| `make format`   | Format code with `black` and `isort`            |
| `make lint`     | Run `ruff` and `mypy`                           |
| `make clean`    | Remove `__pycache__`, coverage, and tool caches |
