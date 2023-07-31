from concurrent import futures
import logging
import os

import grpc
from protobufs.services import riot_ingest_pb2, riot_ingest_pb2_grpc
from service_common.service_logging import init_logging, log_and_flush


class RiotIngestServicer(riot_ingest_pb2_grpc.RiotIngestServicer):
    def GetMatchData(
        self, request: riot_ingest_pb2.MatchDataRequest, context: int
    ) -> riot_ingest_pb2.MatchDataResponse:
        match_id = request.matchId  
        status_code = 100     
        if status_code == 200:
            return riot_ingest_pb2.MatchDataResponse(matchId=match_id, response=self.loadMatchData())
        else:
            error_message = riot_ingest_pb2.ErrorMessageResponse(code=status_code, message="API call failed.")
            context.set_code(grpc.StatusCode.INTERNAL)  # Set an appropriate gRPC status code for the error
            context.set_details("API call to Riot API failed.")
            return error_message

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
