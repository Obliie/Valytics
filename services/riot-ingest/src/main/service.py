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
        return riot_ingest_pb2.MatchDataResponse(matchId="id", response="data")


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
