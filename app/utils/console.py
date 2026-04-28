"""Console output helpers for the CLI SMS client."""

import json

from rich.console import Console
from rich.table import Table

from app.http.message import HTTPResponse


class ResponseConsole:
    """Renders HTTP responses as formatted tables to stdout."""

    def __init__(self) -> None:
        """Initializes the `ResponseConsole`."""
        self.console = Console()

    def print(self, title: str, response: HTTPResponse) -> None:
        """Prints an HTTP response as a formatted table.

        Args:
            title: The table title shown above the output.
            response: The `HTTPResponse` to display.
        """
        table = Table(title=title, show_header=True, header_style="cyan")
        status_style = "green" if response.status_code < 400 else "red"
        table.add_column("Status Code", style=status_style)
        table.add_column("Response Body", style="yellow")

        try:
            formatted_body = json.dumps(json.loads(response.body), indent=2)
        except json.JSONDecodeError:
            formatted_body = response.body
            self.console.log("Error: Failed to decode response body as JSON.")

        table.add_row(str(response.status_code), formatted_body)
        self.console.print(table)
