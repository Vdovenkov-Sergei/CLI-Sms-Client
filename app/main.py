import argparse
import json
import logging
import socket

import toml
from request import HTTPRequest
from response import HTTPResponse
from rich.console import Console
from rich.table import Table

BUFF_SIZE = 4096
CONFIG_FILENAME = "config.toml"

console = Console()

logging.basicConfig(
    filename="sms-log.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger()


def send_sms(
    api_url: str,
    username: str,
    password: str,
    sender: str,
    recipient: str,
    message: str,
) -> HTTPResponse:
    logger.info("Sending SMS...")

    _, host_port_path = api_url.split("://", 1)
    host_port, path = host_port_path.split("/", 1)
    host, port = host_port.split(":", 1)
    path = "/" + path

    auth = (username, password)
    body = (
        f'{{"sender": "{sender}", "recipient": "{recipient}", "message": "{message}"}}'
    )

    request = HTTPRequest("POST", host, path, auth=auth, body=body)

    logging.info(f"Request: {request.request_line}")
    logger.debug(f"Request Body: {request.body}")

    with socket.create_connection((host, int(port))) as sock:
        sock.sendall(request.to_bytes())
        response_data = sock.recv(BUFF_SIZE)

    response = HTTPResponse.from_bytes(response_data)

    logger.info(f"Response: {response.status_line}")
    logger.debug(f"Response Body: {response.body}")
    return response


def main() -> None:
    logger.info("Starting SMS sending process...")

    config = toml.load(CONFIG_FILENAME)

    parser = argparse.ArgumentParser(description="CLI for sending SMS")
    parser.add_argument(
        "--from", dest="sender", required=True, help="Sender phone number"
    )
    parser.add_argument(
        "--to", dest="recipient", required=True, help="Recipient phone number"
    )
    parser.add_argument("--message", required=True, help="SMS message text")
    args = parser.parse_args()

    response = send_sms(
        api_url=config["api_url"],
        username=config["username"],
        password=config["password"],
        sender=args.sender,
        recipient=args.recipient,
        message=args.message,
    )

    table = Table(title="\nSMS Response", show_header=True, header_style="cyan")
    status_style = "green" if response.status_code < 400 else "red"
    table.add_column("Status Code", style=status_style)
    table.add_column("Response Body", style="yellow")

    try:
        formatted_body = json.dumps(json.loads(response.body), indent=2)
    except json.JSONDecodeError:
        formatted_body = response.body

    table.add_row(str(response.status_code), formatted_body)

    console.print(table)
    logger.info("SMS sending process completed.")


if __name__ == "__main__":
    main()
