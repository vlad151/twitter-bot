#!/bin/bash

# Navigate to the project directory
cd /home/vlad/Desktop/twitter-bot/

# Check the remote URL to ensure it's using SSH
echo "Checking Git remote URL..."
git remote -v

# Run the Python script and append the output to cron.log
# The 2>&1 redirects standard error to standard output
/usr/bin/python3 script.py >> cron.log 2>&1

# Add the cron.log file to the Git staging area
git add cron.log

# Commit the changes with a dynamic timestamp
git commit -m "Cron: Updated log on $(date)"

# Push the changes to the remote repository
git push origin main