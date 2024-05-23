import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import connect, Error
import json
from datetime import datetime
from unidecode import unidecode
import re
import argparse

load_dotenv()

# Retrieve database credentials
db_config = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': os.getenv('MYSQL_HOST'),
    'database': os.getenv('MYSQL_DB'),
}

def make_url_friendly(name):
    # Transliterate Unicode characters to closest ASCII representation
    name = unidecode(name)
    # Convert to lowercase
    name = name.lower()
    # Replace spaces with dashes
    name = name.replace(' ', '-')
    # Remove any non-alphanumeric characters except dashes
    name = re.sub(r'[^a-z0-9\-]', '', name)
    return name

def new_rating(game_data):
    input_rating = ""
    if 'ratings' in game_data and game_data['ratings'] is not None:
        if 'dejus' in game_data["ratings"] and 'rating' in game_data["ratings"]['dejus']:
            input_rating = game_data["ratings"]['dejus']['rating']
        elif 'steam_germany' in game_data["ratings"] and 'rating' in game_data["ratings"]['steam_germany']:
            input_rating = game_data["ratings"]['steam_germany']['rating']

        input = input_rating
        rating = ""
        if input == "l" or input == "AL" or input == range(0, 6):
            rating = "E"
        elif input in range(10, 13) or input == "A10" or input == "A12":
            rating = "E10+"
        elif input in range(14, 17) or input == "A14" or input == "A16":
            rating = "T"
        elif input == 18 or input == "A18":
            rating = "M"

        return rating

    else:
        return "NR"

def single_player(game_data):
    for category in game_data["categories"]:
        if category["description"] == "Single-Player":
            return 1
    return 0

def multi_player(game_data):
    for category in game_data["categories"]:
        if category["description"] == "Multi-player":
            return 1
    return 0

def handle_images(mysql_query, vr_title_id, game_name_url_friendly, game_data, current_timestamp, replace_images):
    if replace_images:
        delete_images_sql = "DELETE FROM vr_title_images WHERE vr_title_id = %s"
        mysql_query.execute(delete_images_sql, (vr_title_id,))

    if "screenshots" in game_data:
        for i, screenshot in enumerate(game_data["screenshots"]):
            is_primary = 1 if i == 0 else 0
            file_path = f"images/titles/{game_name_url_friendly}/image_{i}.jpg"
            if not replace_images:
                # Check if the image already exists
                check_image_sql = "SELECT 1 FROM vr_title_images WHERE vr_title_id = %s AND file_path = %s"
                mysql_query.execute(check_image_sql, (vr_title_id, file_path))
                if mysql_query.fetchone():
                    continue

            image_data = {
                "vr_title_id": vr_title_id,
                "file_path": file_path,
                "primary": is_primary,
                "created_at": current_timestamp,
                "updated_at": current_timestamp
            }

            # Building the SQL statement for vr_title_images
            columns = ', '.join(f"`{key}`" for key in image_data.keys())  # Enclose column names in backticks
            placeholders = ', '.join(['%s'] * len(image_data))
            sql = f"INSERT INTO vr_title_images ({columns}) VALUES ({placeholders})"
            mysql_query.execute(sql, list(image_data.values()))

        print("Images handled successfully")
    else:
        print(f"No screenshots found for: {game_data['name']} (Steam ID: {game_data['steam_appid']})")

def main(update, replace_images):
    try:
        # Establishing the connection
        mysql_client = connect(**db_config)
        print('Successfully connected to the database.')

        mysql_query = mysql_client.cursor()

    except Error as err:
        print(f"Error: {err}")
        return

    # Dictionary with column:value pairs
    with open("game_data_output.json", "r") as f:
        games = json.load(f)
        for app_id, game_info in games.items():
            game_data = game_info[app_id]["data"]

            # Check if 'ai_description' key exists
            if 'ai_description' not in game_data:
                print(f"Missing 'ai_description' in: {game_data['name']} - falling back to detailed description")
                game_data["ai_description"] = game_data["detailed_description"]

            current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            game_name_url_friendly = make_url_friendly(game_data["name"])

            data = {
                "title": game_data["name"],
                "slug": game_name_url_friendly,
                "description": game_data["ai_description"],
                "short_description": game_data["short_description"],
                "primary_image": 0, # old image field... proper images are stored in vr_title_images
                "age_rating": new_rating(game_data),
                "single_player": single_player(game_data),
                "multi_player": multi_player(game_data),
                "store_url": game_data["url"],
                "active": 1,
                "steam_id": game_data["steam_appid"],
                "is_free": game_data["is_free"],
                "created_at": current_timestamp,
                "updated_at": current_timestamp
            }

            steam_appid = game_data["steam_appid"]

            # SQL command to check if the steam_appid already exists in the database
            sql_check = f"SELECT id FROM vr_titles WHERE steam_id = %s"
            mysql_query.execute(sql_check, (steam_appid,))
            result = mysql_query.fetchone()
            mysql_query.fetchall()  # Fetch remaining results, if any, to avoid the unread results error

            if result:
                vr_title_id = result[0]
                if update:
                    # Update existing entry
                    data.pop("created_at")  # Do not update the created_at field
                    columns = ', '.join([f"{col} = %s" for col in data.keys()])
                    sql_update = f"UPDATE vr_titles SET {columns} WHERE id = {vr_title_id}"
                    mysql_query.execute(sql_update, list(data.values()))
                    print(f"Data updated successfully for: {game_data['name']} (Steam ID: {steam_appid})")

                    # Handle images based on the replace_images flag
                    handle_images(mysql_query, vr_title_id, game_name_url_friendly, game_data, current_timestamp, replace_images)
                    mysql_client.commit()
                else:
                    print(f"Skipping existing entry: {game_data['name']} (Steam ID: {steam_appid})")
            else:
                # Insert new entry
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['%s'] * len(data))
                sql_insert = f"INSERT INTO vr_titles ({columns}) VALUES ({placeholders})"
                mysql_query.execute(sql_insert, list(data.values()))

                # Get the inserted vr_title_id
                vr_title_id = mysql_query.lastrowid

                # Handle images
                handle_images(mysql_query, vr_title_id, game_name_url_friendly, game_data, current_timestamp, replace_images)

                # Commit the changes to the database
                mysql_client.commit()
                print("Data inserted successfully")

            # Ensure the cursor is cleared before the next iteration
            mysql_query.fetchall()

    mysql_query.close()
    mysql_client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Load game data into the database.')
    parser.add_argument('--update', action='store_true', help='Update existing entries instead of skipping them.')
    parser.add_argument('--replace-images', action='store_true', help='Replace existing images instead of updating them.')
    args = parser.parse_args()

    main(args.update, args.replace_images)
