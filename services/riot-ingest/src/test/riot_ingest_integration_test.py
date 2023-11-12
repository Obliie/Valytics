import logging
import os

import grpc

from protobufs.services.v1 import riot_ingest_pb2, riot_ingest_pb2_grpc
from service_common.http_util import request_get
import json

import re


def test_get_match_data() -> None:
    with grpc.insecure_channel(f"riot-ingest:{ os.environ['RIOT_INGEST_SERVICE_PORT' ]}") as channel:
        stub = riot_ingest_pb2_grpc.RiotIngestServiceStub(channel)

        response = stub.GetMatchData(
            riot_ingest_pb2.GetMatchDataRequest(match_id="7b2412ad-d530-4bec-a112-01b171bb4959")
        )
        assert response.matches_info.match_id == "7b2412ad-d530-4bec-a112-01b171bb4959"
        assert response.matches_info.is_completed == True
        assert response.players_info[0].stats.score == 3461
        assert response.teams_info[1].rounds_won == 13
        assert response.rounds_info[0].round_num == 0
        assert response.rounds_info[2].round_num == 2

        assert (
            response.rounds_info[2].plant_player_locations[0].puu_id
            == "inxcpz8Bw4qzirO6sd0OPv4q3SnRzLV0ql4Q2XUq65aDRqfrjGwY3Sj54rr0W9qpvmTtINbI0VNITw"
        )
        assert (
            response.rounds_info[2].plant_player_locations[1].puu_id
            == "Y2X9ZAnysEx5cxszvriWCL62y4Q5upG5-CFHafgqUgOgrAk1HHficYZRoOxcdN9bri4rMlcv8798bQ"
        )

        assert (
            response.rounds_info[8].defuse_player_locations[0].puu_id
            == "FjXIt87aLFSWcVkZJhxiTyAgf90zeiz2yjiPQtxbmng8oYlFeqwS9ziS7-Er8NClXt2ephk_gS754g"
        )

        assert response.rounds_info[2].plant_location.x == -2381
        assert response.rounds_info[2].defuse_location.x == 0
        assert (
            response.rounds_info[0].player_stats[0].puu_id
            == "FjXIt87aLFSWcVkZJhxiTyAgf90zeiz2yjiPQtxbmng8oYlFeqwS9ziS7-Er8NClXt2ephk_gS754g"
        )
        assert (
            response.rounds_info[0].player_stats[1].puu_id
            == "vnE1JAJyVlf08fJIwuo4zPMjIZZuvlChvEYsDPmMZbdT1Dbg0rmtDLUr1Z22TTfP4pHGEyT-FmbuPA"
        )

        assert response.rounds_info[0].player_stats[1].kills[0].game_start == 132254
        assert response.rounds_info[0].player_stats[1].kills[0].victim_location.x == -642

        assert response.rounds_info[1].player_stats[1].kills[0].game_start == 260604

        assert (
            response.rounds_info[0].player_stats[1].kills[0].assistants[1]
            == "vnE1JAJyVlf08fJIwuo4zPMjIZZuvlChvEYsDPmMZbdT1Dbg0rmtDLUr1Z22TTfP4pHGEyT-FmbuLA"
        )

        assert response.rounds_info[0].player_stats[1].kills[0].player_locations[0].view_radians == 2.7340894

        assert response.rounds_info[0].player_stats[1].kills[0].finishing_damage.damage_type == "WEAPON"
        assert response.rounds_info[0].player_stats[0].damage[0].leg_shots == 0
        assert response.rounds_info[0].player_stats[0].damage[1].leg_shots == 2
        assert response.rounds_info[0].player_stats[0].economy.spent == 800


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


def test_get_leaderboard_data() -> None:
    my_act_id = "EPISODE_1_ACT_1"
    with grpc.insecure_channel(f"riot-ingest:{ os.environ['RIOT_INGEST_SERVICE_PORT' ]}") as channel:
        stub = riot_ingest_pb2_grpc.RiotIngestServiceStub(channel)
        response = stub.GetLeaderboardData(riot_ingest_pb2.GetLeaderboardDataRequest(act_id=my_act_id))
        print(riot_ingest_pb2.ActId.Name(response.act_id))

        assert riot_ingest_pb2.ActId.Name(response.act_id) == my_act_id
        assert riot_ingest_pb2.Shard.Name(response.shard) == "LATAM"

        assert response.total_players == 312
        assert response.players[0].game_name == "hahas das"
        assert response.players[1].ranked_rating == 3132
        assert response.players[2].number_of_wins == 1


def test_get_content_data() -> None:
    with grpc.insecure_channel(f"riot-ingest:{os.environ['RIOT_INGEST_SERVICE_PORT']}", options=channel_opt) as channel:
        stub = riot_ingest_pb2_grpc.RiotIngestServiceStub(channel)

        response = stub.GetContentData(riot_ingest_pb2.GetContentDataRequest())
        print((response.characters_info[0].player_id), flush=True)
        print("hahaaa", flush=True)

        assert response.characters_info[1].localized_names.turkish == "FADE"
        assert response.characters_info[0].player_id == "E370FA57-4757-3604-3648-499E1F642D3F"
        assert response.characters_info[2].asset_name == "Default__Breach_PrimaryAsset_C"
        assert response.characters_info[3].name == "Deadlock"

        assert response.characters_info[4].name == "Raze"

        assert response.game_modes_info[0].asset_path == "/Game/GameModes/Bomb/BombGameMode.BombGameMode_C"
        assert response.game_modes_info[1].asset_name == "DeathmatchGameMode"

        assert response.acts_info[1].parent_id == "fcf2c8f4-4324-e50b-2e23-718e4a3ab046"
