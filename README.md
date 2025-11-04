

## Description

The REST API that automatically censors videos. It can beep out ban words in the audio and blur unwanted objects in the video (like smoking or gore) based on user settings.

## Features ✨

- 🔑 User accounts & login 
- 🔊 Beep out offensive language in audio
- 👀 Blur smoking and gore scenes in video
- 💳 Subscriptions & payments (YooKassa)
- 📧 Email notifications (like password reset)

## Tech Stack ⚙️

- **FastAPI**
- **SQLAlchemy** (async version)
- **Alembic**
- **Pytest**
- **Fastapi-users** (auth & user management)
- **FastCRUD** (automatic endpoint generation)
- **YOLO** (object detection)
- **FasterWhisper** (speech-to-text)
- **YooKassa** (payments)
