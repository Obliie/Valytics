"""Riot Ingest Service.

This module implements the Riot Ingest service, responsible for processing and ingesting data
from the Riot Games API. It configures the protofile schema to provide game statistics and
other relevant information to the application.

Usage:
- Periodically fetches data from the Riot Games API to update the internal database.
- Allows the application to retrieve game statistics through gRPC calls.

Dependencies:
- Relies on the Riot Games API for game data.
- Utilizes Protocol Buffers (protobuf) for efficient communication via gRPC.

Note:
Ensure the correct Riot Games API key is provided for seamless data ingestion.
"""


from concurrent import futures
import json
import logging
import os

import grpc
from protobufs.services import riot_ingest_pb2, riot_ingest_pb2_grpc
from service_common.http_util import request_get
from service_common.service_logging import init_logging, log_and_flush
from google.protobuf.descriptor import EnumDescriptor


RIOT_API_URL = "http://mockserver:1080"
MATCH_DATA_ENDPOINT = f"{RIOT_API_URL}/val/match/v1/matches/{{match_id}}"
ACCOUNT_DATA_ENDPOINT = f"{RIOT_API_URL}/account/v1/accounts/by-riot-id/{{game_name}}/{{tag_line}}"
MATCH_LIST_DATA_ENDPOINT = f"{RIOT_API_URL}/val/match/v1/matchlists/by-puuid/{{puu_id}}"
CONTENT_DATA_ENDPOINT = f"{RIOT_API_URL}/val/content/v1/contents"
LEADERBOARD_DATA_ENDPOINT = f"{RIOT_API_URL}/val/ranked/v1/leaderboards/by-act/{{act_id}}"


class RiotIngestServicer(riot_ingest_pb2_grpc.RiotIngestService):
    """gRPC Service for Riot Ingest.

    The RiotIngestServicer class handles incoming requests and provides game statistics
    and relevant information to the application.

    This class acts as an intermediary between the application and the Riot Games API,
    enabling seamless data retrieval and organization for the application's components.
    """

    def GetMatchData(
        self, request: riot_ingest_pb2.GetMatchDataRequest, context: grpc.ServicerContext
    ) -> riot_ingest_pb2.GetMatchDataResponse:
        """Fetches match data from Riot Games API and returns the retrieved data."""
        url = MATCH_DATA_ENDPOINT.format(match_id=request.match_id)
        print(url, flush=True)
        # headers = {"X-Riot-Token": os.environ["RIOT_API_KEY"]}

        # match_data = request_get(url, headers, context)
        match_data = request_get(url, context)

        if match_data:
            response_message = riot_ingest_pb2.GetMatchDataResponse()
            parsed_matched_data = json.dumps(match_data)
            # Can check ids here
            response_message.match_id = match_data["matchInfo"]["matchId"]
            response_message.response = parsed_matched_data
            return response_message

        return riot_ingest_pb2.GetMatchDataResponse()

    def GetAccountByRiotID(
        self, request: riot_ingest_pb2.GetAccountByRiotIDRequest, context: grpc.ServicerContext
    ) -> riot_ingest_pb2.GetAccountByRiotIDResponse:
        """Fetches match data from Riot Games API and returns the retrieved data."""

        url = ACCOUNT_DATA_ENDPOINT.format(game_name=request.game_name, tag_line=request.tag_line)
        # headers = {"X-Riot-Token": os.environ["RIOT_API_KEY"]}
        # account_data = request_get(url, headers, context)
        account_data = request_get(url, context)

        if account_data:
            response_message = riot_ingest_pb2.GetAccountByRiotIDResponse()
            response_message.game_name = account_data["gameName"]
            response_message.tag_line = account_data["tagLine"]
            response_message.puu_id = account_data["puuid"]
            return response_message

        return riot_ingest_pb2.GetMatchDataResponse()

    def GetPlayerMatches(
        self, request: riot_ingest_pb2.GetPlayerMatchesRequest, context: grpc.ServicerContext
    ) -> riot_ingest_pb2.GetPlayerMatchesResponse:
        """Fetches match data from Riot Games API and returns the retrieved data."""

        url = MATCH_LIST_DATA_ENDPOINT.format(puu_id=request.puu_id)
        # headers = {"X-Riot-Token": os.environ["RIOT_API_KEY"]}

        # match_data = request_get(url, headers, context)
        match_data = request_get(url, context)

        if match_data:
            response_message = riot_ingest_pb2.GetPlayerMatchesResponse()
            matches = []
            match_list = match_data["history"]

            for match in match_list:
                match_proto = riot_ingest_pb2.PlayersMatches()
                match_proto.match_id = match["matchId"]
                match_proto.game_start_time = str(match["gameStartTimeMillis"])
                match_proto.queue_id = match["queueId"]
                matches.append(match_proto)

            response_message.puu_id = match_data["puuid"]
            response_message.history.extend(matches)
            return response_message

        return riot_ingest_pb2.GetPlayerMatchesResponse()

    def GetContentData(
        self, request: riot_ingest_pb2.GetContentDataRequest, context: grpc.ServicerContext
    ) -> riot_ingest_pb2.GetContentDataResponse:
        """Fetches match data from Riot Games API and returns the retrieved data."""

        url = CONTENT_DATA_ENDPOINT
        # headers = {"X-Riot-Token": os.environ["RIOT_API_KEY"]}

        # context_data = request_get(url, headers, context)
        context_data = request_get(url, context)

        if context_data:
            response_message = riot_ingest_pb2.GetContentDataResponse()
            response_message.response = str(context_data)
            return response_message

        return riot_ingest_pb2.GetContentDataResponse()

    def GetLeaderboardData(
        self, request: riot_ingest_pb2.GetLeaderboardDataRequest, context: grpc.ServicerContext
    ) -> riot_ingest_pb2.GetLeaderboardDataResponse:
        """Fetches match data from Riot Games API and returns the retrieved data."""

        # Create a mapping between enum field names and their integer values
        enum_mapping = {
            0: "CLOSED_BETA_ACT_1",
            1: "CLOSED_BETA_ACT_2",
            2: "CLOSED_BETA_ACT_3",
            3: "EPISODE_1_ACT_1",
            4: "EPISODE_1_ACT_2",
            5: "EPISODE_1_ACT_3",
            6: "EPISODE_2_ACT_1",
            7: "EPISODE_2_ACT_2",
            8: "EPISODE_2_ACT_3",
            9: "EPISODE_3_ACT_1",
            10: "EPISODE_3_ACT_2",
            11: "EPISODE_3_ACT_3",
            12: "EPISODE_4_ACT_1",
            13: "EPISODE_4_ACT_2",
            14: "EPISODE_4_ACT_3",
            15: "EPISODE_5_ACT_1",
            16: "EPISODE_5_ACT_2",
            17: "EPISODE_5_ACT_3",
            18: "EPISODE_6_ACT_1",
            19: "EPISODE_6_ACT_2",
            20: "EPISODE_6_ACT_3",
            21: "EPISODE_7_ACT_1",
        }

        # In your GetLeaderboardData function, use the mapping to get the integer value from the field name

        url = LEADERBOARD_DATA_ENDPOINT.format(act_id=enum_mapping.get(request.act_id))
        # headers = {"X-Riot-Token": os.environ["RIOT_API_KEY"]}
        # leaderboard_data = request_get(url, headers, context)

        leaderboard_data = request_get(url, context)

        if leaderboard_data:
            response_message = riot_ingest_pb2.GetLeaderboardDataResponse()
            player_data = []
            parsed_leaderboard_data = leaderboard_data
            players_list = parsed_leaderboard_data["players"]

            for player in players_list:
                player_proto = riot_ingest_pb2.PlayerDto()
                player_proto.puu_id = player["puuid"]
                player_proto.game_name = player["gameName"]
                player_proto.tag_line = player["tagLine"]
                player_proto.leaderboard_rank = player["leaderboardRank"]
                player_proto.ranked_rating = player["rankedRating"]
                player_proto.number_of_wins = player["numberOfWins"]
                player_data.append(player_proto)

            response_message.players.extend(player_data)
            response_message.act_id = parsed_leaderboard_data["actId"]
            response_message.shard = parsed_leaderboard_data["shard"]
            response_message.total_players = parsed_leaderboard_data["totalPlayers"]
            return response_message

        return riot_ingest_pb2.GetPlayerMatchesResponse()


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    riot_ingest_pb2_grpc.add_RiotIngestServiceServicer_to_server(RiotIngestServicer(), server)
    server.add_insecure_port(f"[::]:{ os.environ['RIOT_INGEST_SERVICE_PORT'] }")
    log_and_flush(logging.INFO, "Starting Riot Ingest service...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    init_logging()
    serve()
