import json
import requests
import time
import os
import mysql.connector
import re
from steam_store_poller import poll_steam
from ai_description_tool import summarize_text_with_openai 
from games_list_comparer import comparer
#mydb = mysql.connector.connect(
   # host="",
 #   user="",
  #  password="",
   # database=""
   # )


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

check_and_create_files(['new_games.json', 'old_games.json'])

poll_steam()

comparer()

#mycursor = mydb.cursor()

with open('new_games.json') as json_file:
    data = json.load(json_file)
    all_games_data = {}
    counter = 0
    for game in data['applist']['apps']:
        vr_tag_present = False
        if counter >= 5:
            break
        
        appid = game['appid']
        game_name = game['name']
        game_details = None
        #print(f"Getting details for game {game_name} with appid {appid}")
        
        response = requests.get(f'http://store.steampowered.com/api/appdetails/?appids={appid}')
        
        #print(response.status_code)
        if response.status_code == 200:

            game_data = response.json()

            if str(appid) in game_data and 'data' in game_data[str(appid)]:
                game_details = game_data[str(appid)]['data']  # Accessing the game details
            
           # if game_details is not None:
            #    print(f"Categories for game {game_name}: {game_details.get('categories', [])}")
             #   print(f"Genres for game {game_name}: {game_details.get('genres', [])}")
            
            if game_details is not None:
                vr_tag_present = any([category.get('description', '') == "VR Only" or category.get('description', '') == "VR Supported" for category in game_details.get('categories', [])]) or \
                    any([genre.get('description', '') == 'VR Only' or genre.get('description', '') == 'VR Supported' for genre in game_details.get('genres', [])])
            
            if vr_tag_present:
               # print(f"VR tag found for game {game_name} with appid {appid}")
                print(f"{game_name} is vr")
                all_games_data[appid] = game_data
 
                if 'description' in game_details:
                    description = game_details['description']
                    try:
                        summarized_description = summarize_text_with_openai(description)
                    except Exception as e:
                        print(f"Error during description summarization: {e}")
                        summarized_description = None
            else:
                print(f"{game_name} is not vr")
                pass
                        
        else:
            print(f"Request failed for appid:{appid}")
            print(response.status_code)

        time.sleep(1.5)
        # Check if the game has a 'VR' tag in categories or genres
        

       
        counter += 1

    #for key, value in game_data.items():
     #   sql = "INSERT INTO games (key, value) VALUES (%s, %s)"
      #  val = (key, value)
       # mycursor.execute(sql, val)
with open('game_data_output.json', 'r') as f:
    data = json.load(f)  # Load existing data

    data.update(all_games_data)  # Append new data to existing data

with open('game_data_output.json', 'w') as f:
    json.dump(data, f, indent=4) 
    #mydb.commit()


# Load new games
with open('new_games.json', 'r') as f:
    new_games = json.load(f)

# Load old games
with open('old_games.json', 'r') as f:
    old_games = json.load(f)

# Add new games to old games
old_games['applist']['apps'].extend(new_games['applist']['apps'][:5])

# Write the updated old games back to old_games.json
with open('old_games.json', 'w') as f:
    json.dump(old_games, f)