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


RIOT_API_URL = "https://api.riotgames.com"
MATCH_DATA_ENDPOINT = "{RIOT_API_URL}/val/match/v1/matches/{match_id}"
ACCOUNT_DATA_ENDPOINT = "{RIOT_API_URL}/account/v1/accounts/by-riot-id/{game_name}/{tag_line}}"
MATCH_LIST_DATA_ENDPOINT = "{RIOT_API_URL}/val/match/v1/matchlists/by-puuid/{puu_id}"
LEADERBOARD_DATA_ENDPOINT = "{RIOT_API_URL}/val/ranked/v1/leaderboards/by-act/{actId})"


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
        headers = {"X-Riot-Token": os.environ["RIOT_API_KEY"]}

        match_data = request_get(url, headers, context)
        if match_data:
            response_message = riot_ingest_pb2.GetMatchDataRequest()
            parsed_matched_data = json.dumps(match_data)
            # Can check ids here
            response_message.match_id = parsed_matched_data["matchInfo"]["matchId"]
            response_message.response = parsed_matched_data
            return response_message

        return riot_ingest_pb2.GetMatchDataRequest()

    def GetAccountByRiotID(
        self, request: riot_ingest_pb2.GetAccountByRiotIDRequest, context: grpc.ServicerContext
    ) -> riot_ingest_pb2.GetAccountByRiotIDResponse:
        """Fetches match data from Riot Games API and returns the retrieved data."""

        url = ACCOUNT_DATA_ENDPOINT.format(game_name=request.game_name, tag_line=request.tag_line)
        headers = {"X-Riot-Token": os.environ["RIOT_API_KEY"]}

        account_data = request_get(url, headers, context)
        if account_data:
            response_message = riot_ingest_pb2.GetAccountByRiotIDResponse()
            parsed_account_data = json.dumps(account_data)

            response_message.game_name = parsed_account_data["gameName"]
            response_message.tag_line = parsed_account_data["tagLine"]
            response_message.pu_id = parsed_account_data["puuid"]
            return response_message

        return riot_ingest_pb2.GetMatchDataResponse()

    def GetPlayerMatches(
        self, request: riot_ingest_pb2.GetPlayerMatchesRequest, context: grpc.ServicerContext
    ) -> riot_ingest_pb2.GetPlayerMatchesResponse:
        """Fetches match data from Riot Games API and returns the retrieved data."""

        url = MATCH_LIST_DATA_ENDPOINT.format(puu_id=request.puu_id)
        headers = {"X-Riot-Token": os.environ["RIOT_API_KEY"]}

        match_data = request_get(url, headers, context)
        if match_data:
            response_message = riot_ingest_pb2.GetPlayerMatchesResponse()

            matches = []
            parsed_match_data = json.dumps(match_data)
            match_list = parsed_match_data["history"]

            for match in match_list:
                match = riot_ingest_pb2.PlayersMatches
                match.match_id = match_list["matchId"]
                match.game_start_time = match_list["gameStartTimeMillis"]
                match.queue_id = match_list["queueId"]
                matches.append(match)

            response_message.puu_id = parsed_match_data["puuid"]
            response_message.history.extend(matches)
            return response_message

        return riot_ingest_pb2.GetPlayerMatchesResponse()

    def GetContentData(self, context: grpc.ServicerContext) -> riot_ingest_pb2.GetContentDataResponse:
        """Fetches match data from Riot Games API and returns the retrieved data."""

        url = MATCH_DATA_ENDPOINT  ##
        headers = {"X-Riot-Token": os.environ["RIOT_API_KEY"]}

        context_data = request_get(url, headers, context)
        if context_data:
            response_message = riot_ingest_pb2.GetContentDataResponse()
            parsed_account_data = json.dumps(context_data)
            response_message.response = parsed_account_data
            return response_message

        return riot_ingest_pb2.GetMatchDataResponse()

    def GetLeaderboardData(
        self, request: riot_ingest_pb2.GetLeaderboardDataRequest, context: grpc.ServicerContext
    ) -> riot_ingest_pb2.GetLeaderboardDataResponse:
        """Fetches match data from Riot Games API and returns the retrieved data."""

        url = LEADERBOARD_DATA_ENDPOINT.format(puu_id=request.act_id)
        headers = {"X-Riot-Token": os.environ["RIOT_API_KEY"]}

        leaderboard_data = request_get(url, headers, context)
        if leaderboard_data:
            response_message = riot_ingest_pb2.GetLeaderboardDataResponse()
            player_data = []
            parsed_leaderboard_data = json.dumps(leaderboard_data)
            players_list = parsed_leaderboard_data["players"]

            for player in players_list:
                player = riot_ingest_pb2.PlayerDto
                player.puu_id = players_list["puuid"]
                player.game_name = players_list["gameName"]
                player.tag_line = players_list["tagLine"]
                player.leaderboard_rank = players_list["leaderboardRank"]
                player.ranked_rating = players_list["rankedRating"]
                player.number_of_wins = players_list["numberOfWins"]
                player_data.append(player)

            response_message.act_id = parsed_leaderboard_data["actId"]
            response_message.shard = parsed_leaderboard_data["shard"]
            response_message.total_players = parsed_leaderboard_data["totalPlayers"]
            response_message.players.extend(player_data)
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
