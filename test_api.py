from googleapiclient.discovery import build

API_KEY = "AIzaSyC5hB6YeyryeL6_Wp9rLVjuEQewleMujjo"
yt = build("youtube", "v3", developerKey=API_KEY)
res = yt.commentThreads().list(
    part="snippet", videoId="dQw4w9WgXcQ", maxResults=5, textFormat="plainText"
).execute()

for item in res["items"]:
    print(item["snippet"]["topLevelComment"]["snippet"]["textDisplay"])