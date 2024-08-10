import json
import os
import time
from typing import Any, List, NewType

import pandas as pd
import requests

GameEndpoint = NewType("GameEndpoint", Any)  # There is no typing unfortunately


class RotationEndpoint:
    df: pd.DataFrame

    def __init__(self, game_id: str, timeout: int):
        url = f"https://stats.nba.com/stats/gamerotation?GameID={game_id}&LeagueID=00&RotationStat=PLAYER_PTS"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
            "Host": "stats.nba.com",
            "Referer": f"https://stats.nba.com/game/{game_id}/rotations/",
            "x-nba-stats-origin": "stats",
        }
        # x-nba-stats-token: true}
        response = requests.get(url, headers=headers)
        data = json.loads(response.content)["resultSets"]
        headers = data[0]["headers"]
        rows = data[0]["rowSet"]
        rows1 = data[1]["rowSet"]
        rows.extend(rows1)
        self.df = pd.DataFrame(rows, columns=headers)

    def get_data_frames(self) -> List[pd.DataFrame]:
        return [self.df]


def download_game_data(
    endpoint: Any,
    game_id: str,
    base_folder: str,
    timeout_between_retries=10,
    max_num_retries: int = 5,
):
    num_retries = 0
    os.makedirs(base_folder, exist_ok=True)
    while num_retries < max_num_retries:
        num_retries += 1
        print(f"Downloading {game_id}, Retry {num_retries}/{max_num_retries}")
        try:
            data = endpoint(game_id=game_id, timeout=10)
            data = data.get_data_frames()[0]
            data.to_json(f"{base_folder}/{game_id}.json")
            break
        except Exception as e:
            print(e)
            time.sleep(timeout_between_retries)
