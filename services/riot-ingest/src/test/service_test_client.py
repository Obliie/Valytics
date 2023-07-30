import logging
import os

import grpc

riot_ingest_pb2, riot_ingest_pb2_grpc = grpc.protos_and_services("services/riot_ingest.proto")


def run() -> None:
    print("Trying to get match data...")
    with grpc.insecure_channel(f"172.199.0.1:{ os.environ['RIOT_INGEST_SERVICE_PORT' ]}") as channel:
        stub = riot_ingest_pb2_grpc.RiotIngestStub(channel)
        response = stub.GetMatchData(riot_ingest_pb2.MatchDataRequest(matchId="someId"))
    print(f"Match data received for { response.matchId }. Data: { response.response }")


if __name__ == "__main__":
    logging.basicConfig()
    run()
