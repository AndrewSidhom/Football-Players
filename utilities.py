import requests
from config import api_base_url, api_headers


def call_api(endpoint):
    response = requests.request("GET", api_base_url+endpoint, headers=api_headers)
    api_calls_remaining = response.headers["x-ratelimit-requests-remaining"]
    return response, api_calls_remaining
