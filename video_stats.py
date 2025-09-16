import requests
import json
import os
from dotenv import load_dotenv


load_dotenv(dotenv_path=".env")
API_KEY = os.getenv("API_KEY")

CHANNEL_HANDLER="MrBeast"

def get_channel_id():

    try:

        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forUsername={CHANNEL_HANDLER}&key={API_KEY}"
        json_url = requests.get(url)
        data = json_url.json()
        channel_items = data['items'][0]
        channel_playlistId = channel_items['contentDetails']['relatedPlaylists']['uploads']
        return channel_playlistId
    
    except Exception as e:
        raise e
        print("An error occurred:", e)


if __name__ == "__main__":
    print(get_channel_id())