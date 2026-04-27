from http_client.request import Request
from utils.console import print_sms_response
from http_client.schemas import SMSMessage, PhoneNumber
from utils.cli_parser import parse_arguments
from config import config


def main() -> None:
    api_url = config.get_value("api_url")
    username, password = config.get_value("username"), config.get_value("password")
    args = parse_arguments()

    sms_message = SMSMessage(PhoneNumber(args.sender), PhoneNumber(args.recipient), args.message)
    response = Request.post(api_url, auth=(username, password), body=sms_message)
    print_sms_response(response)


if __name__ == "__main__":
    main()
