#!/bin/bash

# Navigate to the directory containing the Python scripts
cd /home/legendarychevy/projects/aagz/steam-store-poller/main || exit

# Run game_filter.py
python3 game_filter.py

# Check if the first script succeeded
if [ $? -eq 0 ]; then
    # Run db_loader.py
    python3 db_loader.py
else
    echo "game_filter.py failed to run. db_loader.py will not be executed."
    exit 1
fi
