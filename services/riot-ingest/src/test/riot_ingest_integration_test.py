import logging
import os

import grpc

from protobufs.services import riot_ingest_pb2, riot_ingest_pb2_grpc
from service_common.http_util import request_get
import requests_mock


def test_get_match_data() -> None:
    with grpc.insecure_channel(f"riot-ingest:{ os.environ['RIOT_INGEST_SERVICE_PORT' ]}") as channel:
        stub = riot_ingest_pb2_grpc.RiotIngestServiceStub(channel)
        with requests_mock.Mocker() as m:
            data = {
                "matchInfo": {
                    "matchId": "7b2412ad-d530-4bec-a112-01b171bb4959",
                    "mapId": "/Game/Maps/Ascent/Ascent",
                    "gameLengthMillis": 2372651,
                    "gameStartMillis": 1615310282945,
                    "provisioningFlowId": "MATCHMAKING",
                    "isCompleted": True,
                    "customGameName": "",
                    "queueId": "COMPETITIVE",
                    "gameMode": "/Game/GameModes/Bomb/BombGameMode.BombGameMode_C",
                    "isRanked": True,
                    "seasonId": "EPISODE_2_ACT_2",
                },
                "players": [
                    {
                        "puuid": "Hng3HRgjI7CMrBDFH4jd6TS08gALhYD_muPm9JKN2bcwT_s-wOBumpfcrWeSXv7OVydqBXSRunlUsA",
                        "teamId": "BLUE",
                        "partyId": "0b653e5d-7bb5-46cc-95c1-ad1ec51cee62",
                        "characterId": "a3bfb853-43b2-7238-a4f1-ad90e9e46bcc",
                        "stats": {
                            "score": 3461,
                            "roundsPlayed": 21,
                            "kills": 11,
                            "deaths": 14,
                            "assists": 7,
                            "playtimeMillis": 2372651,
                        },
                        "competitiveTier": "SILVER_1",
                        "playerCard": "9fb348bc-41a0-91ad-8a3e-818035c4e561",
                        "playerTitle": "2d284b12-4536-1d0e-b08c-e58850b2a76e",
                    },
                    {
                        "puuid": "HgBQup9MZhYkMyqcw8-HzEqxdL-u4JXfCjAsrTVMSYBTq2djY791__r-XOXx1vkgBXlNmgUvDLxp9Q",
                        "teamId": "BLUE",
                        "partyId": "8a66736a-1982-40ff-ad7f-47e325c2dfd2",
                        "characterId": "f94c3b30-42be-e959-889c-5aa313dba261",
                        "stats": {
                            "score": 6162,
                            "roundsPlayed": 21,
                            "kills": 21,
                            "deaths": 14,
                            "assists": 4,
                            "playtimeMillis": 2372651,
                        },
                        "competitiveTier": "GOLD_1",
                        "playerCard": "16939544-4f84-c889-545e-659e071ff3f8",
                        "playerTitle": "540826d2-4aff-4da9-e1b7-4ebf79deb4b4",
                    },
                ],
            }

            m.get(requests_mock.ANY, json=data)

        response = stub.GetMatchData(
            riot_ingest_pb2.GetMatchDataRequest(match_id="7b2412ad-d530-4bec-a112-01b171bb4959")
        )

    assert response.matchId == "7b2412ad-d530-4bec-a112-01b171bb4959"
