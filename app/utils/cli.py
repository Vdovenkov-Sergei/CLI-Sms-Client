"""Command-line argument parser for the CLI SMS client."""

import argparse


def get_parser() -> argparse.ArgumentParser:
    """Returns parser for command-line arguments for sending an SMS.

    Required arguments:
        --sender: The sender's phone number.
        --recipient: The recipient's phone number.
        --message: The SMS text content.

    Returns:
        A configured parser instance ready to parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="CLI for sending SMS")
    parser.add_argument("--sender", required=True, help="Sender phone number")
    parser.add_argument("--recipient", required=True, help="Recipient phone number")
    parser.add_argument("--message", required=True, help="SMS message text")

    return parser
