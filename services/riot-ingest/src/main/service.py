from concurrent import futures
import logging
import os

import grpc
import json
import requests

riot_ingest_pb2, riot_ingest_pb2_grpc = grpc.protos_and_services(
    "services/riot_ingest.proto")

HTTP_TO_GRPC_STATUS = {
    200: grpc.StatusCode.OK,
    400: grpc.StatusCode.INVALID_ARGUMENT,
    401: grpc.StatusCode.UNAUTHENTICATED,
    403: grpc.StatusCode.PERMISSION_DENIED,
    404: grpc.StatusCode.NOT_FOUND,
    429: grpc.StatusCode.RESOURCE_EXHAUSTED,
    500: grpc.StatusCode.INTERNAL,
    503: grpc.StatusCode.UNAVAILABLE,
}


class RiotIngester(riot_ingest_pb2_grpc.RiotIngestServicer):

    def ErrorHandler(
        self, request: riot_ingest_pb2.MatchDataRequest, context: grpc.ServicerContext
    ) -> riot_ingest_pb2.MatchDataResponse:

        # Extract the 'matchId' from the incoming request message
        match_id = request.matchId

        # Make an HTTP request to the Riot API endpoint
        url = f"https://api.riotgames.com/val/match/v1/matches/{match_id}"
        headers = {"X-Riot-Token": "YOUR_RIOT_API_KEY"}
        try:
            response = requests.get(url, headers=headers)

            # Get the gRPC status code from the mapping or use UNKNOWN if not found
            grpc_status = HTTP_TO_GRPC_STATUS.get(
                response.status_code, grpc.StatusCode.UNKNOWN)

            if grpc_status == grpc.StatusCode.OK:
                # Parse the JSON response from Riot API (assuming it returns JSON)
                match_data = response.json()

                # Create a response message and populate it with the retrieved data
                response_message = riot_api_pb2.GetMatchDataResponse()
                response_message.match_id = match_data["matchId"]
                response_message.response = json.dumps(match_data)

                # Return the response message
                return response_message
                # Handle successful response
            else:
                context.set_code(grpc_status)
                context.set_details(f"HTTP error: {response.status_code}")

        except requests.RequestException as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Requests exception: {str(e)}")
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Unhandled exception {str(e)}")

        return riot_api_pb2.GetMatchDataResponse()


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    riot_ingest_pb2_grpc.add_RiotIngestServicer_to_server(
        RiotIngester(), server)
    server.add_insecure_port(
        f"[::]:{ os.environ['RIOT_INGEST_SERVICE_PORT'] }")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    init_logging()
    serve()
