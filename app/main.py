from config import config
from http_client.request import Request
from http_client.schemas import PhoneNumber, SMSMessage
from utils.cli_parser import parse_arguments
from utils.console import print_response


def main() -> None:
    api_url = config.get("api_url")
    username, password = config.get("username"), config.get("password")
    args = parse_arguments()

    sms_message = SMSMessage(PhoneNumber(args.sender), PhoneNumber(args.recipient), args.message)
    response = Request.post(api_url, auth=(username, password), body=sms_message)
    print_response("SMS Response", response)


if __name__ == "__main__":
    main()
