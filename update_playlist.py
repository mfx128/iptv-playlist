import requests
from bs4 import BeautifulSoup
import re
import os

OUTPUT_FILE = "my_list.iptvcat.com.m3u8"

# Requirement: EPG Mapping for IPTV Smarters
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

def scrape_additional_links():
    """Scrapes iptvcat.com for any fresh public links."""
    print("Scraping for fresh links...")
    url = "https://iptvcat.com/home_22"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # Find potential stream URLs in the page source
        links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', response.text)
        return [link for link in links if ".m3u8" in link or ".ts" in link]
    except Exception as e:
        print(f"Scrape failed: {e}")
        return []

def process_and_clean(content):
    """Cleans tracking tags, adds EPG IDs, and strips whitespace."""
    # Requirement: Remove the tracking parameter
    content = content.replace("?checkedby:iptvcat.com", "")
    
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        if line.startswith("#EXTINF"):
            channel_name = line.split(",")[-1].strip()
            # Clean name for mapping (remove 1080p etc)
            base_name = re.sub(r'\s*\(\d+p\)', '', channel_name).strip()
            
            if base_name in EPG_MAP:
                tvg_id = EPG_MAP[base_name]
                if 'tvg-id=' not in line:
                    line = re.sub(r'(#EXTINF:-?\d+)\s+', fr'\1 tvg-id="{tvg_id}" ', line)
        
        if line.strip(): # Remove blank lines
            new_lines.append(line)
            
    return '\n'.join(new_lines).strip()

def main():
    # 1. Start with existing file content
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = "#EXTM3U"

    # 2. Scrape new links
    new_links = scrape_additional_links()
    
    # 3. Add new links to content if they aren't already there
    for link in new_links:
        if link not in content:
            # We add a generic header for scraped links
            content += f"\n#EXTINF:0 group-title=\"Scraped\",New Stream\n{link}"

    # 4. Clean everything and map EPG
    final_output = process_and_clean(content)

    # 5. Save back to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_output)
    print("Update complete.")

if __name__ == "__main__":
    main()
