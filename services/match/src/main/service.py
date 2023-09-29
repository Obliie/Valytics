from concurrent import futures
import logging
import os
import pymongo
import subprocess
from collections.abc import MutableMapping  # Import from collections.abc instead

import grpc
from protobufs.services import match_pb2, match_pb2_grpc
from service_common.service_logging import init_logging, log_and_flush


class MatchServicer(match_pb2_grpc.MatchServicer):
    def SomeRPCMethod() -> None:
        return


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    match_pb2_grpc.add_MatchServicer_to_server(MatchServicer(), server)
    server.add_insecure_port(f"[::]:{os.environ['MATCH_SERVICE_PORT']}")
    log_and_flush(logging.INFO, "Starting Match service...")

    # MongoDB connection parameters
    mongodb_host = "valytics-ranked-match-db-1"  # Change this to your MongoDB container's host
    mongodb_port = 27001  # Change this to your MongoDB container's port
    mongodb_username = "root"
    mongodb_password = "password"
    database_name = "service-db"

    # Create a MongoDB client
    client = pymongo.MongoClient(
        host=mongodb_host, port=mongodb_port, username=mongodb_username, password=mongodb_password
    )

    # Create or access a database
    db = client[database_name]

    # Example: Insert a document into a collection
    collection = db["your_collection"]
    data = {"key": "value"}
    result = collection.insert_one(data)
    print(f"Inserted document ID: {result.inserted_id}")

    # Close the MongoDB client when done
    client.close()

    print("djjhdsj", flush=True)
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    init_logging()
    serve()
