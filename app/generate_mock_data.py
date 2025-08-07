import pandas as pd
import random
import uuid
import os

feeds_with_genres = {
  "https://feeds.megaphone.fm/conan-obrien-needs-a-friend": "Comedy",
  "https://feeds.megaphone.fm/stuffyoushouldknow": "Education",
  "https://feeds.megaphone.fm/the-daily": "News",
  "https://feeds.megaphone.fm/techstuff": "Technology",
  "https://feeds.megaphone.fm/revisionist-history": "History"
}

states = ["California", "Texas", "New York", "Florida", "Connecticut"]
uas = [
  "Google Podcasts/1.0.0.12345 (Linux; Android 13; Pixel 7)",
  "Spotify/8.9.0 iOS/15.3.1 iPhone13",
  "Apple Podcasts/1.0.0 (Mac OS X)",
  "Pocket Casts/7.0 (Android 11)",
  "Overcast/2025.4 (iOS 17.2)"
]

data = []

for _ in range(1000):
  feed, genre = random.choice(list(feeds_with_genres.items()))
  enclosure = feed.replace("feeds", "feeds/episodes") + f"/ep-{random.randint(1000, 9999)}.m4a"
  uuid_val = str(uuid.uuid4())
  ua = random.choice(uas)
  state = random.choice(states)
  duration = random.randint(60, 3600)  # Duration between 1 minute and 1 hour

  data.append([feed, enclosure, uuid_val, ua, state, duration, genre])

df = pd.DataFrame(data, columns=[
  "Podcast RSS Feed", "Enclosure URL", "UUID", "User Agent", "State", "Duration of Listen (seconds)", "Genre"
])

os.makedirs("app", exist_ok=True)

csv_path = "app/podcast_engagement_data.csv"
df.to_csv(csv_path, index=False)

print(f"Mock data saved to: {csv_path}")
