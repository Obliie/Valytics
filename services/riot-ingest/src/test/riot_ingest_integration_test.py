import logging
import os

import grpc

from protobufs.services import riot_ingest_pb2, riot_ingest_pb2_grpc


def test_get_match_data() -> None:
    with grpc.insecure_channel(f"riot-ingest:{ os.environ['RIOT_INGEST_SERVICE_PORT' ]}") as channel:
        stub = riot_ingest_pb2_grpc.RiotIngestStub(channel)
        response = stub.GetMatchData(riot_ingest_pb2.MatchDataRequest(matchId="someId"))

    assert response.matchId == "id"
    assert response.data == "data"
