import json
import requests
import os
from dotenv import load_dotenv
from steam_store_poller import poll_steam
from ai_description_tool import summarize_text_with_openai
from games_list_comparer import comparer
from picture_downloader import pic_downloader
import time
from requests_ip_rotator import ApiGateway
import random

# Load environment variables
load_dotenv()

def strip_keys(data, keys_to_strip):
    if isinstance(data, dict):
        for key in keys_to_strip:
            if key in data:
                del data[key]
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = strip_keys(value, keys_to_strip)
    return data

keys_to_strip = ['type', 'capsule_image', 'capsule_imagev5', 'mac_requirements', 'linux_requirements', 'packages', 'package_groups']

def check_and_create_files(file_names: list):
    basic_structure = {"applist": {"apps": []}}

    for name in file_names:
        # Check if file exists
        if os.path.isfile(name):
            with open(name, 'r') as f:
                # Load existing data
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    # If file does not contain valid JSON, overwrite with basic structure
                    data = basic_structure

                # Check if data has basic structure
                if "applist" not in data or "apps" not in data.get("applist", {}):
                    # If basic structure is not present, add it
                    data["applist"] = {"apps": []}

            # Write updated data to file
            with open(name, 'w') as f:
                json.dump(data, f)
        else:
            # If the file does not exist, create it with the basic structure
            with open(name, 'w') as f:
                json.dump(basic_structure, f)

def check_game_data_output(file_names: list):
    basic_structure = {}

    for name in file_names:
        # Check iffile exists
        if os.path.isfile(name):
           with open(name, 'r') as f:
                # Load existing data
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    # If file does not contain valid JSON, overwrite with basic structure
                    data = basic_structure

                # Check if game_data_output has empty dict
                if "{}" in str(data.get("game_data_output")):
                    print(f"Empty dictionary found in game_data_output within {name}")

           with open(name, 'w') as f:
               json.dump(data, f)
        else:
            # If the file does not exist, create it with the basic structure
            with open(name, 'w') as f:
                json.dump(basic_structure, f)

def fetch_steam_app_details(appid, session):
    url = f'http://store.steampowered.com/api/appdetails/?appids={appid}'
    print(f"Fetching details for URL: {url}")

    base_delay = 1  # initial delay in seconds
    max_retries = 5

    for attempt in range(max_retries):
        try:
            #print(f"Attempt {attempt + 1}: Making request to {url}")
            response = session.get(url)
            #print(f"Response URL: {response.url}")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limited. Waiting for {delay:.2f} seconds before retrying...")
                time.sleep(delay)
                continue
            elif response.status_code == 400:
                print(f"Request failed for appid:{appid}, status code: {response.status_code}")
                print(f"Response content: {response.content.decode('utf-8')}")
                break
            else:
                print(f"Request failed for appid:{appid}, status code: {response.status_code}")
                print(f"Response content: {response.content.decode('utf-8')}")
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt+1} failed for appid:{appid}: {e}")
        time.sleep(base_delay)  # Wait for base delay before retrying

    print(f"Failed to retrieve app details for appid:{appid} after {max_retries} attempts")
    return None

def load_non_vr_list(file_path):
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            return set(f.read().splitlines())
    return set()

def append_to_non_vr_list(file_path, appid):
    with open(file_path, 'a') as f:
        f.write(f"{appid}\n")

# Initialize the API Gateway for IP rotation outside the function
url = 'http://store.steampowered.com/api/appdetails/'
gateway = ApiGateway(url, access_key_id=os.getenv('AWS_ACCESS_KEY'), access_key_secret=os.getenv('AWS_SECRET_KEY'))
gateway.start()

# Print the endpoints to check if they are correct
#print("API Gateway endpoints:", gateway.endpoints)

session = requests.Session()

# Ensure each specific URL is mounted individually
for endpoint in gateway.endpoints:
    session.mount(endpoint, gateway)

# Check if the session is properly mounted
#print("Session adapters:", session.adapters)

check_and_create_files(['new_games.json', 'old_games.json'])
check_game_data_output(['game_data_output.json'])
poll_steam()
comparer()

# Load new games
with open('new_games.json') as json_file:
    new_games = json.load(json_file)

# Load old games
with open('old_games.json') as json_file:
    old_games = json.load(json_file)

# Load known non-VR app IDs
non_vr_file = 'non_vr_app_ids.txt'
non_vr_app_ids = load_non_vr_list(non_vr_file)

all_games_data = {}
counter = 0

for game in new_games['applist']['apps']:

    if counter >= 10:
        break

    appid = game['appid']
    if str(appid) in non_vr_app_ids:
        print(f"Skipping known non-vr game {appid}")
        continue

    game_name = game['name']
    game_details = None
    print(f"Getting details for game {game_name} with appid {appid}")

    game_data = fetch_steam_app_details(appid, session)
    if game_data is None:
        non_vr_app_ids.add(str(appid))
        append_to_non_vr_list(non_vr_file, appid)
        continue

    if str(appid) in game_data and 'data' in game_data[str(appid)]:
        game_details = game_data[str(appid)]['data']  # Accessing the game details

    exclude_tags = ['Hentai', 'Lust', 'Mature', 'Sexual Content', 'Nudity', 'NSFW', 'Milf', 'sexy', 'Sexy', 'milf', 'sex', 'porn', 'Porn', 'sex', 'Sex', 'sexual', 'Sexual', 'bukkake']

    vr_tag_present = False
    try:
        if game_details is not None:
            bad_description = game_details.get('detailed_description') or game_details.get('about_the_game')
        else:
            bad_description = 'this is ok'
    except Exception as e:
        print(f'There was an error: {str(e)}')

    if bad_description is not None:
        words = bad_description.split()
    else:
        words = []

    if game_details is not None and game_details.get('type') == 'game':
        vr_tag_present = any([category.get('description', '') == "VR Only" or category.get('description', '') == "VR Supported" and category.get('description', '') not in exclude_tags
                              for category in game_details.get('categories', [])]) or \
                        any([genre.get('description', '') == 'VR Only' or genre.get('description', '') == 'VR Supported' and genre.get('description', '') not in exclude_tags
                             for genre in game_details.get('genres', [])])

    if not any(word in exclude_tags for word in words) and vr_tag_present:
        game_details['url'] = f'https://store.steampowered.com/app/{appid}/'  # Storing the URL in the game details

        all_games_data[appid] = game_data

        if game_details.get('screenshots'):
            pic_downloader(game_name, game_details['screenshots'])
        else:
            print('no screenshots')

        strip_keys(all_games_data[appid], keys_to_strip)

        print(f"game #{counter}:{game_name} is vr")
        counter += 1

        if game_details is not None and 'detailed_description' in game_details:
            description = game_details['detailed_description']
            try:
                summarized_description = summarize_text_with_openai(description)
                game_details['ai_description'] = summarized_description
            except Exception as e:
                print(f"Error during description summarization: {e}")
                summarized_description = None
    else:
        non_vr_app_ids.add(str(appid))
        append_to_non_vr_list(non_vr_file, appid)

# Write the updated old games back to old_games.json
old_games['applist']['apps'].extend(new_games['applist']['apps'])
with open('old_games.json', 'w') as f:
    json.dump(old_games, f)

# Clear new_games.json as all games have been processed
with open('new_games.json', 'w') as f:
    json.dump({"applist": {"apps": []}}, f)

# Save all game data to game_data_output.json
with open('game_data_output.json', 'r') as f:
    existing_data = json.load(f)
    existing_data.update(all_games_data)

with open('game_data_output.json', 'w') as f:
    json.dump(existing_data, f, indent=4)

print('done dumping')
