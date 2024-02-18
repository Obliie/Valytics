"""HTTP Utility Functions.

This module provides utility functions for making HTTP requests and converting
HTTP status codes to gRPC status codes.

Dependencies:
- Requires the 'grpc' and 'requests' libraries.
"""

from typing import Dict, Optional

import grpc
import requests

HTTP_TO_GRPC_STATUS = {
    200: grpc.StatusCode.OK,
    400: grpc.StatusCode.INVALID_ARGUMENT,
    401: grpc.StatusCode.UNAUTHENTICATED,
    403: grpc.StatusCode.PERMISSION_DENIED,
    404: grpc.StatusCode.NOT_FOUND,
    429: grpc.StatusCode.RESOURCE_EXHAUSTED,
    500: grpc.StatusCode.INTERNAL,
    502: grpc.StatusCode.DEADLINE_EXCEEDED,
    503: grpc.StatusCode.UNAVAILABLE,
    504: grpc.StatusCode.DEADLINE_EXCEEDED,
}


def http_to_grpc_status_code(http_status_code: int) -> grpc.StatusCode:
    """Converts a HTTP status code to a gRPC status code.

    Args:
        http_status_code (int): HTTP status code to convert.

    Returns:
        grpc.StatusCode: gRPC status code equivalent to the provided HTTP status code.
    """
    return HTTP_TO_GRPC_STATUS.get(http_status_code, grpc.StatusCode.UNKNOWN)


def request_get(
    api_url: str, context: grpc.ServicerContext, headers: Dict[str, str] = None
) -> Optional[Dict[str, str]]:
    """Makes a GET request to a REST API endpoint from a gRPC context.

    Args:
        api_url (str): API endpoint URL to call.
        context (grpc.ServicerContext): gRPC servicer context.
        headers (Dict[str, str]): Optional HTTP headers for the API call.

    Returns:
        Optional[Dict[str, str]]: Response in JSON format if successful, or None otherwise.
    """
    try:
        response = requests.get(api_url, headers=headers)
        grpc_status = http_to_grpc_status_code(response.status_code)
        if grpc_status == grpc.StatusCode.OK:
            return response.json()
        context.set_code(grpc_status)
        context.set_details(f"HTTP error - {response.status_code}: {response.reason}")
    except requests.RequestException as e:
        context.set_code(grpc.StatusCode.INTERNAL)
        context.set_details(f"Requests exception: {str(e)}")
    except Exception as e:
        context.set_code(grpc.StatusCode.INTERNAL)
        context.set_details(f"Unhandled exception: {str(e)}")
    return None
