from unittest.mock import MagicMock

from app.utils.console import print_json_response


class TestPrintResponse:
    def test_successful_json_response(self, mock_console: MagicMock, mock_response: MagicMock) -> None:
        response = mock_response(body={"key": "value"})
        print_json_response("Test Title", response)

        mock_console.print.assert_called_once()
        mock_table = mock_console.print.call_args[0][0]

        assert mock_table.title == "Test Title"
        assert len(mock_table.columns) == 2
        assert mock_table.columns[0].header == "Status Code"
        assert mock_table.columns[1].header == "Response Body"
        assert '{\n  "key": "value"\n}' == next(mock_table.columns[1].cells)
        assert mock_table.columns[0].style == "green"

    def test_non_json_response(self, mock_console: MagicMock, mock_response: MagicMock) -> None:
        response = mock_response(body="Plain text response", is_json=False)
        print_json_response("Test Title", response)

        mock_console.log.assert_called_once_with("Error: Failed to decode response body as JSON.")
        mock_table = mock_console.print.call_args[0][0]
        assert "Plain text response" == next(mock_table.columns[1].cells)

    def test_error_response(self, mock_console: MagicMock, mock_response: MagicMock) -> None:
        response = mock_response(status_code=404, body={"error": "Not found"})
        print_json_response("Error Test", response)

        mock_table = mock_console.print.call_args[0][0]
        assert mock_table.columns[0].style == "red"
        assert '{\n  "error": "Not found"\n}' == next(mock_table.columns[1].cells)

    def test_invalid_json(self, mock_console: MagicMock, mock_response: MagicMock) -> None:
        response = mock_response(body="{invalid: json}", is_json=False)
        print_json_response("Invalid JSON", response)

        mock_console.log.assert_called_once_with("Error: Failed to decode response body as JSON.")
        mock_table = mock_console.print.call_args[0][0]
        assert "{invalid: json}" == next(mock_table.columns[1].cells)
