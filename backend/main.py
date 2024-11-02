import os
from dataclasses import dataclass

import dotenv
import numpy as np
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd

@dataclass
class UserVote:
    tickets: int
    uri: str


def get_db():
    uri = os.environ.get("MONGO_URI")
    client = MongoClient(uri, server_api=ServerApi("1"))
    client.admin.command("ping")
    return client


def choose_next_song(votes: UserVote):
    df = pd.DataFrame(votes)
    # TODO: Calculate tickets
    total_tickets = df["tickets"].sum()
    df["probability"] = df["tickets"] / total_tickets
    song_uri = np.random.choice(df["uri"], 1, p=df["probability"])[0]
    return str(song_uri)


def main():
    dotenv.load_dotenv()
    client = get_db()
    votes = [UserVote(1, "test"), UserVote(1, "test2"), UserVote(2, "test3")]
    print(choose_next_song(votes))


if __name__ == "__main__":
    main()
