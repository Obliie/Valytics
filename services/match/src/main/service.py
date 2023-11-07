from concurrent import futures
import logging
import os

import grpc
from protobufs.services.v1 import match_service_pb2, match_service_pb2_grpc
from service_common.service_logging import init_logging, log_and_flush


class MatchServicer(match_service_pb2_grpc.MatchService):
    def SomeRPCMethod() -> None:
        return


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    match_service_pb2_grpc.add_MatchServiceServicer_to_server(MatchServicer(), server)
    server.add_insecure_port(f"[::]:{ os.environ['MATCH_SERVICE_PORT'] }")
    log_and_flush(logging.INFO, "Starting Match service...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    init_logging()
    serve()
