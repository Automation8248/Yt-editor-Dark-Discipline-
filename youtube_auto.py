import os
import requests
import re
import random
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# ==========================================
# 🛑 USA TARGETING CONFIGURATION 🛑
# ==========================================

# 1. CATEGORY: 27 = Education (Best for RPM), 22 = People & Blogs
CATEGORY_ID = "27" 

# 2. VIRAL USA TITLES (30+ Options - High CTR)
# Script inme se randomly ek title tabhi uthayega jab aapka original title 'Filename' jaisa hoga.
TITLES_LIST = [
    "Wake Up and Fight - Best Motivational Video 2026",
    "It Is Time to Focus - Ultimate Morning Motivation",
    "Nobody Cares, Work Harder - Valid Advice",
    "The Mindset of a Winner - Listen Every Day",
    "Don't Waste Your Life - Powerful Speech",
    "Discipline > Motivation (Must Watch)",
    "Ghost Mode: Disappear and Come Back Shocking",
    "Why You Are Not Successful Yet - The Truth",
    "Stop Making Excuses. Just Do It.",
    "The 1% Rule - How to Get Ahead of 99% People",
    "Success is Lonely. The Harsh Truth.",
    "Be Addicted to Growth - Powerful Motivation",
    "Pain is Necessary for Growth - English Speech",
    "I Will Not Give Up - Powerful Study Motivation",
    "Prove Them Wrong. Shock Them With Success.",
    "Focus on Yourself, Not Others.",
    "Mental Toughness: How to Be Strong",
    "Dream Big. Start Small. Act Now.",
    "Silence is Power - The Sigma Mindset",
    "Your Future Needs You - Struggle Today",
    "One Day or Day One? You Decide.",
    "Control Your Mind or It Will Control You",
    "Execute. Don't Just Plan.",
    "Invest in Yourself. It Pays the Best Interest.",
    "Don't Tell People Your Plans. Show Results.",
    "Stay Hungry. Stay Foolish.",
    "If You Quit Now, You Will Regret It.",
    "Self Discipline - The Key to Freedom",
    "Believe You Can - Best Inspiration",
    "Winners Focus on Winning.",
    "Be The Hardest Worker in the Room",
    "Success Has No Shortcuts.",
    "Your Life is Your Responsibility.",
    "Stop Scrolling. Start Working."
]

# 3. USA SEO TAGS (Strictly English for Tier 1 Countries)
SEO_TAGS_LIST = [
    "Motivation", "Motivational Video", "Best Motivational Speech", "Morning Motivation",
    "Study Motivation", "Workout Motivation", "Success Mindset", "Inspiration",
    "Discipline", "Focus", "Never Give Up", "Believe in Yourself", "Hustle",
    "Entrepreneur", "Business Mindset", "Life Advice", "Wisdom", "English Speech",
    "USA", "American Motivation", "Speech 2026", "Mindset", "Growth",
    "Personal Development", "Hard Work", "Mental Health", "Sigma Male",
    "Grind", "Goals", "Ambition", "Winner", "Champion", "Shorts", "Reels"
]

# 4. UPDATED DESCRIPTION (Your Custom Text)
FIXED_DESCRIPTION = """Everything changes the moment you decide not to quit.

No matter where you are right now — starting over, struggling, healing, learning, or rebuilding — progress is still progress. Small actions done daily turn into big results over time.

Discipline beats motivation. Consistency beats talent. Patience beats luck.

Save this for the days you feel tired. Share it with someone who needs a push today.

#motivation #selfimprovement #successmindset #discipline #growthmindset #consistency #personaldevelopment #mindset #goals #focus #productivity #nevergiveup #mentalstrength #inspiration #habits #hardwork #positivity #lifestyle #entrepreneur #achievement"""

CHANNEL_CUSTOM_NAME = "My Motivation Channel"

# ==========================================
# 🛑 END CONFIGURATION 🛑
# ==========================================

def get_youtube_service():
    """Google Cloud Auth"""
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")

    if not client_id or not refresh_token:
        print("❌ Error: Secrets Missing in GitHub Settings.")
        raise ValueError("Secrets missing!")

    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )
    return build("youtube", "v3", credentials=creds)

def should_replace_title(title):
    """
    Check karta hai ki kya title 'Filename' jaisa hai?
    """
    # 1. Bahut chhota title
    if len(title) < 5: return True
    
    # 2. Keywords check
    bad_words = ["untitled", "upload", "video", "project"]
    if any(word in title.lower() for word in bad_words): return True
        
    # 3. Agar title mein Spaces nahi hain (e.g. VID_20250207)
    if " " not in title: return True
        
    # 4. Agar title mein Date format hai
    if re.search(r'\d{4}-\d{2}-\d{2}', title): return True
    
    # 5. Extension check
    if ".mp4" in title.lower() or ".mov" in title.lower(): return True
        
    return False

def send_telegram_alert(video_id, title):
    """Telegram par notification bhejta hai"""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        return

    video_link = f"https://youtu.be/{video_id}"
    msg = (
        f"<b>🚀 UPLOAD SUCCESS (USA TARGET)</b>\n\n"
        f"<b>Title:</b> {title}\n"
        f"<b>Link:</b> {video_link}\n"
        f"<b>Status:</b> PUBLIC ✅"
    )
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': msg, 'parse_mode': 'HTML'}
    
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram Error: {e}")

def main():
    try:
        print(f"--- STARTING AUTOMATION (USA MODE) ---")
        youtube = get_youtube_service()
        
        # 1. Uploads Playlist ID nikalo
        channel_response = youtube.channels().list(mine=True, part="contentDetails,snippet").execute()
        uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        print(f"✅ Connected to: {channel_response['items'][0]['snippet']['title']}")

        # 2. Recent Videos check karo
        playlist_items = youtube.playlistItems().list(
            playlistId=uploads_playlist_id, part="contentDetails", maxResults=5
        ).execute()
        
        target_video_id = None
        target_snippet = None
        
        # 3. Find Unlisted/Private Video Loop
        for item in playlist_items.get("items", []):
            vid_id = item["contentDetails"]["videoId"]
            
            # Video ki details check karo
            vid_response = youtube.videos().list(id=vid_id, part="snippet,status").execute()
            if not vid_response["items"]: continue
                
            video = vid_response["items"][0]
            status = video["status"]["privacyStatus"]
            
            # Agar video Private ya Unlisted hai, to usko pakdo
            if status in ["private", "unlisted"]:
                target_video_id = vid_id
                target_snippet = video["snippet"]
                print(f"🎯 Target Found: {vid_id} ({status})")
                break 
        
        if not target_video_id:
            print("❌ No Unlisted/Private videos found to edit.")
            return

        # --- EDITING LOGIC ---
        
        current_title = target_snippet["title"]
        new_title = current_title
        
        # A) Title Check Logic
        if should_replace_title(current_title):
            print(f"⚠️ Bad Title Detected: '{current_title}'")
            new_title = random.choice(TITLES_LIST)
            print(f"✨ New Viral Title: {new_title}")
        else:
            print(f"✅ Title is already good: '{current_title}'")
        
        # B) Tags Logic (Limit to 35 tags for safety)
        final_tags = SEO_TAGS_LIST[:35]

        # C) Update Request
        update_body = {
            "id": target_video_id,
            "snippet": {
                "categoryId": CATEGORY_ID,
                "title": new_title,
                "description": FIXED_DESCRIPTION,
                "tags": final_tags,
                "channelTitle": target_snippet["channelTitle"]
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
        
        youtube.videos().update(part="snippet,status", body=update_body).execute()
        
        print("✅ VIDEO UPDATED SUCCESSFULLY!")
        send_telegram_alert(target_video_id, new_title)

    except Exception as e:
        print(f"🔥 CRITICAL ERROR: {e}")

if __name__ == "__main__":
    main()
