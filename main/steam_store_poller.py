import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def poll_steam():
    try:
        response = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2/')
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        with open(f'{os.getenv("APP_PATH")}/data/new_games.json', 'w') as f:
            json.dump(data, f)
            print("Done polling.")
    except requests.exceptions.RequestException as e:
        print(f"Error while polling Steam API: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    poll_steam()
