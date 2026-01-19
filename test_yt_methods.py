from youtube_transcript_api import YouTubeTranscriptApi

video_id = "jNQXAC9IVRw"  # Me at the zoo

print("Testing YouTubeTranscriptApi.list_transcripts(video_id)...")
try:
    print(YouTubeTranscriptApi.list_transcripts(video_id))
except AttributeError:
    print("Method list_transcripts not found.")
except Exception as e:
    print(f"Error calling list_transcripts: {e}")

print("\nTesting YouTubeTranscriptApi().list(video_id)...")
try:
    api = YouTubeTranscriptApi()
    print(api.list(video_id))
except Exception as e:
    print(f"Error calling instance list: {e}")


print("\nTesting instance methods:")
try:
    api = YouTubeTranscriptApi()
    print("Instance attributes:", dir(api))
    if hasattr(api, "get_transcript"):
        print("Calling api.get_transcript(video_id)...")
        print(api.get_transcript(video_id))
    else:
        print("Instance has no get_transcript method.")
except Exception as e:
    print(f"Error: {e}")
