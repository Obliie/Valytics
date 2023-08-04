import os

import grpc

match_pb2, match_pb2_grpc = grpc.protos_and_services("services/match.proto")


def test_example() -> None:
    with grpc.insecure_channel(f"match:{ os.environ['MATCH_SERVICE_PORT' ]}") as channel:
        stub = match_pb2_grpc.MatchStub(channel)
        # Make rpc...

    # Check response...
