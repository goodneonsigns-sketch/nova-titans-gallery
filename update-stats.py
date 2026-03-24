#!/usr/bin/env python3
"""
Nova Titans Stats Updater — Cron Job
Scrapes latest batting/pitching stats from browardhighschoolbaseball.com
Updates data.json and rebuilds the site
Run day after each game
"""
import json
import re
import subprocess
import os
import sys
from datetime import datetime

STATS_URL = "https://www.browardhighschoolbaseball.com/team/nova-titans/varsity-stats/batting/"
SCHEDULE_URL = "https://www.browardhighschoolbaseball.com/team/nova-titans/varsity-schedule/"
ROSTER_URL = "https://www.browardhighschoolbaseball.com/team/nova-titans/varsity-roster/"
SITE_DIR = os.path.dirname(os.path.abspath(__file__))

def fetch_url(url):
    """Fetch URL content using curl."""
    result = subprocess.run(['curl', '-s', url], capture_output=True, text=True, timeout=30)
    return result.stdout

def parse_batting_stats(html):
    """Parse batting stats table from the HTML."""
    stats = {}
    # Find the batting stats table - look for rows with player links
    pattern = r'<a[^>]*href="/player/[^"]*"[^>]*>([^<]+)</a></td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>'
    
    # Simpler approach: split by player links and extract numbers
    lines = html.split('\n')
    for line in lines:
        if '/player/' in line and '<td' in line:
            # Extract player name
            name_match = re.search(r'>([^<]+)</a>', line)
            if not name_match:
                continue
            name = name_match.group(1).strip()
            
            # Extract all numbers in td tags
            nums = re.findall(r'<td[^>]*>([^<]*)</td>', line)
            nums = [n.strip() for n in nums if n.strip()]
            
            # Expected order: AB R H RBI 2B 3B HR SF SH FC ROE HBP BB K BA OBP SLG
            if len(nums) >= 17:
                try:
                    stats[name] = {
                        "AB": int(nums[0]), "R": int(nums[1]), "H": int(nums[2]),
                        "RBI": int(nums[3]), "2B": int(nums[4]), "3B": int(nums[5]),
                        "HR": int(nums[6]), "BB": int(nums[12]), "K": int(nums[13]),
                        "BA": nums[14], "OBP": nums[15], "SLG": nums[16]
                    }
                except (ValueError, IndexError):
                    pass
    
    return stats

def parse_schedule(html):
    """Parse schedule/results from HTML."""
    games = []
    # This is complex HTML parsing - for now use the text extraction approach
    # The cron will call web_fetch via openclaw for better parsing
    return games

def check_new_dropbox_photos():
    """Check for new game photos in Dana's Dropbox."""
    env_file = os.path.join(SITE_DIR, '../../.secrets/nova-titans.env')
    if not os.path.exists(env_file):
        print("No Dropbox credentials found")
        return []
    
    # Load credentials
    creds = {}
    with open(env_file) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, val = line.strip().split('=', 1)
                creds[key] = val.strip('"').strip("'")
    
    token = creds.get('DROPBOX_ACCESS_TOKEN', '')
    if not token:
        print("No Dropbox access token")
        return []
    
    # List folders in /Nova Baseball/Nova Titans/
    result = subprocess.run([
        'curl', '-s', '-X', 'POST',
        'https://api.dropboxapi.com/2/files/list_folder',
        '-H', f'Authorization: Bearer {token}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({"path": "/Nova Baseball/Nova Titans", "recursive": False})
    ], capture_output=True, text=True, timeout=30)
    
    try:
        data = json.loads(result.stdout)
        folders = [e['name'] for e in data.get('entries', []) if e['.tag'] == 'folder']
        return folders
    except:
        print(f"Dropbox API error: {result.stdout[:200]}")
        return []

def git_push(message):
    """Commit and push changes to GitHub."""
    os.chdir(SITE_DIR)
    subprocess.run(['git', 'add', '-A'], capture_output=True)
    subprocess.run(['git', 'commit', '-m', message], capture_output=True)
    subprocess.run(['git', 'push'], capture_output=True)
    print(f"Pushed to GitHub: {message}")

def main():
    print(f"=== Nova Titans Stats Update — {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
    
    # 1. Fetch latest batting stats
    print("Fetching batting stats...")
    html = fetch_url(STATS_URL)
    if html:
        stats = parse_batting_stats(html)
        if stats:
            print(f"  Parsed {len(stats)} player batting stats")
            # Save stats
            with open(os.path.join(SITE_DIR, 'batting-stats.json'), 'w') as f:
                json.dump({"updated": datetime.now().isoformat(), "stats": stats}, f, indent=2)
        else:
            print("  WARNING: Could not parse batting stats from HTML")
    else:
        print("  ERROR: Could not fetch stats page")
    
    # 2. Check for new Dropbox photos
    print("Checking Dropbox for new game photos...")
    folders = check_new_dropbox_photos()
    if folders:
        print(f"  Found {len(folders)} game folders: {', '.join(folders)}")
    
    # 3. Rebuild site
    print("Rebuilding site...")
    os.chdir(SITE_DIR)
    result = subprocess.run([sys.executable, 'build-site.py'], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"  Build error: {result.stderr}")
        return
    
    # 4. Push to GitHub
    git_push(f"Stats update {datetime.now().strftime('%Y-%m-%d')}")
    
    print("=== Update complete ===")

if __name__ == '__main__':
    main()
