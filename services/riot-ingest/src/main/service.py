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

        def set_lang(character, response):
            response = riot_ingest_pb2.Languages()

            print(character["ar-AE"], flush=True)
            print(character["de-DE"], flush=True)

            print(character["en-US"], flush=True)
            print(character["es-ES"], flush=True)
            print(character["es-MX"], flush=True)
            print(character["fr-FR"], flush=True)
            print(character["id-ID"], flush=True)
            print(character["it-IT"], flush=True)
            print(character["ja-JP"], flush=True)
            print(character["ko-KR"], flush=True)
            print(character["pl-PL"], flush=True)
            print(character["pt-BR"], flush=True)
            print(character["ru-RU"], flush=True)
            print(character["th-TH"], flush=True)
            print(character["tr-TR"], flush=True)
            print(character["tr-TR"], flush=True)
            print(character["vi-VN"], flush=True)

            print(character["zh-CN"], flush=True)
            print(character["zh-TW"], flush=True)
            print("HAHAHAAH", flush=True)
            print("HAHAHAAH", flush=True)
            print("HAHAHAAH", flush=True)
            print("HAHAHAAH", flush=True)
            print("HAHAHAAH", flush=True)
            response.arabic = character["ar-AE"]
            response.german = character["de-DE"]
            response.english = character["en-US"]
            response.spanish_spain = character["es-ES"]
            response.spanish_mexico = character["es-MX"]
            response.french = character["fr-FR"]
            response.indonesian = character["id-ID"]
            response.italian = character["it-IT"]
            response.japanese = character["ja-JP"]
            response.korean = character["ko-KR"]
            response.polish = character["pl-PL"]
            response.portuguese_brazil = character["pt-BR"]
            response.russian = character["ru-RU"]
            response.thai = character["th-TH"]
            response.turkish = character["tr-TR"]
            response.vietnamese = character["vi-VN"]
            response.chinese_simplified = character["zh-CN"]
            response.chinese_traditional = character["zh-TW"]
            return response

        def populate_proto_response(list):
            characters = []
            character_list = context_data[list]

            for character in character_list:
                character_proto = riot_ingest_pb2.GameInformation()
                response_languages = set_lang(character["localizedNames"], response=riot_ingest_pb2.Languages())
                character_proto.name = character["name"]
                character_proto.player_id = character["id"]
                character_proto.asset_name = character["assetName"]
                character_proto.localized_names.CopyFrom(response_languages)
                characters.append(character_proto)

            return characters

        if context_data:
            response_message = riot_ingest_pb2.GetContentDataResponse()
            characters = populate_proto_response("characters")
            response_message.character_info.extend(characters)

            maps = populate_proto_response("maps")
            chromas = populate_proto_response("chromas")
            skins = populate_proto_response("skins")
            skinLevels = populate_proto_response("skinLevels")
            equips = populate_proto_response("equips")

            gameModes = populate_proto_response("gameModes")  # DIFFERENT
            sprays = populate_proto_response("sprays")
            sprayLevels = populate_proto_response("sprayLevels")
            charms = populate_proto_response("charms")
            charmLevels = populate_proto_response("charmLevels")
            playerCards = populate_proto_response("playerCards")
            ceremonies = populate_proto_response("ceremonies")

            playerTitles = populate_proto_response("playerTitles")
            # acts = populate_proto_response("acts")  # DIFFERENT

            return response_message

        return riot_ingest_pb2.GetContentDataResponse()

    def GetLeaderboardData(
        self, request: riot_ingest_pb2.GetLeaderboardDataRequest, context: grpc.ServicerContext
    ) -> riot_ingest_pb2.GetLeaderboardDataResponse:
        """Fetches match data from Riot Games API and returns the retrieved data."""

        url = LEADERBOARD_DATA_ENDPOINT.format(act_id=(riot_ingest_pb2.ActId.Name(request.act_id)))

        # headers = {"X-Riot-Token": os.environ["RIOT_API_KEY"]}
        # leaderboard_data = request_get(url, headers, context)

        leaderboard_data = request_get(url, context)

        if leaderboard_data:
            response_message = riot_ingest_pb2.GetLeaderboardDataResponse()
            player_data = []
            players_list = leaderboard_data["players"]

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
            response_message.act_id = leaderboard_data["actId"]
            response_message.shard = leaderboard_data["shard"]
            response_message.total_players = leaderboard_data["totalPlayers"]
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
