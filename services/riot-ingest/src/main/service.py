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
from protobufs.common import match_pb2, match_pb2_grpc

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

        def populate_match_info():
            match_info_list = match_data["matchInfo"]
            match_info_proto = match_pb2.MatchInformation()
            match_info_proto.match_id = match_info_list["matchId"]
            match_info_proto.map_id = match_info_list["mapId"]
            match_info_proto.game_length = match_info_list["gameLengthMillis"]
            match_info_proto.game_start = match_info_list["gameStartMillis"]
            match_info_proto.prov_flow_id = match_info_list["provisioningFlowId"]
            match_info_proto.is_completed = match_info_list["isCompleted"]
            match_info_proto.custom_name = match_info_list["customGameName"]
            match_info_proto.queue_id = match_info_list["queueId"]
            match_info_proto.game_mode = match_info_list["gameMode"]
            match_info_proto.is_ranked = match_info_list["isRanked"]
            match_info_proto.season_id = match_info_list["seasonId"]
            return match_info_proto

        def populate_teams_info():
            teams = []
            teams_list = match_data["teams"]

            for team in teams_list:
                teams_proto = match_pb2.TeamsInformation()
                teams_proto.team_id = team["teamId"]
                teams_proto.won = team["won"]
                teams_proto.rounds_played = team["roundsPlayed"]
                teams_proto.rounds_won = team["roundsWon"]
                teams_proto.num_points = team["numPoints"]
                teams.append(teams_proto)

            return teams

        def populate_location(field_list):
            field_locations_proto_list = []
            for field_item in field_list:
                field_locations_proto = match_pb2.PlayerLocations()
                field_player_coordinates_proto = match_pb2.LocationInformation()
                field_locations_proto.puu_id = field_item["puuid"]
                field_locations_proto.view_radians = field_item["viewRadians"]
                field_player_coordinates_proto.x = field_item["location"]["x"]
                field_player_coordinates_proto.y = field_item["location"]["y"]
                field_locations_proto.location.CopyFrom(field_player_coordinates_proto)
                field_locations_proto_list.append(field_locations_proto)
            return field_locations_proto_list

        def populate_round_info():
            def field_location(field_name):
                if field_name in round and round[field_name]:
                    field_list = round[field_name]
                    field_locations_proto_list = []  # Create a list to store PlayerLocations protobuf objects
                    field_locations_proto_list = populate_location(field_list)

                    if field_name == "plantPlayerLocations":
                        rounds_proto.plant_player_locations.extend(field_locations_proto_list)
                    elif field_name == "defusePlayerLocations":
                        rounds_proto.defuse_player_locations.extend(field_locations_proto_list)

            rounds = []
            rounds_list = match_data["roundResults"]

            for round in rounds_list:
                rounds_proto = match_pb2.RoundsInformation()
                rounds_proto.round_num = round["roundNum"]
                rounds_proto.round_result = round["roundResult"]
                rounds_proto.round_ceremony = round["roundCeremony"]
                rounds_proto.winning_team = round["winningTeam"]
                if "bombPlanter" in round and round["bombPlanter"]:
                    rounds_proto.bomb_planter = round["bombPlanter"]
                if "bombdefuser" in round and round["bombdefuser"]:
                    rounds_proto.bomb_defuser = round["bombdefuser"]
                rounds_proto.plant_round_time = round["plantRoundTime"]

                def player_stats():
                    stats_list = round["playerStats"]
                    stats_proto_list = []

                    for stats_item in stats_list:
                        stats_proto = match_pb2.PlayerRoundStatsInformation()
                        stats_proto.puu_id = stats_item["puuid"]
                        stats_proto.score = stats_item["score"]
                        kills_proto_list = []

                        kills_list = stats_item["kills"]

                        for kills_item in kills_list:
                            kills_proto = match_pb2.KillsInformation()
                            kills_proto.game_start = kills_item["timeSinceGameStartMillis"]
                            kills_proto.round_start = kills_item["timeSinceRoundStartMillis"]
                            kills_proto.killer = kills_item["killer"]
                            kills_proto.victim = kills_item["victim"]

                            victim_location_proto = match_pb2.LocationInformation()
                            victim_location_proto.x = kills_item["victimLocation"]["x"]
                            victim_location_proto.y = kills_item["victimLocation"]["y"]
                            kills_proto.victim_location.CopyFrom(victim_location_proto)

                            field_list = kills_item["playerLocations"]
                            field_locations_proto_list = populate_location(field_list)
                            kills_proto.player_locations.extend(field_locations_proto_list)

                            damage_proto = match_pb2.FinishingDamageInformation()
                            damage_list = kills_item["finishingDamage"]
                            damage_proto.damage_type = damage_list["damageType"]
                            damage_proto.damage_item = damage_list["damageItem"]
                            damage_proto.is_secondary_fire_mode = damage_list["isSecondaryFireMode"]
                            kills_proto.finishing_damage.CopyFrom(damage_proto)

                            assistant_list = kills_item["assistants"]
                            for assistant in assistant_list:
                                kills_proto.assistants.extend([assistant])

                            kills_proto_list.append(kills_proto)

                        stats_proto.kills.extend(kills_proto_list)
                        stats_proto_list.append(stats_proto)
                    rounds_proto.player_stats.extend(stats_proto_list)

                player_stats()

                field_location("plantPlayerLocations")
                field_location("defusePlayerLocations")

                plant_coordinates_proto = match_pb2.LocationInformation()
                plant_coordinates_proto.x = round["plantLocation"]["x"]
                plant_coordinates_proto.y = round["plantLocation"]["y"]
                rounds_proto.plant_location.CopyFrom(plant_coordinates_proto)

                defuse_coordinates_proto = match_pb2.LocationInformation()
                defuse_coordinates_proto.x = round["defuseLocation"]["x"]
                defuse_coordinates_proto.y = round["defuseLocation"]["y"]
                rounds_proto.defuse_location.CopyFrom(defuse_coordinates_proto)
                rounds_proto.plant_site = round["plantSite"]
                rounds_proto.defuse_round_time = round["defuseRoundTime"]
                rounds_proto.round_result_code = round["roundResultCode"]

                rounds.append(rounds_proto)
            return rounds

        def populate_player_info():
            players = []
            players_list = match_data["players"]

            for player in players_list:
                stats_list = player["stats"]
                stat_proto = match_pb2.PlayerStats()
                stat_proto.score = stats_list["score"]
                stat_proto.rounds_played = stats_list["roundsPlayed"]
                stat_proto.kills = stats_list["kills"]
                stat_proto.deaths = stats_list["deaths"]
                stat_proto.assists = stats_list["assists"]
                stat_proto.play_time = stats_list["playtimeMillis"]

                player_proto = match_pb2.PlayerInformation()
                player_proto.stats.CopyFrom(stat_proto)
                player_proto.puu_id = player["puuid"]

                if "gameName" in player and player["gameName"]:
                    player_proto.game_name = player["gameName"]

                if "tagLine" in player and player["tagLine"]:
                    player_proto.tag_line = player["tagLine"]

                player_proto.team_id = player["teamId"]
                player_proto.party_id = player["partyId"]
                player_proto.character_id = player["characterId"]
                player_proto.competitive_tier = player["competitiveTier"]
                player_proto.player_card = player["playerCard"]
                player_proto.player_title = player["playerTitle"]
                players.append(player_proto)
            return players

        if match_data:
            response_message = riot_ingest_pb2.GetMatchDataResponse()
            match_info_proto = populate_match_info()
            response_message.matches_info.CopyFrom(match_info_proto)

            players_proto = populate_player_info()
            response_message.players_info.extend(players_proto)

            teams_proto = populate_teams_info()
            response_message.teams_info.extend(teams_proto)

            rounds_proto = populate_round_info()
            response_message.rounds_info.extend(rounds_proto)

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

        def populate_proto_response(input_list):
            # Define a dictionary to map input list names to protobuf types
            protobuf_types = {
                "gameModes": riot_ingest_pb2.GameModesInformation,
                "acts": riot_ingest_pb2.ActsInformation,
            }

            characters = []
            character_list = context_data[input_list]

            for character in character_list:
                protobuf_type = protobuf_types.get(input_list, riot_ingest_pb2.GameInformation)
                character_proto = protobuf_type()

                # Common fields
                character_proto.name = character["name"]
                character_proto.player_id = character["id"]

                # Set the specific fields based on the input list
                if input_list == "gameModes":
                    character_proto.asset_path = character["assetPath"]
                    character_proto.asset_name = character["assetName"]
                elif input_list == "acts":
                    character_proto.parent_id = character["parentId"]
                    character_proto.type = character["type"]
                    character_proto.isActive = str(character["isActive"])
                else:
                    character_proto.asset_name = character["assetName"]

                # Set localized_names if character["name"] is not empty
                if character["name"]:
                    response_languages = set_lang(character["localizedNames"], response=riot_ingest_pb2.Languages())
                    character_proto.localized_names.CopyFrom(response_languages)

                characters.append(character_proto)

            return characters

        if context_data:
            response_message = riot_ingest_pb2.GetContentDataResponse()
            characters = populate_proto_response("characters")
            response_message.characters_info.extend(characters)

            maps = populate_proto_response("maps")
            response_message.maps_info.extend(maps)

            chromas = populate_proto_response("chromas")
            response_message.chromas_info.extend(chromas)

            skins = populate_proto_response("skins")
            response_message.skins_info.extend(skins)

            skin_levels = populate_proto_response("skinLevels")
            response_message.skin_levels_info.extend(skin_levels)

            equips = populate_proto_response("equips")
            response_message.skin_levels_info.extend(equips)

            gameModes = populate_proto_response("gameModes")  # DIFFERENT
            response_message.game_modes_info.extend(gameModes)

            sprays = populate_proto_response("sprays")
            response_message.sprays_info.extend(sprays)

            spray_levels = populate_proto_response("sprayLevels")
            response_message.spray_levels_info.extend(spray_levels)

            charms = populate_proto_response("charms")
            response_message.charms_info.extend(charms)

            charm_levels = populate_proto_response("charmLevels")
            response_message.charm_levels_info.extend(charm_levels)

            player_cards = populate_proto_response("playerCards")
            response_message.player_cards_info.extend(player_cards)

            ceremonies = populate_proto_response("ceremonies")
            response_message.ceremonies_info.extend(ceremonies)

            player_titles = populate_proto_response("playerTitles")
            response_message.player_titles_info.extend(player_titles)

            acts = populate_proto_response("acts")  # DIFFERENT
            response_message.acts_info.extend(acts)
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
