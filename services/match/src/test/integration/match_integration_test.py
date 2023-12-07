import os

import grpc

from protobufs.common.v1 import match_pb2
from protobufs.services.match.v1 import match_service_pb2, match_service_pb2_grpc
from protobufs.services.v1 import riot_ingest_pb2, riot_ingest_pb2_grpc


def get_riot_match_data():
    with grpc.insecure_channel(
        f"riot-ingest:{os.environ['RIOT_INGEST_SERVICE_PORT']}"
    ) as channel:
        stub = riot_ingest_pb2_grpc.RiotIngestServiceStub(channel)

        response = stub.GetMatchData(
            riot_ingest_pb2.GetMatchDataRequest(
                match_id="7b2412ad-d530-4bec-a112-01b171bb4959"
            )
        )

        print(str(response))
    return response


def test_store_match() -> None:
    print("hello")
