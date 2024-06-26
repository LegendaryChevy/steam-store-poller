import os
import re
import requests
import time
from unidecode import unidecode

def make_url_friendly(name):
    # Transliterate Unicode characters to closest ASCII representation
    name = unidecode(name)
    # Convert to lowercase
    name = name.lower()
    # Replace spaces with dashes
    name = name.replace(' ', '-')
    # Remove any non-alphanumeric characters except dashes
    name = re.sub(r'[^a-z0-9\-]', '', name)
    # Replace any non-ASCII characters with "non-ascii"
    name = re.sub(r'[^a-z0-9\-]', 'non-ascii', name)
    return name

def pic_downloader(game_name, screenshots):
    # Make the game_name URL friendly
    game_name_friendly = make_url_friendly(game_name)

    # Form directory path
    dir_path = os.path.join(os.getenv('IMAGES_PATH_FULL'), game_name_friendly)

    # Create directory if it doesn't exist
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    # Fetch and save each image
    for i, screenshot in enumerate(screenshots):
        path_full = screenshot['path_full']

        response = requests.get(path_full, stream=True)
        if response.status_code == 200:
            # Define the file path for the image
            image_file_path = os.path.join(dir_path, f'image_{i}.jpg')

            # Open a file in the newly created directory and write image data to it
            with open(image_file_path, 'wb') as img_file:
                img_file.write(response.content)

            # Replace the URL in the screenshots with the local file path
            screenshots[i]['path_full'] = image_file_path
        time.sleep(0.5)
    # Return the updated screenshots
    return screenshots
