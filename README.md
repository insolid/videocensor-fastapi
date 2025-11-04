# 🎬 VideoCensor

## Description

**VideoCensor** is a REST API that automatically censors videos. It can beep out ban words in the audio and blur unwanted objects in the video (like smoking or gore) based on user settings.

## Features ✨

- 🔑 User accounts & login
- 📼 Upload videos for censorship
- 🔊 Audio: Beeps out profanity, hate speech, or your own custom words
- 👀 Video: Blurs smoking and gore scenes
- 💳 Subscriptions & payments (YooKassa)
- 📧 Email notifications (like password reset)

## Tech Stack 🛠️

- **FastAPI**
- **SQLAlchemy** (async version)
- **Alembic**
- **pytest**
- **Fastapi-users** (auth & user management)
- **FastCRUD** (automatic endpoint generation)
- **YOLO** (object detection)
- **Whisper** (speech-to-text)
- **pydub** (audio editing)
- **YooKassa** (payments)
