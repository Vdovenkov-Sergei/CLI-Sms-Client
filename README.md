# CLI SMS Client

This is a command-line tool for sending SMS messages via an API. It supports configuration via a `TOML` file, logs requests and responses, and provides a user-friendly console output using `rich`.

## Prerequisites

Ensure you have the following installed on your system:
- Python 3.11+
- `make`
- `poetry` package manager

## Setup

1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Create a virtual environment and install dependencies:
   ```sh
   poetry install --no-root
   ```

3. Configure the application by creating a `config.toml` file in the root directory:
   ```toml
   api_url = "http://localhost:4010/send_sms"
   username = "your_username"
   password = "your_password"
   ```

## Running the Application

To send an SMS, use the following command:

```sh
make run FROM="Sender phone number" TO="Recipient phone number" MESSAGE="Your message here"
```

### Example Output
```
+-------------+-----------------------------------------------+
| Status Code | Response Body                                 |
+-------------+-----------------------------------------------+
| 200         | {"status": "success", "message_id": "123456"} |
+-------------+-----------------------------------------------+
```

## Other Commands in Makefile

The `Makefile` provides additional commands for convenience:

- **Run tests**  
  ```sh
  make test
  ```
  Executes the test suite using `pytest`.

- **Format the code**  
  ```sh
  make format
  ```
  Formats the code using `black` and `isort`.

- **Lint the code**  
  ```sh
  make lint
  ```
  Runs `ruff` and `mypy` to check for code issues.

- **Clean the project**  
  ```sh
  make clean
  ```
  Removes cache files and temporary build artifacts.

## Logging

All requests and responses are logged to `sms-log.log`. You can view logs using:

```sh
tail -f sms-log.log
```
