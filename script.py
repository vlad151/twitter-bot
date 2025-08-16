# A simple Twitter bot script using Python and the tweepy library.
# This script requires a Twitter (X) Developer account and the tweepy library.

# ====================================================================
# STEP 1: Set up your Twitter (X) Developer Account
# ====================================================================
# You need to apply for a developer account on the Twitter Developer Portal.
# This is where you'll get the necessary API keys and tokens.
#
# Follow these steps:
# 1. Go to https://developer.twitter.com and sign up for an account.
# 2. Apply for a project and create a new App within that project.
#    Note: Make sure to create a "Project" and then an "App" within it
#    to gain access to API v2.
# 3. Under the "Keys and tokens" section of your App, you will find
#    your API Key, API Key Secret, Access Token, and Access Token Secret.
#    You will need these for authentication.
#
# IMPORTANT: Keep these keys and tokens secret! Do not share them or
# hard-code them directly into a public repository. A better practice
# is to use environment variables.

# ====================================================================
# STEP 2: Install the required libraries
# ====================================================================
# Open your terminal or command prompt and run the following command
# to install the tweepy and requests libraries:
#
# pip install tweepy requests
#
# You'll also need a way to schedule this script to run once a day.
# On a Linux server, you can use `crontab`.

# ====================================================================
# STEP 3: The Python Script
# ====================================================================

import os
import random
import requests
import json
import tweepy
import pandas as pd
import time
from pytrends.request import TrendReq
from dotenv import load_dotenv

# Load environment variables from .env.local. This must be called before
# any os.getenv() calls to ensure the values are loaded correctly.
load_dotenv('.env.local')

# ---
# 1. Configuration
# ---

# IMPORTANT: Set these API keys as environment variables on your system.
# On Linux/macOS: export API_KEY="your_key_here"
# On Windows (CMD): set API_KEY="your_key_here"
# Replace with your actual keys from the Twitter developer portal and the Gemini API.
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# List of topics the bot can tweet about.
# The bot will select one of these topics randomly.
TOPICS = [
    "tech",
    "fullstack development",
    "AI",
    "the Moldovan tech market",
    "startups",
    "launching products"
]

# The Gemini model to use for text generation.
# Use gemini-2.5-flash-preview-05-20 as it's the most efficient for this task.
GEMINI_MODEL = "gemini-2.5-flash-preview-05-20"

# The blog URL to include in some tweets.
BLOG_URL = "https://vladlazar.blog"

# The languages the bot can tweet in.
LANGUAGES = ["en", "ro"] # English, Romanian

# ---
# 2. Function Definitions
# ---

def get_trending_topics_with_pytrends():
    """
    Fetches the top daily trending searches for Moldova using the pytrends library.

    Returns:
        list: A list of trending query strings, or None if an error occurs.
    """
    print("Fetching trending topics from Google Trends for Moldova...")
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        # The 'pn' parameter is the country code. 'MD' is for Moldova.
        trending_df = pytrends.trending_searches(pn='MD')
        
        if not trending_df.empty:
            # Extract the trending topics from the DataFrame
            trending_topics = trending_df[0].tolist()
            return trending_topics
        else:
            print("No trending topics found for Moldova.")
            return None
    except Exception as e:
        print(f"Error fetching Google Trends data: {e}")
        return None

def generate_tweet_with_gemini(topic, is_funny=False, trending_keyword=None, include_link=False, language="en"):
    """
    Uses the Gemini API to generate a creative and engaging tweet.

    Args:
        topic (str): The subject for the tweet.
        is_funny (bool): If True, generates a humorous tweet.
        trending_keyword (str): An optional trending keyword to include.
        include_link (bool): If True, asks the model to include a relevant link.
        language (str): The language code for the tweet (e.g., 'en' for English, 'ro' for Romanian).

    Returns:
        str: The generated tweet text, or None if an error occurs.
    """
    print(f"Generating a tweet in {language} about: {topic}...")

    # The prompt is customized based on the language.
    if language == "ro":
        prompt_intro = f"""
        Ești un pasionat de tehnologie, prietenos, antrenant și informat.
        Sarcina ta este să scrii un singur tweet (maximum 280 de caractere) despre următorul subiect:
        "{topic}".
        """
        tweet_guidelines = """
        Tweet-ul ar trebui să fie:
        - Concis și direct la subiect.
        - Antrenant și conversațional.
        - Să folosească hashtag-uri relevante.
        - Să sune ca și cum ar fi fost scris de o persoană.
        """
        if trending_keyword:
            prompt_trending = f"\n\nDe asemenea, încearcă să incluzi organic următorul cuvânt-cheie în trend: \"{trending_keyword}\"."
        else:
            prompt_trending = ""
        
        if is_funny:
            prompt_humor = "\n\nFă acest tweet amuzant și spiritual. Folosește umorul pentru a-ți exprima punctul de vedere."
        else:
            prompt_humor = ""

        if include_link:
            prompt_link = f"\n\nInclude un link pertinent de pe blog-ul {BLOG_URL}. De exemplu: {BLOG_URL}/postari/despre-subiectul-tweet-ului"
        else:
            prompt_link = ""
        
        prompt = prompt_intro + tweet_guidelines + prompt_trending + prompt_humor + prompt_link
    
    else: # Default to English
        prompt = f"""
        You are a friendly, engaging, and knowledgeable tech enthusiast.
        Your task is to write a single tweet (maximum 280 characters) about the following topic:
        "{topic}".
        
        The tweet should be:
        - Concise and to the point.
        - Engaging and conversational.
        - Use relevant hashtags.
        - Sound like it was written by a human.
        """
        
        if trending_keyword:
            prompt += f"\n\nAlso, try to organically include the following trending keyword: \"{trending_keyword}\"."
        
        if is_funny:
            prompt += "\n\nMake this tweet funny and witty. Use humor to get your point across."
        
        if include_link:
            prompt += f"\n\nInclude a relevant link from the blog {BLOG_URL}. For example: {BLOG_URL}/posts/about-the-tweet-topic."


    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    try:
        # Add a timeout to prevent the API call from hanging indefinitely.
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=30 # Set a timeout of 30 seconds
        )
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        data = response.json()
        
        # Safely access the generated text from the JSON response.
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

    Args:
        tweet_text (str): The text of the tweet to post.

    Returns:
        bool: True if the tweet was posted successfully, False otherwise.
    """
    print("Attempting to post the tweet...")
    
    try:
        # Authenticate with the Twitter API using your credentials.
        # This uses API v2.
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
    Main function to run the bot. It determines how many tweets to send today
    and then posts them with a delay in between.
    """
    # Decide how many tweets to send today (0-7).
    num_tweets = random.randint(0, 7)
    print(f"Scheduled to post {num_tweets} tweets today.")

    if num_tweets == 0:
        print("No tweets scheduled for today. Exiting.")
        return

    for i in range(num_tweets):
        # Choose a random topic from the predefined list.
        selected_topic = random.choice(TOPICS)
        
        # Add a 20% chance to generate a funny tweet.
        should_be_funny = random.random() < 0.2
        
        # Add a 40% chance to include a link to your blog.
        should_include_link = random.random() < 0.4
        
        # Choose a random language from the list.
        selected_language = random.choice(LANGUAGES)
        
        # Get a trending keyword to make the tweet more relevant.
        trending_keywords = get_trending_topics_with_pytrends()
        trending_keyword = None
        if trending_keywords:
            trending_keyword = random.choice(trending_keywords)
        
        # Generate the tweet content.
        tweet_content = generate_tweet_with_gemini(
            selected_topic,
            is_funny=should_be_funny,
            trending_keyword=trending_keyword,
            include_link=should_include_link,
            language=selected_language
        )
        
        # If the generation was successful, post the tweet.
        if tweet_content:
            post_tweet(tweet_content)
        else:
            print("Could not generate a tweet. Skipping this iteration.")
        
        # Wait a random amount of time (e.g., 1-4 hours) before the next tweet.
        # This prevents spamming and makes the bot's behavior more natural.
        if i < num_tweets - 1:
            # We'll calculate a delay in seconds.
            # 1 hour = 3600 seconds, 4 hours = 14400 seconds.
            delay_in_seconds = random.randint(3600, 14400)
            print(f"Tweet {i+1}/{num_tweets} posted. Waiting {delay_in_seconds // 60} minutes for the next one.")
            time.sleep(delay_in_seconds)

if __name__ == "__main__":
    # Check if all required environment variables are set.
    if not all([X_BEARER_TOKEN, X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET, GEMINI_API_KEY]):
        print("Error: One or more environment variables are missing.")
        print("Please ensure X_BEARER_TOKEN, X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET, and GEMINI_API_KEY are set.")
    else:
        run_bot()
