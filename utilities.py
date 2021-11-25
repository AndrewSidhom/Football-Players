import requests
from config import api_base_url, api_headers


def call_api(endpoint, data):
    return requests.request("GET", api_base_url+endpoint, headers=api_headers, data=data).text
