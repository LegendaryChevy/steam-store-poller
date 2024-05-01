import json

def comparer():
    try:
        # Load the dictionaries from the first file into a list
        with open('new_games.json') as f:
            new_games = json.load(f)

        # If new_games is empty, there's nothing to compare
        if not new_games:
            print("No new games to compare.")
            return

    except (FileNotFoundError, json.JSONDecodeError):
        print("Error loading new games.")
        return

    try:
        # Load the dictionaries from the second file into a list
        with open('old_games.json') as f:
            old_games = json.load(f)

    except (FileNotFoundError, json.JSONDecodeError):
        print("Error loading old games.")
        return

    # Convert the old games into a set for faster searching
    old_games_set = set(tuple(game.items()) for game in old_games['applist']['apps'])

    # Create a new list from the new games that excludes any games found in the old games
    new_games['applist']['apps'] = [game for game in new_games['applist']['apps'] if tuple(game.items()) not in old_games_set]

    # Save the pared-down new games list back into the first file
    with open('new_games.json', 'w') as f:
        json.dump(new_games, f)
        print('done comparing.')