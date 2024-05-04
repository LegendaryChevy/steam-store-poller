import json
import requests
import time
import os
import mysql.connector
from mysql.connector import connect, Error
from dotenv import load_dotenv
import re
from steam_store_poller import poll_steam
from ai_description_tool import summarize_text_with_openai 
from games_list_comparer import comparer

   # Load environment variables
load_dotenv()

# Retrieve database credentials
db_config = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': os.getenv('MYSQL_HOST'),
    'database': os.getenv('MYSQL_DB'),
}

try:
    # Establishing the connection
    mysql_client = connect(**db_config)
    print('Successfully connected to the database.')

    mysql_query = mysql_client.cursor()
   
except Error as err:
    print(f"Error: {err}")


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
        if counter >= 1000:
            
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
            bad_description = game_details.get('detailed_description') or game_details.get('about_the_game')

            # Split words if description is not None
            if bad_description is not None:
                words = bad_description.split()
            else:
                words = []  # Use an empty list as words if there's no description
           

            if game_details is not None and game_details.get('type') == 'game':
                vr_tag_present = any([category.get('description', '') == "VR Only" or category.get('description', '') == "VR Supported" and category.get('description', '') not in exclude_tags 
                              for category in game_details.get('categories', [])]) or \
                        any([genre.get('description', '') == 'VR Only' or genre.get('description', '') == 'VR Supported' and genre.get('description', '') not in exclude_tags
                             for genre in game_details.get('genres', [])])
                               
                               
            if not any(word in exclude_tags for word in words):
                                                           
                            
                if vr_tag_present:
                    game_details['url'] = url  # Storing the URL in the game details

                    all_games_data[appid] = game_data
                
                    strip_keys(all_games_data[appid], keys_to_strip)
               
                    # print(f"VR tag found for game {game_name} with appid {appid}")
                    print(f"game #{counter}:{game_name} is vr")
                
 
                if 'description' in game_details:
                    description = game_details['description']
                    try:
                        summarized_description = summarize_text_with_openai(description)
                    except Exception as e:
                        print(f"Error during description summarization: {e}")
                        summarized_description = None
                
                with open('game_data_output.json', 'r') as f:
                    existing_data = json.load(f)
                    existing_data.update(all_games_data)
                with open('game_data_output.json', 'w') as f:
                    json.dump(existing_data, f, indent=4)
                all_games_data = {} 
          
            else:
                #print(f"game#{counter+1}:{game_name} is not vr")
                pass
                        
        else:
            print(f"Request failed for appid:{appid}")
            print(response.status_code)

        time.sleep(1.5)
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


    # Dictionary with column:value pairs
    data = {
        "title": "Sample VR Title",
        "slug": "sample-vr-title",
        "description": "A detailed description of Sample VR Title goes here.",
        "short_description": "A short description of Sample VR Title.",
        "primary_image": "/path/to/primary/image.jpg",
        "age_rating": "E",
        "min_players": 1,
        "max_players": 4,
        "store_url": "https://store.example.com/sample-vr-title",
        "active": 1,
        "steam_id": ""
    }

    # Dynamically building the SQL statement
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['%s'] * len(data))
    sql = f"INSERT INTO vr_titles ({columns}) VALUES ({placeholders})"
    
    # Executing the SQL command
    mysql_query.execute(sql, list(data.values()))
    
    # Committing the changes to the database
    mysql_client.commit()
    
    print("Data inserted successfully")



