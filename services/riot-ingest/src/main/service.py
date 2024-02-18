"""Riot Ingest Service.

This module implements the Riot Ingest service, responsible for processing and ingesting data
from the Riot Games API.

Note:
Ensure the correct Riot Games API key is provided for seamless data ingestion.
"""

from concurrent import futures
import logging
import os
from typing import Any, Dict, List

import grpc
from protobufs.common.v1 import match_pb2
from protobufs.services.v1 import riot_ingest_pb2, riot_ingest_pb2_grpc
from service_common.http_util import request_get
from service_common.service_logging import init_logging, log_and_flush


RIOT_API_URL = "http://mockserver:1080"
RIOT_API_KEY_FILE = "/run/secrets/riot-api-key"

MATCH_DATA_ENDPOINT = f"{RIOT_API_URL}/val/match/v1/matches/{{match_id}}"
ACCOUNT_DATA_ENDPOINT = (
    f"{RIOT_API_URL}/account/v1/accounts/by-riot-id/{{game_name}}/{{tag_line}}"
)
MATCH_LIST_DATA_ENDPOINT = f"{RIOT_API_URL}/val/match/v1/matchlists/by-puuid/{{puuid}}"
CONTENT_DATA_ENDPOINT = f"{RIOT_API_URL}/val/content/v1/contents"
LEADERBOARD_DATA_ENDPOINT = (
    f"{RIOT_API_URL}/val/ranked/v1/leaderboards/by-act/{{act_id}}"
)


class RiotIngestServicer(riot_ingest_pb2_grpc.RiotIngestService):
    """gRPC Service for Riot Ingest.

    The RiotIngestServicer class handles incoming requests and provides game statistics
    and relevant information to the application.

    This class fetches data from the Riot Games API and seamlessly organizes
    it into protobufs for our application's components
    """

    def __init__(self) -> None:
        """Initialize the RiotIngestServicer."""
        with open(RIOT_API_KEY_FILE) as riot_key_file:
            self.riot_api_key = riot_key_file.read()

    def GetMatchData(
        self,
        request: riot_ingest_pb2.GetMatchDataRequest,
        context: grpc.ServicerContext,
    ) -> riot_ingest_pb2.GetMatchDataResponse:
        """Fetches match data from Riot Games API and returns the retrieved data.

        Args:
            request (riot_ingest_pb2.GetMatchDataRequest): gRPC request containing the match ID.
            context (grpc.ServicerContext): gRPC service context.

        Returns:
            riot_ingest_pb2.GetMatchDataResponse: gRPC response containing the retrieved match data.
        """
        url = MATCH_DATA_ENDPOINT.format(match_id=request.match_id)
        headers = {"X-Riot-Token": self.riot_api_key}
        match_data = request_get(url, context, headers)

        if match_data is None:
            context.abort(context.code(), context.details())

        response_message = riot_ingest_pb2.GetMatchDataResponse()
        match_info_proto = self._populate_match_info(match_data)
        response_message.match.matches_info.CopyFrom(match_info_proto)

        players_proto = self._populate_player_info(match_data)
        response_message.match.players_info.extend(players_proto)

        teams_proto = self._populate_teams_info(match_data)
        response_message.match.teams_info.extend(teams_proto)

        rounds_proto = self._populate_round_info(match_data)
        response_message.match.rounds_info.extend(rounds_proto)

        return response_message

    def _populate_player_info(
        self, match_data: Dict[str, Any]
    ) -> List[match_pb2.PlayerData]:
        """Populates a list of protobuf messages for player information based on the provided match data.

        Args:
            match_data (Dict[str, Any]): Dictionary containing match data.

        Returns:
            List[match_pb2.PlayerData]: List of protobuf messages for player information.
        """
        players = []

        for player in match_data["players"]:
            stat_proto = match_pb2.PlayerStats()
            stats_list = player["stats"]
            stat_proto.score = stats_list["score"]
            stat_proto.rounds_played = stats_list["roundsPlayed"]
            stat_proto.kills = stats_list["kills"]
            stat_proto.deaths = stats_list["deaths"]
            stat_proto.assists = stats_list["assists"]
            stat_proto.play_time = stats_list["playtimeMillis"]

            player_proto = match_pb2.PlayerData()
            player_proto.stats.CopyFrom(stat_proto)
            player_proto.puuid = player["puuid"]

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

    def _populate_match_info(self, match_data: Dict[str, Any]) -> match_pb2.MatchData:
        """Populates a protobuf message for match information based on the provided match data.

        Args:
            match_data (Dict[str, Any]): Dictionary containing match data.

        Returns:
            match_pb2.MatchData: Protobuf message for match information.
        """
        match_info_proto = match_pb2.MatchData()
        match_info_list = match_data["matchInfo"]
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

    def _populate_teams_info(
        self, match_data: Dict[str, Any]
    ) -> List[match_pb2.TeamData]:
        """Populates a list of protobuf messages for team information based on the provided match data.

        Args:
            match_data(Dict[str, Any]): The dictionary containing match data.

        Returns:
            List[match_pb2.TeamData]: List of protobuf messages for team information.
        """
        return [
            match_pb2.TeamData(
                team_id=team["teamId"],
                won=team["won"],
                rounds_played=team["roundsPlayed"],
                rounds_won=team["roundsWon"],
                num_points=team["numPoints"],
            )
            for team in match_data["teams"]
        ]

    def _populate_location(
        self, field_list: List[Any]
    ) -> List[match_pb2.PlayerLocations]:
        """Populates a list of protobuf messages for player locations based on the provided field list.

        Args:
            field_list (List[Any]): The list containing player location information.

        Returns:
            List[match_pb2.PlayerLocations]: List of protobuf messages for player locations.
        """
        return [
            match_pb2.PlayerLocations(
                puuid=field_item["puuid"],
                view_radians=field_item["viewRadians"],
                location=match_pb2.LocationData(
                    x=field_item["location"]["x"], y=field_item["location"]["y"]
                ),
            )
            for field_item in field_list
        ]

    def _field_location(
        self,
        round_item: Dict[str, Any],
        rounds_proto: match_pb2.RoundsData,
        field_name: str,
    ) -> None:
        """Processes location field in a round and extends the corresponding field in protobuf message.

        Args:
            round_item (Dict[str, Any]): The dictionary containing round information.
            rounds_proto (match_pb2.RoundsData): The protobuf message for round information.
            field_name (str): The name of the field.

        Returns:
            None
        """
        if field_name in round_item and round_item[field_name]:
            field_locations_proto_list = self._populate_location(round_item[field_name])

            if field_name == "plantPlayerLocations":
                rounds_proto.plant_player_locations.extend(field_locations_proto_list)
            elif field_name == "defusePlayerLocations":
                rounds_proto.defuse_player_locations.extend(field_locations_proto_list)

    def _player_stats(
        self, stats_list: List[Dict[str, Any]]
    ) -> List[match_pb2.PlayerRoundStatsData]:
        """Returns a list of corresponding protobuf messages.

        Args:
            stats_list (List[Dict[str, Any]]): The list containing player stats.

        Returns:
            List[match_pb2.PlayerRoundStatsData]: List of protobuf messages for player stats.
        """
        stats_proto_list = []

        for stats_item in stats_list:
            stats_proto = match_pb2.PlayerRoundStatsData()
            stats_proto.puuid = stats_item["puuid"]
            stats_proto.score = stats_item["score"]

            damage_proto_list = []
            damage_list = stats_item["damage"]

            for damage_item in damage_list:
                damage_proto = match_pb2.DamageData()
                damage_proto.receiver = damage_item["receiver"]
                damage_proto.damage = damage_item["damage"]
                damage_proto.leg_shots = damage_item["legshots"]
                damage_proto.body_shots = damage_item["bodyshots"]
                damage_proto.head_shots = damage_item["headshots"]
                damage_proto_list.append(damage_proto)

            stats_proto.damage.extend(damage_proto_list)

            economy_proto = match_pb2.EconomyData()
            economy_list = stats_item["economy"]
            economy_proto.loadout_value = economy_list["loadoutValue"]
            economy_proto.weapon = economy_list["weapon"]
            economy_proto.armor = economy_list["armor"]
            economy_proto.remaining = economy_list["remaining"]
            economy_proto.spent = economy_list["spent"]

            stats_proto.economy.CopyFrom(economy_proto)

            kills_proto_list = []
            kills_list = stats_item["kills"]

            for kills_item in kills_list:
                kills_proto = match_pb2.KillData()
                kills_proto.game_start = kills_item["timeSinceGameStartMillis"]
                kills_proto.round_start = kills_item["timeSinceRoundStartMillis"]
                kills_proto.killer = kills_item["killer"]
                kills_proto.victim = kills_item["victim"]

                victim_location_proto = match_pb2.LocationData()
                victim_location_proto.x = kills_item["victimLocation"]["x"]
                victim_location_proto.y = kills_item["victimLocation"]["y"]
                kills_proto.victim_location.CopyFrom(victim_location_proto)

                field_list = kills_item["playerLocations"]
                field_locations_proto_list = self._populate_location(field_list)
                kills_proto.player_locations.extend(field_locations_proto_list)

                damage_proto = match_pb2.FinishingDamageData()
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

        return stats_proto_list

    def _populate_round_info(
        self, match_data: Dict[str, Any]
    ) -> List[match_pb2.RoundsData]:
        """Populates protobuf messages for round information based on the provided match data.

        Args:
            match_data (Dict[str, Any]): The dictionary containing match data.

        Returns:
            List[match_pb2.RoundsData]: List of populated protobuf messages for round information.
        """
        rounds_list = []

        for round_item in match_data["roundResults"]:
            rounds_proto = match_pb2.RoundsData()
            rounds_proto.round_num = round_item["roundNum"]
            rounds_proto.round_result = round_item["roundResult"]
            rounds_proto.round_ceremony = round_item["roundCeremony"]
            rounds_proto.winning_team = round_item["winningTeam"]
            if "bombPlanter" in round_item and round_item["bombPlanter"]:
                rounds_proto.bomb_planter = round_item["bombPlanter"]
            if "bombdefuser" in round_item and round_item["bombdefuser"]:
                rounds_proto.bomb_defuser = round_item["bombdefuser"]
            rounds_proto.plant_round_time = round_item["plantRoundTime"]
            rounds_proto.round_result_code = round_item["roundResultCode"]

            player_stats = round_item["playerStats"]
            rounds_proto.player_stats.extend(self._player_stats(player_stats))
            self._field_location(round_item, rounds_proto, "plantPlayerLocations")
            self._field_location(round_item, rounds_proto, "defusePlayerLocations")

            plant_coordinates_proto = match_pb2.LocationData()
            plant_coordinates_proto.x = round_item["plantLocation"]["x"]
            plant_coordinates_proto.y = round_item["plantLocation"]["y"]
            rounds_proto.plant_location.CopyFrom(plant_coordinates_proto)

            defuse_coordinates_proto = match_pb2.LocationData()
            defuse_coordinates_proto.x = round_item["defuseLocation"]["x"]
            defuse_coordinates_proto.y = round_item["defuseLocation"]["y"]
            rounds_proto.defuse_location.CopyFrom(defuse_coordinates_proto)
            rounds_proto.plant_site = round_item["plantSite"]
            rounds_proto.defuse_round_time = round_item["defuseRoundTime"]
            rounds_proto.round_result_code = round_item["roundResultCode"]

            rounds_list.append(rounds_proto)

        return rounds_list

    def GetAccountByRiotID(
        self,
        request: riot_ingest_pb2.GetAccountByRiotIDRequest,
        context: grpc.ServicerContext,
    ) -> riot_ingest_pb2.GetAccountByRiotIDResponse:
        """Fetch account data from Riot Games API and return the retrieved data.

        Args:
            request (riot_ingest_pb2.GetAccountByRiotIDRequest): The request containing game_name and tag_line.
            context (grpc.ServicerContext): gRPC servicer context.

        Returns:
            riot_ingest_pb2.GetAccountByRiotIDResponse: The response containing account information.
        """
        url = ACCOUNT_DATA_ENDPOINT.format(
            game_name=request.game_name, tag_line=request.tag_line
        )

        headers = {"X-Riot-Token": self.riot_api_key}
        account_data = request_get(url, context, headers)

        if account_data is None:
            context.abort(context.code(), context.details())

        response_message = riot_ingest_pb2.GetAccountByRiotIDResponse()
        response_message.puuid = account_data["puuid"]
        return response_message

    def GetPlayerMatches(
        self,
        request: riot_ingest_pb2.GetPlayerMatchesRequest,
        context: grpc.ServicerContext,
    ) -> riot_ingest_pb2.GetPlayerMatchesResponse:
        """Fetches match data for a player from the Riot Games API.

        Args:
            request (riot_ingest_pb2.GetPlayerMatchesRequest): The request object containing
                the player's PUU ID.
            context (grpc.ServicerContext): The context for the gRPC service.

        Returns:
            riot_ingest_pb2.GetPlayerMatchesResponse: The response containing the player's match history.

        Raises:
            grpc.RpcError: An error occurred during the gRPC call.

        """
        url = MATCH_LIST_DATA_ENDPOINT.format(puuid=request.puuid)
        headers = {"X-Riot-Token": self.riot_api_key}
        match_data = request_get(url, context, headers)

        if match_data is None:
            context.abort(context.code(), context.details())

        response_message = riot_ingest_pb2.GetPlayerMatchesResponse()
        response_message.history.extend(
            [
                riot_ingest_pb2.PlayersMatches(
                    match_id=match["matchId"],
                    game_start_time=match["gameStartTimeMillis"],
                    queue_id=match["queueId"],
                )
                for match in match_data["history"]
            ]
        )
        return response_message

    def GetContentData(
        self,
        request: riot_ingest_pb2.GetContentDataRequest,
        context: grpc.ServicerContext,
    ) -> riot_ingest_pb2.GetContentDataResponse:
        """Fetches content data from Riot Games API and returns the retrieved data.

        Args:
            request (riot_ingest_pb2.GetContentDataRequest): The gRPC request object.
            context (grpc.ServicerContext): The gRPC servicer context.

        Returns:
            riot_ingest_pb2.GetContentDataResponse: The gRPC response object containing content data.
        """
        url = CONTENT_DATA_ENDPOINT
        headers = {"X-Riot-Token": self.riot_api_key}
        context_data = request_get(url, context, headers)

        if context_data is None:
            context.abort(context.code(), context.details())

        response_message = riot_ingest_pb2.GetContentDataResponse()
        characters = self._populate_proto_response(context_data, "characters")
        response_message.characters_info.extend(characters)

        maps = self._populate_proto_response(context_data, "maps")
        response_message.maps_info.extend(maps)

        chromas = self._populate_proto_response(context_data, "chromas")
        response_message.chromas_info.extend(chromas)

        skins = self._populate_proto_response(context_data, "skins")
        response_message.skins_info.extend(skins)

        skin_levels = self._populate_proto_response(context_data, "skinLevels")
        response_message.skin_levels_info.extend(skin_levels)

        equips = self._populate_proto_response(context_data, "equips")
        response_message.skin_levels_info.extend(equips)

        game_modes = self._populate_proto_response(context_data, "gameModes")
        response_message.game_modes_info.extend(game_modes)

        sprays = self._populate_proto_response(context_data, "sprays")
        response_message.sprays_info.extend(sprays)

        spray_levels = self._populate_proto_response(context_data, "sprayLevels")
        response_message.spray_levels_info.extend(spray_levels)

        charms = self._populate_proto_response(context_data, "charms")
        response_message.charms_info.extend(charms)

        charm_levels = self._populate_proto_response(context_data, "charmLevels")
        response_message.charm_levels_info.extend(charm_levels)

        player_cards = self._populate_proto_response(context_data, "playerCards")
        response_message.player_cards_info.extend(player_cards)

        ceremonies = self._populate_proto_response(context_data, "ceremonies")
        response_message.ceremonies_info.extend(ceremonies)

        player_titles = self._populate_proto_response(context_data, "playerTitles")
        response_message.player_titles_info.extend(player_titles)

        acts = self._populate_proto_response(context_data, "acts")
        response_message.acts_info.extend(acts)
        return response_message

    def _set_lang(
        self, character: Dict[str, str], response: riot_ingest_pb2.Languages
    ) -> riot_ingest_pb2.Languages:
        """Sets language values in the provided `response` proto based on the given `character` dictionary.

        Args:
            character (Dict[str, str]): A dictionary containing language codes as keys and corresponding values.
            response (riot_ingest_pb2.Languages): A protobuf message representing language settings.

        Returns:
            riot_ingest_pb2.Languages: The modified `response` proto with language values set.
        """
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

    def _populate_proto_response(
        self, context_data: Dict[str, Any], input_list: str
    ) -> List[riot_ingest_pb2.GameData]:
        """Populates a protobuf response with data from the input list.

        Args:
            context_data (Dict[str, Any]): Dictionary containing context data.
            input_list (str): Name of the input list.

        Returns:
            List[riot_ingest_pb2.GameData]: List of populated protobuf messages.
        """
        protobuf_types = {
            "gameModes": riot_ingest_pb2.GameModesData,
            "acts": riot_ingest_pb2.ActsData,
        }

        characters = []

        for character in context_data[input_list]:
            protobuf_type = protobuf_types.get(input_list, riot_ingest_pb2.GameData)
            character_proto = protobuf_type()
            character_proto.name = character["name"]
            character_proto.player_id = character["id"]

            if input_list == "gameModes":
                character_proto.asset_path = character["assetPath"]
                character_proto.asset_name = character["assetName"]
            elif input_list == "acts":
                character_proto.parent_id = character["parentId"]
                character_proto.type = character["type"]
                character_proto.is_active = str(character["isActive"])
            else:
                character_proto.asset_name = character["assetName"]

            if character["name"]:
                response_languages = self._set_lang(
                    character["localizedNames"],
                    response=riot_ingest_pb2.Languages(),
                )
                character_proto.localized_names.CopyFrom(response_languages)

            characters.append(character_proto)
        return characters

    def GetLeaderboardData(
        self,
        request: riot_ingest_pb2.GetLeaderboardDataRequest,
        context: grpc.ServicerContext,
    ) -> riot_ingest_pb2.GetLeaderboardDataResponse:
        """Fetches leaderboard data from Riot Games API.

        Args:
            request (riot_ingest_pb2.GetLeaderboardDataRequest): gRPC request containing the act_id.
            context (grpc.ServicerContext): gRPC servicer context.

        Returns:
            riot_ingest_pb2.GetLeaderboardDataResponse: gRPC response containing the leaderboard data.
        """
        url = LEADERBOARD_DATA_ENDPOINT.format(
            act_id=(riot_ingest_pb2.ActId.Name(request.act_id))
        )
        headers = {"X-Riot-Token": self.riot_api_key}
        leaderboard_data = request_get(url, context, headers)

        if leaderboard_data is None:
            context.abort(context.code(), context.details())

        response_message = riot_ingest_pb2.GetLeaderboardDataResponse()
        response_message.act_id = leaderboard_data["actId"]
        response_message.shard = leaderboard_data["shard"]
        response_message.total_players = leaderboard_data["totalPlayers"]
        response_message.players.extend(
            [
                riot_ingest_pb2.PlayerDto(
                    puuid=player["puuid"],
                    game_name=player["gameName"],
                    tag_line=player["tagLine"],
                    leaderboard_rank=player["leaderboardRank"],
                    ranked_rating=player["rankedRating"],
                    number_of_wins=player["numberOfWins"],
                )
                for player in leaderboard_data["players"]
            ]
        )

        return response_message


def serve() -> None:
    """Starts the Riot Ingest service and waits for termination.

    This function sets up a gRPC server, adds the RiotIngestServicer to it, starts the server,
    and waits for termination.

    Returns:
        None
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    riot_ingest_pb2_grpc.add_RiotIngestServiceServicer_to_server(
        RiotIngestServicer(), server
    )
    server.add_insecure_port(f"[::]:{ os.environ['RIOT_INGEST_SERVICE_PORT'] }")
    log_and_flush(logging.INFO, "Starting Riot Ingest service...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    init_logging()
    serve()
