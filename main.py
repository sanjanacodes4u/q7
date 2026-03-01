import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi

app = FastAPI()

# -----------------------------
# Request Model
# -----------------------------
class AskRequest(BaseModel):
    video_url: str
    topic: str


# -----------------------------
# Extract Video ID
# -----------------------------
def extract_video_id(url: str):
    pattern = r"(?:v=|youtu\.be/)([^&?/]+)"
    match = re.search(pattern, url)
    if not match:
        raise ValueError("Invalid YouTube URL")
    return match.group(1)


# -----------------------------
# Convert Seconds to HH:MM:SS
# -----------------------------
def seconds_to_hhmmss(seconds: float):
    total = int(seconds)
    hours = total // 3600
    minutes = (total % 3600) // 60
    secs = total % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


# -----------------------------
# Endpoint
# -----------------------------
@app.post("/ask")
def ask_timestamp(request: AskRequest):
    try:
        video_id = extract_video_id(request.video_url)

        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id)

        topic_lower = request.topic.lower()

        for entry in transcript:
            if topic_lower in entry.text.lower():
                timestamp = seconds_to_hhmmss(entry.start)

                return {
                    "timestamp": timestamp,
                    "video_url": request.video_url,
                    "topic": request.topic
                }

        raise HTTPException(status_code=404, detail="Topic not found in transcript")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)