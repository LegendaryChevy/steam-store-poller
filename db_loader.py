import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import connect, Error
import json

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

with open("game_data_output.json", "r") as f:
    games = json.load(f)
    for app_id, game_info in games.items():
        game_data = game_info[app_id]["data"]


def make_slug(name):            
    words = name.split(" ")
    slug = "-".join(words)
    return slug


def new_rating(input):
    rating=""
    if input == "l" or input == "AL":
        rating = "E"

    elif input in range(10, 13) or input == "A10" or input == "A12":
        rating = "E10+"
    
    elif input in range(14, 17) or input == "A14" or input == "A16":
        rating = "T"
        
    elif input == 18 or input == "A18":
        rating = "M"
    
    return rating

def single_player():
    for category in game_data["categories"]:
        if category["description"] == "Single-Player":
            return 1
    return 0
    
def multi_player():
    for category in game_data["categories"]:
        if category["description"] == "Multi-player":
            return 1
    return 0

   # Dictionary with column:value pairs


for game in games:

    data = {
        "title": game_data["name"],
        "slug": make_slug(game_data["name"]),
        "description": game_data["ai_description"],
        "short_description": game_data["short_description"],
        "primary_image": f"pics/{game_data['name']}",
        "age_rating": new_rating(game_data["ratings"]["dejus"]["rating"]),
        "min_players": single_player(),
        "max_players": multi_player(),
        "store_url": game_data["url"],
        "active": 1,
        "steam_id": game_data["steam_appid"]
    }


    steam_appid = game_data["steam_appid"]

        # SQL command to check if the steam_appid already exists in the database
    sql_check = f"SELECT 1 FROM vr_titles WHERE steam_id = %s"
    mysql_query.execute(sql_check, (steam_appid,))

# If the steam_appid does not exist in the database then insert the data
    if not mysql_query.fetchone():
            # Dynamically building the SQL statement
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        sql = f"INSERT INTO vr_titles ({columns}) VALUES ({placeholders})"
            
            # Executing the SQL command
        mysql_query.execute(sql, list(data.values()))
            
            # Committing the changes to the database
        mysql_client.commit()
            
        print("Data inserted successfully")

    else:
        pass
