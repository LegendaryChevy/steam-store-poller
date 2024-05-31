# Steam Store Poller
    
## Description

steam-store-poller is a project designed to build a database of family-friendly VR games from the Steam store. It includes two main executables: game_filter.py and db_loader.py. Under most circu

**game_filter.py**: 
Fetches games from the Steam store and filters them to include only family-friendly VR games that haven't already been downloaded.
    
**db_loader.py**: 
Loads the filtered game data into the vr_titles table in the aagz database.

**Prerequisite libraries are in requirements.txt.**


## Installation
    Clone the Repository:

        cd steam-store-poller
        git clone git@github.com:LegendaryChevy/steam-store-poller.git
        
    
## Set Up Environment Variables:

    Fill out the .env file with all the required fields. An example .env file might look like this:
    DB_HOST=your_db_host
    DB_USER=your_db_user
    DB_PASS=your_db_password
    DB_NAME=aagz
    
## Install Dependencies:
pip install -r requirements.txt
    
## Set Up Database:
In terminal/command line, enter:
sudo mysql;
'your computer password'
create database 'example-name';
exit mysql with 'CTRL Z'

Execute table_vr_titles.sql in the terminal/command line:
sudo mysql -u your_db_user -p your_db_name < table_vr_titles.sql
    
## Usage
Running the Scripts:

Open the command line/terminal

Navigate to the Project Directory:
    cd path/to/steam-store-poller

primarily run the files using:
    ./poll_steam.sh

Alternatively you can run them seperately if needed with:
    
Run game_filter.py:
    python3 game_filter.py
    
Run db_loader.py:
    python3 db_loader.py
    



## Setup bash permissions   
Make the script executable: Use the chmod command to grant permissions to the script:
   chmod +x poll_steam.sh
   
Verify the file is executable: :
   ls -l poll_steam.sh
   
You should see something like this:
   -rwxr-xr-x 1 your_username your_group  1234 Oct  4 12:34 poll_steam.sh

Execute the script:
   ./poll_steam.sh
   
This should execute the script and run your Python programs in the specified order. 
    


## Contact Information
For any assistance, please contact:
Email: leeson73@gmail.com
