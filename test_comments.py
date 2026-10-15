from itertools import islice
from youtube_comment_downloader import YoutubeCommentDownloader

d = YoutubeCommentDownloader()
for c in islice(d.get_comments_from_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ"), 5):
    print(c["text"])