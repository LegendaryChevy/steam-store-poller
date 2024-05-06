import os
from dotenv import load_dotenv
import mysql.connector
import json
load_dotenv



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



  
   # Dictionary with column:value pairs
data = {
        "title": game_data["name"],
        "slug": "sample-vr-title",
        "description": game_data["ai_description"],
        "short_description": game_data["short_description"],
        "images": f"pics/{game_data["name"]}",
        "age_rating": "E",
        "min_players": 1,
        "max_players": 4,
        "store_url": game_data["url"],
        "active": 1,
        "steam_id": game_data["steam_appid"]
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

