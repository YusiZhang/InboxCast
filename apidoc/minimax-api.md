# Python example

```
import requests
import json

group_id = "your_group_id"
api_key = "your_api_key"

url = f"https://api.minimax.io/v1/t2a_v2?GroupId={group_id}"

payload = json.dumps({
  "model":"speech-02-hd",
  "text":"The real danger is not that computers start thinking like people, but that people start thinking like computers. Computers can only help us with simple tasks.",
  "stream":False,
  "voice_setting":{
    "voice_id":"Grinch",
    "speed":1,
    "vol":1,
    "pitch":0
  },
  "audio_setting":{
    "sample_rate":32000,
    "bitrate":128000,
    "format":"mp3",
    "channel":1
  }
})
headers = {
  'Authorization': f'Bearer {api_key}',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, stream=True, headers=headers, data=payload)
parsed_json = json.loads(response.text)

# get audio
audio_value = bytes.fromhex(parsed_json['data']['audio'])
with open('output.mp3', 'wb') as f:
    f.write(audio_value)

```