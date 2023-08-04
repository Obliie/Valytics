from concurrent import futures
import logging
import os

import grpc
from service_common.service_logging import init_logging, log_and_flush

match_pb2, match_pb2_grpc = grpc.protos_and_services("services/match.proto")


class MatchServicer(match_pb2_grpc.MatchServicer):
    def SomeRPCMethod() -> None:
        return


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    match_pb2_grpc.add_MatchServicer_to_server(MatchServicer(), server)
    server.add_insecure_port(f"[::]:{ os.environ['MATCH_SERVICE_PORT'] }")
    log_and_flush(logging.INFO, "Starting Match service...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    init_logging()
    serve()
