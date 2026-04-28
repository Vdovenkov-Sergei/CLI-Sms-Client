"""Entry point for the SMS CLI client."""

import sys

from app.config import Config
from app.exceptions import SMSClientError
from app.http.client import Request
from app.http.schemas import SMSMessage
from app.utils.cli import get_parser
from app.utils.console import ResponseConsole
from app.utils.logging import get_logger

logger = get_logger()


def main() -> None:
    """Reads config, parses CLI args, sends an SMS, and prints the response."""
    console = ResponseConsole()
    try:
        config = Config("config.toml")
        api_url = config.get("api_url")
        username, password = config.get("username"), config.get("password")

        parser = get_parser()
        args = parser.parse_args()

        logger.info("Sending SMS...")
        sms_message = SMSMessage(args.sender, args.recipient, args.message)
        response = Request.post(api_url, auth=(username, password), body=sms_message)
        logger.info("SMS sent successfully.")
        console.print("SMS Response", response)

    except SMSClientError as err:
        logger.error(f"SMS client error: {err}")
        sys.exit(-1)


if __name__ == "__main__":
    main()
