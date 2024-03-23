import requests

url = "https://api.zhishuyun.com/midjourney/imagine?token=1e0242a1b5534eb8a2663fc2fcf5778e"

headers = {
    "content-type": "application/json"
}

payload = {
    "prompt": "a beautiful cat",
    "translation": True
}

response = requests.post(url, json=payload, headers=headers)
print(response.json()["image_url"])