import json
import requests
import os
from mysql.connector import connect, Error
from dotenv import load_dotenv
from steam_store_poller import poll_steam
from ai_description_tool import summarize_text_with_openai 
from games_list_comparer import comparer
from picture_downloader import pic_downloader
import pprint
  
  
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
        # Check if file exists
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

check_and_create_files(['new_games.json', 'old_games.json'])

check_game_data_output(['game_data_output.json'])
poll_steam()

comparer()

#mycursor = mydb.cursor()

with open('new_games.json') as json_file:
    data = json.load(json_file)
    all_games_data = {}
    counter = 0
    for game in data['applist']['apps']:
        vr_tag_present = False
        if counter >= 100:
            
                break
        
        appid = game['appid']
        game_name = game['name']
        game_details = None
        #print(f"Getting details for game {game_name} with appid {appid}")
        
        response = requests.get(f'http://store.steampowered.com/api/appdetails/?appids={appid}')
        url = (f'https://store.steampowered.com/app/{appid}/')

        #print(response.status_code)
        if response.status_code == 200:

            game_data = response.json()

            if str(appid) in game_data and 'data' in game_data[str(appid)]:
                game_details = game_data[str(appid)]['data']   # Accessing the game details

           # if game_details is not None:
            #    print(f"Categories for game {game_name}: {game_details.get('categories', [])}")
             #   print(f"Genres for game {game_name}: {game_details.get('genres', [])}")
            
            exclude_tags = ['Hentai', 'Mature', 'Sexual Content', 'Nudity', 'NSFW', 'Milf', 'sexy', 'Sexy', 'milf', 'sex', 'porn', 'Porn', 'sex', 'Sex', 'sexual', 'Sexual', 'bukkake']  # Define your exclude tags here.

           # Retrieve detailed_description or about_the_game
            try:
                if game_details is not None:
                    bad_description = game_details.get('detailed_description') or game_details.get('about_the_game')
                else:
                    bad_description = 'this is ok'
                    #print(f'{game_name} has no game details')
            except Exception as e:
                print(f'There was an error: {str(e)}')

            # Split words if description is not None
            if bad_description is not None:
                words = bad_description.split()
            else:
                words = []

            if game_details is not None and game_details.get('type') == 'game':
                vr_tag_present = any([category.get('description', '') == "VR Only" or category.get('description', '') == "VR Supported" and category.get('description', '') not in exclude_tags 
                              for category in game_details.get('categories', [])]) or \
                        any([genre.get('description', '') == 'VR Only' or genre.get('description', '') == 'VR Supported' and genre.get('description', '') not in exclude_tags
                             for genre in game_details.get('genres', [])])
                               
                               
            if not any(word in exclude_tags for word in words):
                                                           
                            
                if vr_tag_present:
                    game_details['url'] = url  # Storing the URL in the game details

                    all_games_data[appid] = game_data

                    pic_downloader(game_name, game_details['screenshots'])
                    strip_keys(all_games_data[appid], keys_to_strip)
               
                    # print(f"VR tag found for game {game_name} with appid {appid}")
                    print(f"game #{counter}:{game_name} is vr")
                
                

                #pprint.pprint(game_details)
                if game_details is not None and 'detailed_description' in game_details:
                    #print('game detailed_description found')
                    description = game_details['detailed_description']
                    try:
                        summarized_description = summarize_text_with_openai(description)
                        game_details['ai_description'] = summarized_description
                    except Exception as e:
                        print(f"Error during description summarization: {e}")
                        summarized_description = None

                    with open('game_data_output.json', 'r') as f:
                        existing_data = json.load(f)
                        existing_data.update(all_games_data)
                
                    with open('game_data_output.json', 'w') as f:
                        json.dump(existing_data, f, indent=4)
                        all_games_data = {}
                #else: 
                    #print(f'game#{counter+1}:{game_name} is not a vr')
                        
        else:
            print(f"Request failed for appid:{appid}")
            print(response.status_code)
    
        
        # Check if the game has a 'VR' tag in categories or genres
        
        # Load new games
        with open('new_games.json', 'r') as f:
            new_games = json.load(f)

        # Load old games
        with open('old_games.json', 'r') as f:
            old_games = json.load(f)

        #Add new games to old games
        old_games['applist']['apps'].extend(new_games['applist']['apps'][:1])

        # Write the updated old games back to old_games.json
        with open('old_games.json', 'w') as f:
            json.dump(old_games, f)
        
        # Remove the processed game from the 'new_games'
        new_games['applist']['apps'].pop(0)

        # Write the updated new games back to new_games.json
        with open('new_games.json', 'w') as f:
            json.dump(new_games, f)
        
    
        
        counter += 1


