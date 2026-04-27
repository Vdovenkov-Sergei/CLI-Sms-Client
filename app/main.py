from app.config import Config
from app.http_client.request import Request
from app.http_client.schemas import SMSMessage
from app.utils.cli_parser import parse_arguments
from app.utils.console import print_json_response


def main() -> None:
    config = Config("config.toml")
    api_url = config.get("api_url")
    username, password = config.get("username"), config.get("password")
    args = parse_arguments()

    sms_message = SMSMessage(args.sender, args.recipient, args.message)
    response = Request.post(api_url, auth=(username, password), body=sms_message)
    print_json_response("SMS Response", response)


if __name__ == "__main__":
    main()
