"""API.py
>API利用メゾッド
"""
from datetime import datetime
import time
import requests
from src.core import BASE

class YouTubeAPI():
    @staticmethod
    def get_schedule(channel_id: str, max_results: int = 10):
        max_results = min(max_results, 20)
        
        search_url = "https://www.googleapis.com/youtube/v3/search"
        search_params = {
            "key": BASE.YOUTUBE_API_KEY,
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
            "key": BASE.YOUTUBE_API_KEY,
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

        result.sort(key=lambda x: x["date"])
        return result

class TwitchAPI():
    _cached_token = None
    _cached_expires_at = 0

    @staticmethod
    def access_token():
        """Twitch APIのアクセストークン
        命名意図：アクセストークンを格納する変数としての利用を目的としているため。
        """
        if (TwitchAPI._cached_token and time.time() < TwitchAPI._cached_expires_at):
            return TwitchAPI._cached_token

        try:
            token_data = BASE.dataload(BASE.TWITCH_TOKEN_PATH)
        except FileNotFoundError:
            BASE.datasave({}, BASE.TWITCH_TOKEN_PATH)
            token_data = BASE.dataload(BASE.TWITCH_TOKEN_PATH)

        if (token_data == {} or
            token_data.get("expires_at") is None or
            time.time() >= token_data["expires_at"]):

            url = "https://id.twitch.tv/oauth2/token"
            params = {
                "client_id": BASE.client_id,
                "client_secret": BASE.client_secret,
                "grant_type": "client_credentials"
            }

            response = requests.post(url, params=params)
            response.raise_for_status()
            auth_data = response.json()

            access_token = auth_data["access_token"]
            expires_in = auth_data["expires_in"]
            expires_at = time.time() + expires_in

            token_data = {
                "access_token": access_token,
                "expires_at": expires_at
            }
            BASE.datasave(token_data, BASE.TWITCH_TOKEN_PATH)
        else:
            access_token = token_data["access_token"]
            expires_at = token_data["expires_at"]

        # キャッシュに保存
        TwitchAPI._cached_token = access_token
        TwitchAPI._cached_expires_at = expires_at

        return access_token

    @staticmethod
    def get_broadcaster_id(username: str) -> str:
        """
        指定された Twitch ユーザー名からブロードキャスターIDを取得する。

        Raises:
            ValueError: ユーザー名が空、またはTwitchユーザーが見つからなかった場合。
        """
        if not username:
            raise ValueError("username が空です")

        url = "https://api.twitch.tv/helix/users"
        headers = {
            "Authorization": f"Bearer {TwitchAPI.access_token()}",
            "Client-Id": BASE.client_id
        }
        params = {"login": username}

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        users = response.json().get("data", [])
        if not users:
            raise ValueError(f"Twitchユーザーが見つかりません: {username}")
        
        return users[0]["id"]

    @staticmethod
    def get_schedule(broadcaster_id: str, max_results: int = 10) -> list:
        """
        指定されたブロードキャスターIDの配信予定を取得する。
        配信予定が存在しない場合は空のリストを返す。

        Returns:
            List[dict]: 各予定のタイトルと日時を格納した辞書のリスト。
        """
        max_results = min(max_results, 20)

        url = "https://api.twitch.tv/helix/schedule"
        headers = {
            "Authorization": f"Bearer {TwitchAPI.access_token()}",
            "Client-Id": BASE.client_id
        }
        params = {
            "broadcaster_id": broadcaster_id,
            "first": max_results
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 404:
            return []

        response.raise_for_status()
        segments = response.json().get("data", {}).get("segments", [])
        if not segments:
            return []

        results = []
        for segment in segments:
            title = segment.get("title", "（タイトルなし）")
            start_time = segment["start_time"]
            dt = datetime.fromisoformat(start_time.replace("Z", "+00:00")).astimezone()
            results.append({
                "date": dt,
                "title": title
            })

        return results