import requests
import re
import os

# The file in your repository
OUTPUT_FILE = "my_list.iptvcat.com.m3u8"

# A sample mapping of your channels to iptv-org's tvg-ids
# You can expand this dictionary by looking up IDs at: https://github.com/iptv-org/epg
EPG_MAP = {
    "Fox News Channel": "FoxNewsChannel.us",
    "CNN USA": "CNN.us",
    "ESPN U": "ESPNU.us",
    "NBA TV": "NBATV.us",
    "MLB Network": "MLBNetwork.us",
    "Bloomberg TV": "BloombergTelevision.us",
    "CBS News 24/7": "CBSNews.us",
    "ABC News Live": "ABCNewsLive.us",
    "Showtime East": "ShowtimeEast.us",
    "HBO 2 East": "HBO2East.us",
    "AMC East": "AMCEast.us",
    "Discovery Channel": "DiscoveryChannelEast.us",
    "History": "HistoryEast.us",
    "National Geographic East": "NationalGeographicEast.us",
    "Comedy Central East": "ComedyCentralEast.us",
    "Al Jazeera English": "AlJazeeraEnglish.qa",
    "France 24": "France24English.fr",
    "Sky News": "SkyNews.uk"
}

def clean_and_map_m3u(content):
    # Requirement 3: Clean up the URL tracking parameters
    content = content.replace("?checkedby:iptvcat.com", "")

    # Requirement 2: Add tvg-id for EPG mapping
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith("#EXTINF"):
            # Extract the raw channel name (everything after the last comma)
            channel_name = line.split(",")[-1].strip()
            
            # Strip resolution tags like " (1080p)" or " (720p)" to match the dictionary
            base_name = re.sub(r'\s*\(\d+p\)', '', channel_name).strip()

            if base_name in EPG_MAP:
                tvg_id = EPG_MAP[base_name]
                # Inject the tvg-id if it's not already there
                if 'tvg-id=' not in line:
                    lines[i] = re.sub(r'(#EXTINF:-?\d+)\s+', fr'\1 tvg-id="{tvg_id}" ', line)
                    
    return '\n'.join(lines)

def main():
    # If you have a direct URL to pull the raw text from daily, uncomment this:
    # SOURCE_URL = "https://example.com/raw_playlist"
    # response = requests.get(SOURCE_URL)
    # content = response.text
    
    # Otherwise, read the existing file in the repo
    if not os.path.exists(OUTPUT_FILE):
        print(f"Error: {OUTPUT_FILE} not found.")
        return

    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    processed_content = clean_and_map_m3u(content)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(processed_content)

    print("Playlist processed: URLs cleaned and EPG tvg-ids injected.")

if __name__ == "__main__":
    main()
