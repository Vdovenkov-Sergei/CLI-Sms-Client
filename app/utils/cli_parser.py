import argparse


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CLI for sending SMS")
    parser.add_argument("--sender", required=True, help="Sender phone number")
    parser.add_argument("--recipient", required=True, help="Recipient phone number")
    parser.add_argument("--message", required=True, help="SMS message text")

    return parser.parse_args()
