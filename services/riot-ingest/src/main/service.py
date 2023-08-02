from concurrent import futures
import logging
import os

import grpc
from protobufs.services import riot_ingest_pb2, riot_ingest_pb2_grpc
from service_common.service_logging import init_logging, log_and_flush


class RiotIngestServicer(riot_ingest_pb2_grpc.RiotIngestServicer):
    def GetMatchData(
        self, request: riot_ingest_pb2.MatchDataRequest, context: grpc.ServicerContext
    ) -> riot_ingest_pb2.MatchDataResponse:
        
        # Extract the 'matchId' from the incoming request message
        match_id = request.matchId

        # Make an HTTP request to the Riot API endpoint
        url = f"https://api.riotgames.com/val/match/v1/matches/{match_id}"
        headers = {"X-Riot-Token": "YOUR_RIOT_API_KEY"}
        response = requests.get(url, headers=headers)


      # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response from Riot API (assuming it returns JSON)
            match_data = response.json()

            # Create a response message and populate it with the retrieved data
            response_message = riot_api_pb2.GetMatchDataResponse()
            response_message.match_id = match_data["matchId"]
            response_message.response = json.dumps(match_data)

            # Return the response message
            return response_message
        else:
            # Handle error cases if the Riot API call fails
            error_status = status_pb2.Status(
                code=grpc.StatusCode.INTERNAL.value[0],
                message="API call to Riot API failed."
            )
            riot_api_error = riot_api_pb2.RiotApiError(error=error_status)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("API call to Riot API failed.")
            return riot_api_error

def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    riot_ingest_pb2_grpc.add_RiotIngestServicer_to_server(RiotIngestServicer(), server)
    server.add_insecure_port(f"[::]:{ os.environ['RIOT_INGEST_SERVICE_PORT'] }")
    log_and_flush(logging.INFO, "Starting Riot Ingest service...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    init_logging()
    serve()
