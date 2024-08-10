import os
import numpy as np
from scrape.util import download_game_data, RotationEndpoint
from nba_api.stats.endpoints import playbyplayv2, boxscoresummaryv2, GameRotation

from nba_api.stats.endpoints import leaguegamefinder

data = leaguegamefinder.LeagueGameFinder(
    season_nullable="2019-20",
    season_type_nullable="Regular Season",
    league_id_nullable="00",
)
data = data.get_data_frames()[0]
os.makedirs("./games", exist_ok=True)
data.to_json("./games/games_19_20.json")

games = np.unique(data["GAME_ID"])
for game in games:
    download_game_data(playbyplayv2.PlayByPlayV2, game, "games/playbyplay")
    download_game_data(boxscoresummaryv2.BoxScoreSummaryV2, game, "games/summary")
    download_game_data(RotationEndpoint, game, "games/rotation")
