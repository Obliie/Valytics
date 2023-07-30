import logging
import os

import grpc

riot_ingest_pb2, riot_ingest_pb2_grpc = grpc.protos_and_services("services/riot_ingest.proto")


def test_get_match_data() -> None:
    with grpc.insecure_channel(f"riot-ingest:{ os.environ['RIOT_INGEST_SERVICE_PORT' ]}") as channel:
        stub = riot_ingest_pb2_grpc.RiotIngestStub(channel)
        response = stub.GetMatchData(riot_ingest_pb2.MatchDataRequest(matchId="someId"))

    assert response.matchId == "id"
    assert response.data == "data"
