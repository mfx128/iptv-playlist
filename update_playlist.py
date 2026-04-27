import requests
from bs4 import BeautifulSoup
import re
import os

# Configuration
NEW_FILE = "my_list.iptvcat.com.m3u"
OLD_FILE = "my_list.iptvcat.com.m3u8"

# EPG Mapping for IPTV Smarters
# Add more mappings here following the "Channel Name": "tvg-id" format
EPG_MAP = {
    "Fox News Channel": "FoxNewsChannel.us",
    "CNN USA": "CNN.us",
    "ESPN U": "ESPNU.us",
    "NBA TV": "NBATV.us",
    "MLB Network": "MLBNetwork.us",
    "Bloomberg TV": "BloombergTelevision.us",
    "CBS News 24/7": "CBSNews.us",
    "ABC News Live": "ABCNewsLive.us",
    "Al Jazeera English": "AlJazeeraEnglish.qa",
    "Sky News": "SkyNews.uk"
}

def scrape_iptvcat():
    """Scrapes iptvcat.com for any fresh public links."""
    print("Scraping for fresh links...")
    url = "https://iptvcat.com/home_22"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # Regex to find m3u8 or ts streams
        links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', response.text)
        return list(set([link for link in links if ".m3u8" in link or ".ts" in link]))
    except Exception as e:
        print(f"Scrape failed: {e}")
        return []

def process_and_clean(content):
    """Strips tracking, adds EPG IDs, and fixes formatting."""
    # Remove tracking parameter from iptvcat
    content = content.replace("?checkedby:iptvcat.com", "")
    
    lines = content.split('\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("#EXTINF"):
            channel_name = line.split(",")[-1].strip()
            # Remove resolution markers for cleaner matching
            base_name = re.sub(r'\s*\(\d+p\)', '', channel_name).strip()
            
            if base_name in EPG_MAP:
                tvg_id = EPG_MAP[base_name]
                if 'tvg-id=' not in line:
                    line = re.sub(r'(#EXTINF:-?\d+)\s+', fr'\1 tvg-id="{tvg_id}" ', line)
        
        processed_lines.append(line)
            
    return '\n'.join(processed_lines).strip()

def main():
    # 1. Handle Migration and Loading
    content = "#EXTM3U"
    if os.path.exists(OLD_FILE):
        with open(OLD_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"Migrating data from {OLD_FILE}...")
    elif os.path.exists(NEW_FILE):
        with open(NEW_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

    # 2. Integrate Scraped Links
    fresh_links = scrape_iptvcat()
    for link in fresh_links:
        if link not in content:
            content += f"\n#EXTINF:0 group-title=\"Scraped\",New Stream\n{link}"

    # 3. Clean and Map
    final_output = process_and_clean(content)

    # 4. Save and Cleanup
    with open(NEW_FILE, 'w', encoding='utf-8') as f:
        f.write(final_output)
    
    print(f"Success: Playlist saved as {NEW_FILE}")

if __name__ == "__main__":
    main()
