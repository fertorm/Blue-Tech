import os
from dotenv import load_dotenv

print("Loading .env...")
loaded = load_dotenv()
print(f"load_dotenv returned: {loaded}")

key = os.getenv("GOOGLE_API_KEY")
if key:
    print(f"Key found: {key[:5]}...{key[-5:] if len(key)>10 else ''}")
    print(f"Key length: {len(key)}")
else:
    print("Key NOT found in environment.")

# Check file existence manually
if os.path.exists(".env"):
    print(".env file exists.")
    with open(".env", "r") as f:
        content = f.read()
        print(f"File content length: {len(content)}")
        # Check if it looks like variable declaration
        if "GOOGLE_API_KEY" in content:
            print("GOOGLE_API_KEY string found in file.")
        else:
            print("GOOGLE_API_KEY string NOT found in file.")
else:
    print(".env file does NOT exist.")
