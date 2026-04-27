import json

from rich.console import Console
from rich.table import Table

from app.http_client.http_message import HTTPResponse

console = Console()


def print_json_response(title: str, response: HTTPResponse) -> None:
    table = Table(title=title, show_header=True, header_style="cyan")
    status_style = "green" if response.status_code < 400 else "red"
    table.add_column("Status Code", style=status_style)
    table.add_column("Response Body", style="yellow")

    try:
        formatted_body = json.dumps(json.loads(response.body), indent=2)
    except json.JSONDecodeError:
        formatted_body = response.body
        console.log("Error: Failed to decode response body as JSON.")

    table.add_row(str(response.status_code), formatted_body)

    console.print(table)
