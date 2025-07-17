# Request (non-streaming)
```
curl --location 'https://api.minimax.io/v1/t2a_v2?GroupId=${group_id}' \
--header 'Authorization: Bearer ${api_key}' \
--header 'Content-Type: application/json' \
--data '{
    "model":"speech-02-hd",
    "text":"The real danger is not that computers start thinking like people, but that people start thinking like computers. Computers can only help us with simple tasks.",
    "stream":false,
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
  }'
  ```

  # Response (non-streaming)
  ```
  {
    "data":{
        "audio":"hex audio",
        "status":2,
        "subtitle_file":"https://minimax-algeng-chat-tts.oss-cn-wulanchabu.aliyuncs.com/XXXX",
    },     
     "extra_info":{
        "audio_length":5746,
        "audio_sample_rate":32000,
        "audio_size":100845,
        "audio_bitrate":128000,
        "word_count":300,
        "invisible_character_ratio":0,
        "audio_format":"mp3",
        "usage_characters":630
    },
    "trace_id":"01b8bf9bb7433cc75c18eee6cfa8fe21",
    "base_resp":{
        "status_code":0,
        "status_msg":""
    }
}
```