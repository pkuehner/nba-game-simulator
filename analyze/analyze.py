import os
import pandas as pd
import json
from nba_api.stats.static import teams as tm


from .eventTypes import eventTypes
import numpy as np
from . import textprocessor
from . import rotation_tools

# Basic Request
import glob

tp = textprocessor.TextProcessor()

files_reg = glob.glob("./games/summary/*.json")
files_pbp = glob.glob("./games/playbyplay/*.json")


def handle_game_time(pcstring, period_change, period_is_ot):
    nums = pcstring.split(":")
    timeSec = int(nums[0]) * 60 + int(nums[1])
    diff = old_game_time - timeSec
    if period_change:
        constant_time = 720
        if period_is_ot:
            constant_time = 300

        if teams["home"] == team:
            stats["home"][str(lineups["home"])]["min"] += constant_time - timeSec
        if teams["away"] == team:
            stats["away"][str(lineups["away"])]["min"] += constant_time - timeSec
    else:
        if teams["home"] == team:
            stats["home"][str(lineups["home"])]["min"] += diff
        if teams["away"] == team:
            stats["away"][str(lineups["away"])]["min"] += diff
    return timeSec


def add_ast(playerId):
    stats[curr_team][str(lineups[curr_team])]["ast"] += 1


def add_lineup_to_stats():
    if not str(lineups[curr_team]) in stats[curr_team]:
        stats[curr_team][str(lineups[curr_team])] = {
            "lineup": lineups[curr_team],
            "2ptm": 0,
            "3ptm": 0,
            "ftm": 0,
            "2pta": 0,
            "3pta": 0,
            "fta": 0,
            "poss": 0,
            "tov": 0,
            "ast": 0,
            "foul_s": 0,
            "foul_reg": 0,
            "d_reb": 0,
            "o_reb": 0,
            "min": 0,
            "subs": 0,
        }


def add_possession():
    stats[curr_team][str(lineups[curr_team])]["poss"] += 1


def add_turnover():
    stats[curr_team][str(lineups[curr_team])]["tov"] += 1


def add_reb():
    reb_type = "d_reb"
    if last_shot_team == curr_team:
        reb_type = "o_reb"
    stats[curr_team][str(lineups[curr_team])][reb_type] += 1


def add_sub(new_lineup):
    stats[curr_team][str(lineups[curr_team])]["subs"] += 1


def add_foul(foul_type):
    if foul_type == "S":
        stats[curr_team][str(lineups[curr_team])]["foul_s"] += 1
    elif "off" not in foul_type.lower():
        stats[curr_team][str(lineups[curr_team])]["foul_reg"] += 1


def add_shot(made, typea, typem):
    stats[curr_team][str(lineups[curr_team])][typea] += 1
    if made:
        stats[curr_team][str(lineups[curr_team])][typem] += 1


games = pd.read_json("games/games_19_20.json")
games = np.unique(games["GAME_ID"])
for team in [team["abbreviation"] for team in tm.get_teams()]:
    stats = {"home": {}, "away": {}}

    for game_id in games:
        game = f"./games/playbyplay/0{game_id}.json"
        game_sum = f"./games/summary/0{game_id}.json"
        game_rot = f"./games/rotation/00{game_id}.json"
        print(game_sum)
        game_data = pd.read_json(game_sum)
        home_team = tm.find_team_name_by_id(game_data.loc[0, "HOME_TEAM_ID"])
        away_team = tm.find_team_name_by_id(game_data.loc[0, "VISITOR_TEAM_ID"])

        if home_team["abbreviation"] != team and away_team["abbreviation"] != team:
            continue

        teams = {"home": home_team["abbreviation"], "away": away_team["abbreviation"]}

        pbp_data = pd.read_json(game)
        x = {}
        starters_by_period = rotation_tools.get_starters_by_period(game_rot, game_sum)
        lineups = {"home": [], "away": []}
        possessions = {"home": {}, "away": {}}
        shots = {
            "home": {"2ptm": 0, "3ptm": 0, "ftm": 0, "2pta": 0, "3pta": 0, "fta": 0},
            "away": {"2ptm": 0, "3ptm": 0, "ftm": 0, "2pta": 0, "3pta": 0, "fta": 0},
        }

        current_period = -1
        old_game_time = 0
        last_shot_team = "neutral"
        curr_team = "neutral"

        for i in range(len(pbp_data["HOMEDESCRIPTION"])):
            current_period_new = pbp_data.loc[i, "PERIOD"] - 1
            play_clock = pbp_data.loc[i, "PCTIMESTRING"]
            period_changed = current_period_new > current_period
            period_is_ot = current_period_new >= 5
            if period_changed:
                last_shot_team = "neutral"
                current_period = current_period_new
                print("Period Start")
                lineups["home"] = sorted(starters_by_period[current_period]["home"])
                lineups["away"] = sorted(starters_by_period[current_period]["away"])
                curr_team = "home"
                if teams[curr_team] == team:
                    add_lineup_to_stats()
                curr_team = "away"
                if teams[curr_team] == team:
                    add_lineup_to_stats()
                curr_team = "neutral"

            old_game_time = handle_game_time(play_clock, period_changed, period_is_ot)

            if pbp_data.loc[i, "HOMEDESCRIPTION"] is not None:
                x["text"] = pbp_data.loc[i, "HOMEDESCRIPTION"]
                curr_team = "home"
            elif pbp_data.loc[i, "VISITORDESCRIPTION"] is not None:
                x["text"] = pbp_data.loc[i, "VISITORDESCRIPTION"]
                curr_team = "away"
            else:
                x["text"] = ""
                continue
            if teams[curr_team] != team:
                continue
            event = tp.process_item(x)
            if event["type"] == eventTypes.SUB:
                playerOutId = pbp_data.loc[i, "PLAYER1_ID"]
                playerInId = pbp_data.loc[i, "PLAYER2_ID"]
                lineup_new = [
                    x if x != playerOutId else int(playerInId)
                    for x in lineups[curr_team]
                ]
                add_sub(lineup_new)
                lineups[curr_team] = lineup_new
                add_lineup_to_stats()
            elif event["type"] == eventTypes.SHOT:
                last_shot_team = curr_team
                add_possession()
                if event["3pa"] == 1:
                    add_shot(event["shot_made"], "3pta", "3ptm")
                else:
                    add_shot(event["shot_made"], "2pta", "2ptm")
                if event["ast_player"] is not None:
                    add_ast(pbp_data.loc[i, "PLAYER2_ID"])
            elif event["type"] == eventTypes.FREE_THROW:
                last_shot_team = curr_team
                add_shot(event["shot_made"], "fta", "ftm")
                if event["fta_ovr"] > 1 and event["fta_no"] == 1:
                    if "technical" not in event["shot_type"].lower():
                        add_possession()

            elif (
                event["type"] == eventTypes.TURNOVER
                or event["type"] == eventTypes.TEAM_TURNOVER
            ):
                add_possession()
                add_turnover()
            elif event["type"] == eventTypes.FOUL:
                add_foul(event["foul_type"])
            elif event["type"] == eventTypes.REBOUND:
                add_reb()
                last_shot_team = "neutral"
            elif event["type"] == eventTypes.TEAM_REBOUND:
                add_reb()
                last_shot_team = "neutral"

    print(stats)
    secs = 0
    for key in stats["away"].keys():
        secs += stats["away"][key]["o_reb"]
    print(secs)
    os.makedirs("processed_stats/", exist_ok=True)
    with open(f"processed_stats/{team}.json", "w") as fp:
        json.dump(stats, fp)
