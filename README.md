# SMS CLI Client

This is a command-line tool for sending SMS messages via an API. It supports configuration via a `TOML` file, logs requests and responses, and provides a user-friendly console output using `rich`.

## Installation and Configuration

1. Clone the repository: `git clone <repository-url>`
2. Create a virtual environment and install dependencies: `poetry install --no-root`
3. Configure the application by creating a `config.toml` file in the root directory:
   ```toml
   api_url = "http://localhost:4010/send_sms"
   username = "your_username"
   password = "your_password"
   ```

## Running the Application

To run the program, use the following command:

```sh
make run SENDER="Sender" RECIPIENT="Recipient" MESSAGE="Message"
```

You need to provide three arguments:
- `SENDER`: The sender's phone number.
- `RECIPIENT`: The recipient's phone number.
- `MESSAGE`: The content of the SMS message

This command will send the specified SMS from the sender to the recipient.

### Example Output
```
+-------------+-----------------------------------------------+
| Status Code | Response Body                                 |
+-------------+-----------------------------------------------+
| 200         | {"status": "success", "message_id": "123456"} |
+-------------+-----------------------------------------------+
```

## Makefile commands

The `Makefile` provides additional commands for convenience:
- `make test` to execute the test suite using `pytest`.
- `make format` to format the code using `black` and `isort`.
- `make lint` to run `ruff` and `mypy` to check for code issues.
- `make clean` to remove cache files and temporary build artifacts.

## Logging

All requests and responses are logged to `sms-log.log`. You can view logs using:

```sh
tail -f sms-log.log
```
