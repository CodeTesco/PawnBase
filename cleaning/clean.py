import pandas as pd
from pathlib import Path

# matches
matches_path = Path(__file__).resolve().parents[1] / "datasets" / "raw" / "matches.csv"
matches = pd.read_csv(matches_path)

unique_matches = matches.dropna(subset=["white_id", "black_id"], how="all")

unique_matches['white_id'] = unique_matches['white_id'].astype('Int64')
unique_matches['black_id'] = unique_matches['white_id'].astype('Int64')
unique_matches['white_rtg'] = unique_matches['white_rtg'].astype('Int64')
unique_matches['black_rtg'] = unique_matches['white_rtg'].astype('Int64')

unique_matches.to_csv(Path(__file__).resolve().parents[1] / "datasets" / "cleaned" / "unique_matches.csv", index=False)

# players
players_path = Path(__file__).resolve().parents[1] / "datasets" / "raw" / "players.csv"
players = pd.read_csv(players_path)

unique_players = players.dropna(subset=["player_id", "name"])

unique_players['standard_rating'] = unique_players['standard_rating'].astype('Int64')
unique_players['blitz_rating'] = unique_players['blitz_rating'].astype('Int64')
unique_players['rapid_rating'] = unique_players['rapid_rating'].astype('Int64')

unique_players.to_csv(Path(__file__).resolve().parents[1] / "datasets" / "cleaned" / "unique_players.csv", index=False)

# tournaments
tournament_path = Path(__file__).resolve().parents[1] / "datasets" / "raw" / "tournaments.csv"
tournaments = pd.read_csv(tournament_path)

unique_tournaments = tournaments.dropna(subset=["tourney_name"])
unique_tournaments['base_minutes'] = unique_tournaments['base_minutes'].astype('Int64')

unique_tournaments.to_csv(Path(__file__).resolve().parents[1] / "datasets" / "cleaned" / "unique_tournaments.csv", index=False)