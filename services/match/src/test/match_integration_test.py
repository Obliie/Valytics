import os

import grpc

from protobufs.common.v1 import match_pb2
from protobufs.services.match.v1 import match_service_pb2, match_service_pb2_grpc


def test_example() -> None:
    with grpc.insecure_channel(
        f"match:{ os.environ['MATCH_SERVICE_PORT' ]}"
    ) as channel:
        stub = match_service_pb2_grpc.MatchServiceStub(channel)
        # Make rpc...

    # Check response...
