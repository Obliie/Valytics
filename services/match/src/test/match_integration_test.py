import os

import grpc

from protobufs.services.v1 import match_service_pb2, match_service_pb2_grpc


def test_example() -> None:
    with grpc.insecure_channel(f"match:{ os.environ['MATCH_SERVICE_PORT' ]}") as channel:
        stub = match_service_pb2_grpc.MatchServiceStub(channel)
        # Make rpc...

    # Check response...
