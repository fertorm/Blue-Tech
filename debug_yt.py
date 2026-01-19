import sys
import youtube_transcript_api
from youtube_transcript_api import YouTubeTranscriptApi

print(f"Python Executable: {sys.executable}")
print(f"Module File: {youtube_transcript_api.__file__}")
print(f"Version: {getattr(youtube_transcript_api, '__version__', 'Unknown')}")
print("Attributes of youtube_transcript_api MODULE:")
print(dir(youtube_transcript_api))

if "YouTubeTranscriptApi" in dir(youtube_transcript_api):
    cls = youtube_transcript_api.YouTubeTranscriptApi
    print(f"Type of YouTubeTranscriptApi: {type(cls)}")
    print(f"Dir of YouTubeTranscriptApi: {dir(cls)}")
