"""Tests for CLI argument parsing and validation."""

import sys
from unittest.mock import patch

import pytest

from app.utils.cli import get_parser


class TestGetParser:
    """Tests CLI argument parser."""

    @pytest.mark.parametrize(
        ["sender", "recipient", "message"],
        [
            ("+1234567890", "+0987654321", "Test message"),
            ("+123", "+456", "Short"),
            ("+1-234-567", "+9-876-543", "Special-chars: !@#"),
            ("1234567890", "9876543210", "No plus signs"),
        ],
        ids=[
            "standard",
            "short-numbers",
            "special-characters",
            "no-plus-signs",
        ],
    )
    def test_valid_arguments(self, sender: str, recipient: str, message: str) -> None:
        """Parses all three required arguments and assigns them to the correct attributes."""
        test_args = ["script.py", "--sender", sender, "--recipient", recipient, "--message", message]

        with patch.object(sys, "argv", test_args):
            parser = get_parser()
            args = parser.parse_args()

        assert args.sender == sender
        assert args.recipient == recipient
        assert args.message == message

    @pytest.mark.parametrize(
        "test_args",
        [
            ["script.py", "--recipient", "+123", "--message", "test"],
            ["script.py", "--sender", "+123", "--message", "test"],
            ["script.py", "--sender", "+123", "--recipient", "+456"],
            ["script.py"],
        ],
        ids=[
            "missing-sender",
            "missing-recipient",
            "missing-message",
            "missing-all",
        ],
    )
    def test_missing_required_args(self, test_args: list[str]) -> None:
        """Exits with an error when any required argument is omitted."""
        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit):
                parser = get_parser()
                parser.parse_args()

    def test_help_message(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Prints help text containing all argument names and descriptions."""
        with patch.object(sys, "argv", ["script.py", "--help"]):
            try:
                parser = get_parser()
                parser.parse_args()
            except SystemExit:
                pass

        output = capsys.readouterr().out

        assert "Sender phone number" in output
        assert "Recipient phone number" in output
        assert "SMS message text" in output
        assert "--sender" in output
        assert "--recipient" in output
        assert "--message" in output

    def test_argument_order_independence(self) -> None:
        """Parses arguments correctly regardless of their order on the command line."""
        test_args = [
            "script.py",
            "--message",
            "Test message",
            "--sender",
            "+1234567890",
            "--recipient",
            "+0987654321",
        ]

        with patch.object(sys, "argv", test_args):
            parser = get_parser()
            args = parser.parse_args()

        assert args.sender == "+1234567890"
        assert args.recipient == "+0987654321"
        assert args.message == "Test message"

    def test_unknown_arguments(self) -> None:
        """Exits with an error when an unrecognised argument is passed."""
        test_args = [
            "script.py",
            "--sender",
            "+123",
            "--recipient",
            "+456",
            "--message",
            "test",
            "--unknown",
            "value",
        ]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit):
                parser = get_parser()
                parser.parse_args()
