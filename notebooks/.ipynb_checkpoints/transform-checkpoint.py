import datetime
import numpy as np
import pandas as pd


def apply_get_opponent(team, matches):
    def get_opponent(row):
        id_team = row["id_team"]
        m_round = row["round"]

        all_teams = matches.loc[
            (matches["round"] == m_round)
            & (
                (matches.home_team == id_team)
                | (matches.away_team == id_team)
            ),
            ["home_team", "away_team"]
        ].values[0]

        if len(all_teams) != 2:
            raise Exception("many values for opponent")

        opponent = all_teams[0] if all_teams[1] == id_team else all_teams[1]

        return opponent


    team["id_opponent_team"] = team.apply(lambda row: get_opponent(row), axis=1)
    return team


def apply_check_home(team, matches):
    def is_home_team(row):
        id_team = row["id_team"]
        m_round = row["round"]

        home_team = matches.loc[
            (matches["round"] == m_round)
            & (matches.home_team == id_team)
        ].shape[0] == 1

        return home_team


    team["was_home_team"] = team.apply(lambda row: is_home_team(row), axis=1)
    return team


def apply_winner_check(team, matches):
    def is_winner(row):
        id_team = row["id_team"]
        m_round = row["round"]

        home_team = row["was_home_team"]
        location = "home_team" if home_team else "away_team"

        cond = (matches["round"] == m_round) & (matches[location] == id_team)
        home_win = matches.loc[cond, "home_win"].values[0]
        draw = matches.loc[cond, "draw"].values[0]

        if draw: return False 
        return home_team == home_win

    team["has_won"] = team.apply(lambda row: is_winner(row), axis=1)
    return team

    
def apply_championship_score(team):
    def championship_score(row):
        id_team = row["id_team"]
        m_round = row["round"]

        total = team.loc[
            (team.id_team == id_team)
            & (team["round"] <= m_round),
            'match_points'
        ].values.sum()

        return total

    team["championship_score"] = team.apply(lambda row: championship_score(row), axis=1)
    return team


def apply_match_points(team):
    def match_points(row):
        if row["has_won"]:
            return 3
        if row['draw']:
            return 1
        return 0

    team["match_points"] = team.apply(lambda row: match_points(row), axis=1)
    return team


def apply_check_draw(team, matches):
    def check_draw(row):
        id_team = row["id_team"]
        m_round = row["round"]

        draw = matches.loc[
            (matches["round"] == m_round)
            & (
                (matches.home_team == id_team)
                | (matches.away_team == id_team)
            ),
            "draw"
        ].values[0]

        return draw

    team["was_draw"] = team.apply(lambda row: check_draw(row), axis=1)
    return team


def process_date_columns(team, matches, date_format: str = '%d/%m/%Y - %H:%M'):
    def get_date(row):
        id_team = row["id_team"]
        m_round = row["round"]

        date = matches.loc[
            (matches["round"] == m_round)
            & (
                (matches.home_team == id_team)
                | (matches.away_team == id_team)
            ),
            "date"
        ].values[0]

        return date

    team["date"] = team.apply(lambda row: get_date(row), axis=1)
    
    team["timestamp"] = team.apply(
        lambda row: int(datetime.datetime.strptime(row["date"], date_format).timestamp()),
        axis=1
    )
    
    team["date"] = team.apply(
        lambda row: datetime.datetime.strptime(row["date"], date_format),
        axis=1
    )
    
    team["week_day"] = team.apply(
        lambda row: row["date"].weekday(),
        axis=1
    )
    
    return team


def calcule_championship_position(team):
    
    ids = team.id_team.unique()

    position = 'championship_position'
    team[position] = np.NaN

    for r in range(1, 39):
        df_r = team.loc[team['round'] == r]
        df_r = df_r.sort_values(by='championship_score', ascending=False)
        df_r = df_r.reset_index(drop=True)

        for t in ids:
            team.loc[
                (team.id_team == t)
                & (team['round'] == r),
                position
            ] = df_r.index[df_r.id_team == t].values[0] + 1
    
    return team