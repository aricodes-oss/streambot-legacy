from . import env
import requests


def _get_token():
    res = requests.post(
        "https://id.twitch.tv/oauth2/token",
        params={
            "client_id": env("TWITCH_CLIENT_ID"),
            "client_secret": env("TWITCH_CLIENT_SECRET"),
            "grant_type": "client_credentials",
        },
    )

    return res.json()["access_token"]


def _headers():
    return {"Authorization": f"Bearer {_get_token()}", "Client-Id": env("TWITCH_CLIENT_ID")}


def get_game(name):
    params = {"name": name}

    res = requests.get("https://api.twitch.tv/helix/games", params=params, headers=_headers())
    json = res.json()

    if json is not None:
        return json.get("data")

    return []


async def get_streams(game_id):
    response = requests.get(
        "https://api.twitch.tv/helix/streams", params={"game_id": game_id}, headers=_headers()
    )

    return response.json()["data"]
