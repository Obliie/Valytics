import logging
import os

import grpc

from protobufs.services import riot_ingest_pb2, riot_ingest_pb2_grpc
from service_common.http_util import request_get
import json


def test_get_match_data() -> None:
    with grpc.insecure_channel(f"riot-ingest:{ os.environ['RIOT_INGEST_SERVICE_PORT' ]}") as channel:
        stub = riot_ingest_pb2_grpc.RiotIngestServiceStub(channel)

        response = stub.GetMatchData(
            riot_ingest_pb2.GetMatchDataRequest(match_id="7b2412ad-d530-4bec-a112-01b171bb4959")
        )
    # Define the path to the directory you want to list files from

    assert response.match_id == "7b2412ad-d530-4bec-a112-01b171bb4959"


def test_get_account_by_riot_ID() -> None:
    with grpc.insecure_channel(f"riot-ingest:{ os.environ['RIOT_INGEST_SERVICE_PORT' ]}") as channel:
        stub = riot_ingest_pb2_grpc.RiotIngestServiceStub(channel)

        response = stub.GetAccountByRiotID(riot_ingest_pb2.GetAccountByRiotIDRequest(game_name="Obli", tag_line="0003"))

    assert response.game_name == "Obli"
    assert response.tag_line == "0003"
    assert response.puu_id == "xya6wbl5uMkzSdFUPWScfJ1VUUY1-Ip1Qz3AKDBIlt7vV0ZpNQNRKunciG0LnpgcQDPhWbJI_tr9bg"


def test_get_player_matches() -> None:
    with grpc.insecure_channel(f"riot-ingest:{ os.environ['RIOT_INGEST_SERVICE_PORT' ]}") as channel:
        stub = riot_ingest_pb2_grpc.RiotIngestServiceStub(channel)
        response = stub.GetPlayerMatches(
            riot_ingest_pb2.GetPlayerMatchesRequest(
                puu_id="xya6wbl5uMkzSdFUPWScfJ1VUUY1-Ip1Qz3AKDBIlt7vV0ZpNQNRKunciG0LnpgcQDPhWbJI_tr9bg"
            )
        )

    assert response.puu_id == "xya6wbl5uMkzSdFUPWScfJ1VUUY1-Ip1Qz3AKDBIlt7vV0ZpNQNRKunciG0LnpgcQDPhWbJI_tr9bg"
    assert len(response.history) == 2
    for match in response.history:
        assert match.match_id == "7b2412ad-d530-4bec-a112-01b171bb4959"
        assert match.game_start_time == "1615310282945"
        assert match.queue_id == "COMPETITIVE"


channel_opt = [
    ("grpc.max_send_message_length", 512 * 1024 * 1024),
    ("grpc.max_receive_message_length", 512 * 1024 * 1024),
]


def test_get_content_data() -> None:
    with grpc.insecure_channel(f"riot-ingest:{os.environ['RIOT_INGEST_SERVICE_PORT']}", options=channel_opt) as channel:
        stub = riot_ingest_pb2_grpc.RiotIngestServiceStub(channel)

        response = stub.GetContentData(riot_ingest_pb2.GetContentDataRequest())


def test_get_leaderboard_data() -> None:
    with grpc.insecure_channel(f"riot-ingest:{ os.environ['RIOT_INGEST_SERVICE_PORT' ]}") as channel:
        stub = riot_ingest_pb2_grpc.RiotIngestServiceStub(channel)
        response = stub.GetLeaderboardData(riot_ingest_pb2.GetLeaderboardDataRequest(act_id=3))
