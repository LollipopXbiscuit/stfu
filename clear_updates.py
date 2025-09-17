import requests
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset=-1")
print("Cleared pending updates")
