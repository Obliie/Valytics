import os

import grpc

from protobufs.services import match_pb2, match_pb2_grpc


def test_example() -> None:
    with grpc.insecure_channel(f"match:{ os.environ['MATCH_SERVICE_PORT' ]}") as channel:
        stub = match_pb2_grpc.MatchStub(channel)
        # Make rpc...

    # Check response...
