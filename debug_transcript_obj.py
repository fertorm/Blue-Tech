from youtube_transcript_api import YouTubeTranscriptApi

video_id = "FwjaHCVNBWA"

try:
    api = YouTubeTranscriptApi()
    transcript_list = api.list(video_id)
    transcript = next(iter(transcript_list))
    full_data = transcript.fetch()

    print(f"Type of full_data: {type(full_data)}")
    if full_data:
        first_item = full_data[0]
        print(f"Type of first item: {type(first_item)}")
        print(f"Dir of first item: {dir(first_item)}")
        print(f"First item repr: {first_item}")

except Exception as e:
    print(f"Error: {e}")
