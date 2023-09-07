import logging
import os

import grpc

from protobufs.services import riot_ingest_pb2, riot_ingest_pb2_grpc
from service_common.http_util import request_get
import json

import re


def test_get_match_data() -> None:
    with grpc.insecure_channel(f"riot-ingest:{ os.environ['RIOT_INGEST_SERVICE_PORT' ]}") as channel:
        stub = riot_ingest_pb2_grpc.RiotIngestServiceStub(channel)

        response = stub.GetMatchData(
            riot_ingest_pb2.GetMatchDataRequest(match_id="7b2412ad-d530-4bec-a112-01b171bb4959")
        )
    # Define the path to the directory you want to list files from

    assert response.match_id == "7b2412ad-d530-4bec-a112-01b171bb4959"


def test_get_account_by_riot_ID() -> None:
    my_game_name = "Obli"
    my_tag_line = "0003"
    with grpc.insecure_channel(f"riot-ingest:{ os.environ['RIOT_INGEST_SERVICE_PORT' ]}") as channel:
        stub = riot_ingest_pb2_grpc.RiotIngestServiceStub(channel)

        response = stub.GetAccountByRiotID(
            riot_ingest_pb2.GetAccountByRiotIDRequest(game_name=my_game_name, tag_line=my_tag_line)
        )

    assert response.game_name == my_game_name
    assert response.tag_line == my_tag_line
    assert response.puu_id == "xya6wbl5uMkzSdFUPWScfJ1VUUY1-Ip1Qz3AKDBIlt7vV0ZpNQNRKunciG0LnpgcQDPhWbJI_tr9bg"


def test_get_player_matches() -> None:
    my_puu_id = "xya6wbl5uMkzSdFUPWScfJ1VUUY1-Ip1Qz3AKDBIlt7vV0ZpNQNRKunciG0LnpgcQDPhWbJI_tr9bg"
    with grpc.insecure_channel(f"riot-ingest:{ os.environ['RIOT_INGEST_SERVICE_PORT' ]}") as channel:
        stub = riot_ingest_pb2_grpc.RiotIngestServiceStub(channel)
        response = stub.GetPlayerMatches(riot_ingest_pb2.GetPlayerMatchesRequest(puu_id=my_puu_id))

    assert len(response.history) == 2
    assert response.puu_id == my_puu_id
    assert response.history[0].queue_id == "COMPETITIVE"

    match_id_pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    start_time_pattern = r"^\d{13}$"

    for match in response.history:
        assert re.match(match_id_pattern, match.match_id)
        assert re.match(start_time_pattern, match.game_start_time)


channel_opt = [
    ("grpc.max_send_message_length", 512 * 1024 * 1024),
    ("grpc.max_receive_message_length", 512 * 1024 * 1024),
]


def test_get_content_data() -> None:
    with grpc.insecure_channel(f"riot-ingest:{os.environ['RIOT_INGEST_SERVICE_PORT']}", options=channel_opt) as channel:
        stub = riot_ingest_pb2_grpc.RiotIngestServiceStub(channel)

        response = stub.GetContentData(riot_ingest_pb2.GetContentDataRequest())


def test_get_leaderboard_data() -> None:
    my_act_id = "EPISODE_1_ACT_1"
    with grpc.insecure_channel(f"riot-ingest:{ os.environ['RIOT_INGEST_SERVICE_PORT' ]}") as channel:
        stub = riot_ingest_pb2_grpc.RiotIngestServiceStub(channel)
        response = stub.GetLeaderboardData(riot_ingest_pb2.GetLeaderboardDataRequest(act_id=my_act_id))
        assert riot_ingest_pb2.ActId.Name(response.act_id) == my_act_id
