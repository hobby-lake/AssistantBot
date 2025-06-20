from datetime import datetime, timedelta
import calendar
import discord
from discord import ApplicationContext
from src import JSON, PATH
import requests

YOUTUBE_API_KEY = "AIzaSyDPDpAG1BNYFT7xpU2b-XneoqTSCC7nWw8"
client_id = "p5awiw3bbnat4fjkxae1upvlsb4lcz"
client_secret = "cpv4j7bg11trw8l0niq4a4a1s2soop"

# テスト用ダミースケジュール
def get_mock_schedule():
    today = datetime.now()
    result = []
    for i in range(0, 45, 3):
        date = today + timedelta(days=i)
        result.append({
            "date": date,
            "title": f"配信タイトル（{date.strftime('%H:%M')}）"
        })
    return result

# YouTube API
def get_schedule_from_youtube(channel_id: str, max_results=25):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    search_params = {
        "key": YOUTUBE_API_KEY,
        "channelId": channel_id,
        "eventType": "upcoming",
        "type": "video",
        "order": "date",
        "part": "id",
        "maxResults": max_results
    }

    search_response = requests.get(search_url, params=search_params)
    search_data = search_response.json()

    video_ids = [item["id"]["videoId"] for item in search_data.get("items", [])]
    if not video_ids:
        return []

    videos_url = "https://www.googleapis.com/youtube/v3/videos"
    videos_params = {
        "key": YOUTUBE_API_KEY,
        "id": ",".join(video_ids),
        "part": "snippet,liveStreamingDetails"
    }

    videos_response = requests.get(videos_url, params=videos_params)
    videos_data = videos_response.json()

    result = []
    for item in videos_data.get("items", []):
        snippet = item["snippet"]
        details = item.get("liveStreamingDetails", {})
        scheduled = details.get("scheduledStartTime")
        if scheduled:
            dt = datetime.fromisoformat(scheduled.replace("Z", "+00:00")).astimezone()
            result.append({
                "date": dt,
                "title": snippet["title"]
            })

    return result

# Twitch API
def get_twitch_app_access_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }

    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()["access_token"]

def get_twitch_broadcaster_id(username: str, access_token: str):
    url = "https://api.twitch.tv/helix/users"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-Id": client_id
    }
    params = {
        "login": username
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    users = data.get("data", [])
    if not users:
        raise ValueError(f"Twitchユーザーが見つかりません: {username}")
    return users[0]["id"]

def get_schedule_from_twitch(broadcaster_id: str, access_token: str, max_results=5):
    url = "https://api.twitch.tv/helix/schedule"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-Id": client_id
    }
    params = {
        "broadcaster_id": broadcaster_id,
        "first": max_results
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 404:
        # スケジュール未登録などによる 404 は無視
        return []

    response.raise_for_status()
    data = response.json()

    results = []
    for segment in data.get("data", {}).get("segments", []):
        title = segment.get("title", "（タイトルなし）")
        start_time = segment["start_time"]
        dt = datetime.fromisoformat(start_time.replace("Z", "+00:00")).astimezone()
        results.append({
            "date": dt,
            "title": title
        })

    return results

# YouTube + Twitch 統合スケジュール取得
def get_combined_schedule(streamer_config, twitch_token):
    result = []

    if "youtube" in streamer_config:
        result += get_schedule_from_youtube(streamer_config["youtube"])

    if "twitch" in streamer_config:
        try:
            broadcaster_id = get_twitch_broadcaster_id(
                username=streamer_config["twitch"],
                access_token=twitch_token,
            )
            result += get_schedule_from_twitch(
                broadcaster_id=broadcaster_id,
                access_token=twitch_token,
            )
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                # スケジュールなし→無視
                pass
            else:
                raise

    return sorted(result, key=lambda x: x["date"])

def build_schedule_embed(guild_id: int, streamer_id, schedule_list):
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]

    now = datetime.now()
    this_month = []
    next_month = []
    future = []

    for item in schedule_list:
        d = item["date"]
        formatted = f"{d.strftime('%m/%d')} ({weekdays[d.weekday()]}) {item['title']}"

        if d.year == now.year and d.month == now.month:
            this_month.append(formatted)
        elif d.year == now.year and d.month == (now.month % 12) + 1:
            next_month.append(formatted)
        else:
            future.append(formatted)

    # 配信者の表示名取得
    path = PATH.get_json(guild_id, "streamer")
    streamer_data = JSON.load(path)
    streamer_name = streamer_data[streamer_id]["display_name"]

    embed = discord.Embed(title=f"📅 {streamer_name}の配信予定", color=0x00aaff)

    if this_month:
        embed.add_field(name=f"{now.month}月の予定", value="\n".join(this_month), inline=False)
    if next_month:
        embed.add_field(name=f"{(now.month % 12) + 1}月の予定", value="\n".join(next_month), inline=False)
    if future:
        embed.add_field(name="以降の予定", value="\n".join(future), inline=False)

    embed.set_footer(text="毎時自動更新されます")
    return embed