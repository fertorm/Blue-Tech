import os
import re
import sys
import time
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables (API Key)
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("WARNING: GOOGLE_API_KEY not found in environment variables.")
    print("Please set it in a .env file or export it.")
else:
    genai.configure(api_key=GOOGLE_API_KEY)


def get_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    Supports various formats (standard, short, embed).
    """
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def get_video_metadata(url):
    """
    Scrapes the video title and description using BeautifulSoup
    to avoid heavy dependencies like pytube (which breaks often).
    """
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Title is usually in the <title> tag, or meta tags
        title_tag = soup.find("meta", property="og:title")
        title = title_tag["content"] if title_tag else "Unknown Title"

        # Description
        desc_tag = soup.find("meta", property="og:description")
        description = desc_tag["content"] if desc_tag else "No description found."

        return title, description
    except Exception as e:
        print(f"Error fetching metadata: {e}")
        return "Unknown Title", "No description"


def get_transcript(video_id):
    """
    Fetches the transcript for the given video ID.
    Returns a single string with the full text or None if failed.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Configure session with headers to avoid being blocked
            session = requests.Session()
            session.headers.update(
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
            )

            # Detected environment uses instance-based API with .list() method
            # Re-instantiate per attempt to get fresh session if needed
            api = YouTubeTranscriptApi(http_client=session)
            transcript_list = api.list(video_id)

            # Priority: Manual English -> Manual Spanish -> Any Generated English -> Any Generated
            try:
                transcript = transcript_list.find_transcript(
                    ["en", "es", "en-US", "es-419"]
                )
            except:
                # If exact match fails, try finding any generated transcript
                try:
                    transcript = transcript_list.find_generated_transcript(["en", "es"])
                except:
                    # Fallback to the first available transcript
                    transcript = next(iter(transcript_list))

            full_data = transcript.fetch()
            full_text = " ".join([t.text for t in full_data])
            return full_text

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print(f"Error fetching transcript after {max_retries} attempts: {e}")
                return None


def analyze_with_ai(title, transcript):
    """
    Sends the transcript to Gemini for analysis.
    """
    if not GOOGLE_API_KEY:
        return "Error: No API Key configured."

    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
    You are an expert video analyst. Analyze the following YouTube video transcript.
    
    Video Title: {title}
    
    Transcript:
    {transcript[:25000]}  # Limiting context window just in case
    
    Generate a response in the following format:
    
    1. **Clickbait Verdict**: [YES/NO] - [Reasoning based on title vs actual content]
    2. **Summary**: [A concise 3-sentence summary of the video]
    3. **Key Insights**:
       - [Insight 1]
       - [Insight 2]
       - [Insight 3]
    4. **Important Timestamps** (Approximate based on content flow):
       - [Time]: [Event/Topic]
       - [Time]: [Event/Topic]
       
    (Note: Since you only have text, estimate valid timestamp areas if possible, or omit specific times if unsure, but try to identify key sections.)
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error during AI analysis: {e}"


def main():
    print("--- YouTube Video Analyzer ---")

    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter YouTube Video URL: ").strip()

    if not url:
        print("Error: No URL provided.")
        return

    print(f"Processing URL: {url}...")

    video_id = get_video_id(url)
    if not video_id:
        print("Error: Could not extract Video ID.")
        return

    print(f"Video ID: {video_id}")

    # 1. Get Metadata
    print("Fetching metadata...")
    title, description = get_video_metadata(url)
    print(f"Title: {title}")

    # 2. Get Transcript
    print("Fetching transcript...")
    transcript = get_transcript(video_id)

    if not transcript:
        print(
            "Could not retrieve transcript. The video might not have captions enabled or is restricted."
        )
        return

    print(f"Transcript length: {len(transcript)} characters.")

    # 3. Analyze
    print("\n--- Analyzing with AI (Gemini) ---\n")
    analysis = analyze_with_ai(title, transcript)

    print(analysis)

    # Save report
    with open(f"analysis_{video_id}.txt", "w", encoding="utf-8") as f:
        f.write(f"URL: {url}\n")
        f.write(f"Title: {title}\n\n")
        f.write(analysis)
    print(f"\nReport saved to: analysis_{video_id}.txt")


if __name__ == "__main__":
    main()
