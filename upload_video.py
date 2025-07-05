import base64
import sys
import os
import requests

def encode_file_to_base64(file_path):
    if not os.path.isfile(file_path):
        print(f"❌ Error: '{file_path}' is not a valid file.")
        return None

    with open(file_path, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode("utf-8")
    return encoded_string

def send_to_api(base64_str, file_name, description="The course head is Dr Loke."):
    url = "http://localhost:8080/upload"
    payload = {
        "course_code": "SC1007",
        "video": [{
            "video_name": "Sc1007_videolecture",
            "video_description": description,
            "base64_encoded_video": base64_str
        }]
    }
    try:
        response = requests.post(url, json=payload)
        print(f"\n📤 Sent to API: {url}")
        print(f"✅ Status: {response.status_code}")
        print(f"📝 Response: {response.text}")
    except requests.RequestException as e:
        print(f"❌ Failed to send to API: {e}")

def main():
    # Get file path from command line or prompt
    file_path = r"C:\Users\nicol\OneDrive\Desktop\lecture-chatbot-repo\z_downloadedVideo\sc1007_720_2.mp4"

    file_name = os.path.basename(file_path)
    base64_str = encode_file_to_base64(file_path)

    if base64_str:
        print("\n✅ Base64 string (first 100 characters):")
        print(base64_str[:100])

        send_to_api(base64_str, file_name)

if __name__ == "__main__":
    main()
