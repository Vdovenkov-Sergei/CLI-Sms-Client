import argparse
import socket
import logging

import toml
from app.request import HTTPRequest
from app.response import HTTPResponse


BUFF_SIZE = 4096
CONFIG_FILENAME = "config.toml"

logging.basicConfig(
    filename="sms_sender.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger()


def send_sms(
    api_url: str,
    username: str,
    password: str,
    from_number: str,
    to_number: str,
    message: str,
) -> HTTPResponse:
    logger.info("Sending SMS...")

    _, host_port = api_url.split("://", 1)
    host, port = host_port.split(":", 1)
    path = "/" + __name__

    auth = (username, password)
    body = f'{{"from": "{from_number}", "to": "{to_number}", "message": "{message}"}}'

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
        "--from", dest="from_number", required=True, help="Sender phone number"
    )
    parser.add_argument(
        "--to", dest="to_number", required=True, help="Recipient phone number"
    )
    parser.add_argument("--message", required=True, help="SMS message text")
    args = parser.parse_args()

    response = send_sms(
        api_url=config["api_url"],
        username=config["username"],
        password=config["password"],
        from_number=args.from_number,
        to_number=args.to_number,
        message=args.message,
    )

    print(f"Response Code: {response.status_code}")
    print(f"Response Body: {response.body}")
    logger.info("SMS sending process completed.")


if __name__ == "__main__":
    main()
