import requests
import json

def poll_steam():
    response = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2/')
    data = response.json()

    with open('new_games.json', 'w') as f:
        json.dump(data, f)
        print("done polling.")
