#!/bin/sh

curl -X 'POST' \
  'http://0.0.0.0:8000/upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'sensor_id=b2d2b89b-f159-4eae-b44c-4aee925c4c9a' \
  -F 'timestamp=2024-05-16T19:07:06.767091' \
  -F 'lat=32.875573' \
  -F 'lon=-117.2323364' \
  -F 'accuracy=20' \
  -F 'battery=100' \
  -F 'temperature=40' \
  -F 'audio_file=@example.wav;type=audio/wav'
