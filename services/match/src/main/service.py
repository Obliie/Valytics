import logging
import os
from concurrent import futures

import grpc
from config import Config
from google.protobuf import json_format
from pymongo import MongoClient
from service_common.service_logging import init_logging, log_and_flush

from protobufs.services.match.v1 import match_service_pb2, match_service_pb2_grpc

DATABASE_USERNAME_FILE = "/run/secrets/mongo-root-username"
DATABASE_PASSWORD_FILE = "/run/secrets/mongo-root-password"

MATCH_COLLECTION_NAME = "match"


class MatchServicer(match_service_pb2_grpc.MatchService):
    DATABASE_HOST = Config.CONFIG["Services"]["Match"]["Database"]["Host"]
    DATABASE_PORT = Config.CONFIG["Services"]["Match"]["Database"]["Port"]
    DATABASE_NAME = Config.CONFIG["Services"]["Match"]["Database"]["Name"]

    def __init__(self):
        with open(DATABASE_USERNAME_FILE) as database_username_file, open(
            DATABASE_PASSWORD_FILE
        ) as database_password_file:
            self.client = MongoClient(
                f"mongodb://{database_username_file.read()}:{database_password_file.read()}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}?authSource=admin"
            )
            log_and_flush(logging.INFO, f"MongoDB client created...")

    def StoreMatch(
        self,
        request: match_service_pb2.StoreMatchRequest,
        context: grpc.ServicerContext,
    ) -> match_service_pb2.StoreMatchResponse:
        result = (
            self.client[self.DATABASE_NAME]
            .get_collection(MATCH_COLLECTION_NAME)
            .insert_one(json_format.MessageToDict(request.match))
        )

        resp = match_service_pb2.StoreMatchResponse()
        resp.success = result.acknowledged
        return resp


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
