from concurrent import futures
import logging
import os

import grpc


riot_ingest_pb2, riot_ingest_pb2_grpc = grpc.protos_and_services("services/riot_ingest.proto")


class RiotIngester(riot_ingest_pb2_grpc.RiotIngestServicer):
    def GetMatchData(
        self, request: riot_ingest_pb2.MatchDataRequest, context: int
    ) -> riot_ingest_pb2.MatchDataResponse:
        return riot_ingest_pb2.MatchDataResponse(matchId="id", response="data")


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    riot_ingest_pb2_grpc.add_RiotIngestServicer_to_server(RiotIngester(), server)
    server.add_insecure_port(f"[::]:{ os.environ['RIOT_INGEST_SERVICE_PORT'] }")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()
