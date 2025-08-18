#!/usr/bin/env python3

# A simple Twitter bot script using Python and the tweepy library.
# This script scrapes articles from daily.dev for content and links.
#
# This script requires a Twitter (X) Developer account and the following libraries:
# - tweepy
# - requests
# - beautifulsoup4 (for web scraping)
# - pandas
# - python-dotenv
#
# ====================================================================
# STEP 1: Install the required libraries
# ====================================================================
# Open your terminal or command prompt and run the following command
# to install the necessary libraries:
#
# pip install tweepy requests beautifulsoup4 pandas python-dotenv
#
# ====================================================================
# STEP 2: The Python Script
# ====================================================================

import os
import random
import requests
import json
import tweepy
import pandas as pd
import time
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# ---
# 1. Configuration
# ---

# IMPORTANT: Use the full, absolute path to the .env.local file.
# This ensures the script can find the file regardless of the current working directory.
ENV_PATH = '/home/vlad/Desktop/twitter-bot/.env.local'

if os.path.exists(ENV_PATH):
    print(f"Loading environment variables from: {ENV_PATH}")
    load_dotenv(ENV_PATH)
else:
    print(f"Error: The .env.local file was not found at {ENV_PATH}")
    print("Please make sure the path is correct and the file exists.")
    exit()

# IMPORTANT: Set these API keys as environment variables on your system.
# Replace with your actual keys from the Twitter developer portal and the Gemini API.
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ---
# 1.1. Diagnostic Check (Added for troubleshooting)
# ---
print("\n--- Diagnostic Check ---")
print(f"X_BEARER_TOKEN loaded: {bool(X_BEARER_TOKEN)}")
print(f"X_API_KEY loaded: {bool(X_API_KEY)}")
print(f"X_API_SECRET loaded: {bool(X_API_SECRET)}")
print(f"X_ACCESS_TOKEN loaded: {bool(X_ACCESS_TOKEN)}")
print(f"X_ACCESS_SECRET loaded: {bool(X_ACCESS_SECRET)}")
print(f"GEMINI_API_KEY loaded: {bool(GEMINI_API_KEY)}")
print("------------------------\n")

if not all([X_BEARER_TOKEN, X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET, GEMINI_API_KEY]):
    print("Error: One or more environment variables are missing after loading the file.")
    print("Please check the .env.local file to ensure all keys are present and correctly formatted.")
    exit()
# End of Diagnostic Check

# A more diverse and engaging list of topics the bot can tweet about.
# The bot will select one of these topics randomly.
TOPICS = [
    "tech trends",
    "fullstack development",
    "AI ethics",
    "the future of work",
    "startups and venture capital",
    "launching products",
    "cybersecurity tips",
    "programming languages",
    "data science",
    "cloud computing",
    "web development frameworks",
    "open source projects",
    "tech career advice",
    "software engineering best practices"
]

# The Gemini model to use for text generation.
GEMINI_MODEL = "gemini-2.5-flash-preview-05-20"

# ---
# 2. Function Definitions
# ---

def get_article_from_daily_dev():
    """
    Scrapes the daily.dev homepage to find a relevant tech article to link.

    Returns:
        str: A URL of a recent tech article, or None if an error occurs.
    """
    print("Scraping daily.dev for a relevant article...")
    url = "https://daily.dev"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Updated selector to be more robust.
        links = soup.select('div[data-testid="feed-article-card-link"] a[href]')
        
        if links:
            # Pick a random link from the found articles.
            full_link = random.choice(links)['href']
            print(f"Found article link: {full_link}")
            return full_link
        else:
            print("No articles found on daily.dev with the specified selector.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error scraping daily.dev: {e}")
        return None

def generate_tweet_with_gemini(topic, tweet_type="standard", include_link=None, language="en"):
    """
    Uses the Gemini API to generate a creative and engaging tweet.
    This function can generate standard tweets, hot takes, or fun facts.

    Args:
        topic (str): The subject for the tweet.
        tweet_type (str): 'standard', 'fun_fact', or 'hot_take'.
        include_link (str): An optional URL to include in the tweet.
        language (str): The language code for the tweet (e.g., 'en' for English, 'ro' for Romanian).

    Returns:
        str: The generated tweet text, or None if an error occurs.
    """
    print(f"Generating a {tweet_type} tweet in {language} about: {topic}...")

    # Base prompt for the AI persona.
    base_prompt = """
    You are a friendly, engaging, and knowledgeable tech enthusiast.
    Your task is to write a single tweet (maximum 280 characters) about the following topic:
    "{topic}".
    
    The tweet should be:
    - Concise and to the point.
    - Engaging and conversational.
    - Use relevant hashtags.
    - Sound like it was written by a human.
    """

    # Customize the prompt based on the tweet type.
    if tweet_type == "fun_fact":
        base_prompt += "\n\nStart the tweet with 'Fun Fact:' or 'Did you know?' and present a surprising or interesting fact about the topic."
    elif tweet_type == "hot_take":
        base_prompt += "\n\nStart the tweet with a strong, opinionated statement (a 'hot take') about the topic that is likely to spark debate. Use an emoji to signal the opinion."
    
    if include_link:
        base_prompt += f"\n\nInclude this link at the end of the tweet, after the content and hashtags: {include_link}"

    # Translate the prompt if the language is Romanian.
    if language == "ro":
        prompt_template = f"""
        Ești un pasionat de tehnologie, prietenos, antrenant și informat.
        Sarcina ta este să scrii un singur tweet (maximum 280 de caractere) despre următorul subiect:
        "{topic}".
        
        Tweet-ul ar trebui să fie:
        - Concis și direct la subiect.
        - Antrenant și conversațional.
        - Să folosească hashtag-uri relevante.
        - Să sune ca și cum ar fi fost scris de o persoană.
        """
        if tweet_type == "fun_fact":
            prompt_template += "\n\nÎncepe tweet-ul cu 'Un fapt interesant:' sau 'Știai că?' și prezintă un fapt surprinzător sau interesant despre subiect."
        elif tweet_type == "hot_take":
            prompt_template += "\n\nÎncepe tweet-ul cu o declarație fermă, bazată pe opinie (un 'hot take') despre subiect, care să stârnească o dezbatere. Folosește un emoji pentru a semnala opinia."
        if include_link:
            prompt_template += f"\n\nInclude acest link la finalul tweet-ului, după conținut și hashtag-uri: {link_to_include}"
    else: # Default to English
        prompt_template = base_prompt

    payload = {
        "contents": [{"parts": [{"text": prompt_template}]}]
    }

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    try:
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=30 # Set a timeout of 30 seconds
        )
        response.raise_for_status()
        
        data = response.json()
        
        tweet_text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text")
        
        if tweet_text:
            return tweet_text.strip()
        else:
            print("Error: No tweet text found in the Gemini response.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Error parsing Gemini response: {e}")
        return None

def post_tweet(tweet_text):
    """
    Posts a tweet to your Twitter (X) account using the Tweepy library.
    """
    print("Attempting to post the tweet...")
    
    try:
        client = tweepy.Client(
            bearer_token=X_BEARER_TOKEN,
            consumer_key=X_API_KEY,
            consumer_secret=X_API_SECRET,
            access_token=X_ACCESS_TOKEN,
            access_token_secret=X_ACCESS_SECRET
        )
        
        response = client.create_tweet(text=tweet_text)
            
        print("Tweet posted successfully!")
        print(f"View it at: https://twitter.com/user/status/{response.data['id']}")
        return True
    
    except tweepy.errors.TweepyException as e:
        print(f"Error posting tweet: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

# ---
# 3. Main Execution Logic
# ---

def run_bot():
    """
    Main function to run the bot.
    """
    num_tweets = random.randint(0, 7)
    print(f"Scheduled to post {num_tweets} tweets today.")

    if num_tweets == 0:
        print("No tweets scheduled for today. Exiting.")
        return

    for i in range(num_tweets):
        # Determine language with a 33% chance for Romanian.
        selected_language = random.choices(["en", "ro"], weights=[67, 33], k=1)[0]
        
        # Choose a random tweet type.
        tweet_type = random.choice(["standard", "fun_fact", "hot_take"])
        
        # Choose a random topic.
        selected_topic = random.choice(TOPICS)
        
        # Get a link if the topic is tech and there's a 50% chance.
        link_to_include = None
        if selected_topic in ["tech", "fullstack development", "AI"] and random.random() < 0.5:
            link_to_include = get_article_from_daily_dev()
        
        # Generate the tweet content.
        tweet_content = generate_tweet_with_gemini(
            selected_topic,
            tweet_type=tweet_type,
            include_link=link_to_include,
            language=selected_language
        )
        
        if tweet_content:
            post_tweet(tweet_content)
        else:
            print("Could not generate a tweet. Skipping this iteration.")
        
        if i < num_tweets - 1:
            delay_in_seconds = random.randint(3600, 14400)
            print(f"Tweet {i+1}/{num_tweets} posted. Waiting {delay_in_seconds // 60} minutes for the next one.")
            time.sleep(delay_in_seconds)

if __name__ == "__main__":
    run_bot()
