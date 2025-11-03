import os
import re
import subprocess
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import cv2
from faster_whisper import WhisperModel
from pydub import AudioSegment
from pydub.generators import Sine
from ultralytics import YOLO

from app.core.config import settings
from app.models.videojobs import VideoJob


@dataclass
class WordInfo:
    value: str
    start: float
    end: float


class ITranscriber(ABC):
    @abstractmethod
    def transcribe_with_timestamps(self, file_path: str, lang: str) -> list[WordInfo]:
        pass


class Transcriber(ITranscriber, WhisperModel):
    def transcribe_with_timestamps(self, file_path: str, lang: str) -> list[WordInfo]:
        segments = super().transcribe(file_path, lang, word_timestamps=True)[0]
        words = []
        for segment in segments:
            for w in segment.words:  # type: ignore
                # Merge hypenated words into 1 word, as whisper may split
                # word like `check-in` into `check` and `-in`.
                if w.word.startswith("-"):
                    words[-1].value += self._normalize_word(w.word)
                    continue
                words.append(
                    WordInfo(
                        value=self._normalize_word(w.word),
                        start=w.start,
                        end=w.end,
                    )
                )
        return words

    def _normalize_word(self, word):
        """Bring the word to the valid format"""
        return re.sub(r"[^\w-]", "", word.lower().strip())


class AudioCensor:
    def __init__(self, transcriber: ITranscriber):
        self.transcriber = transcriber

    def censor(
        self,
        input_path: str,
        output_path: str,
        ban_words: set[str],
        lang: str,
        output_format: str = "wav",
    ) -> str | None:
        """Censor audio track and return censored audio path"""
        if not AudioCensor.has_audio(input_path):
            return

        words = self.transcriber.transcribe_with_timestamps(input_path, lang)
        audio = AudioSegment.from_file(input_path)

        # Apply censoring sound to detected ban words
        for w in words:
            if w.value in ban_words:
                start_ms, end_ms = w.start * 1000, w.end * 1000
                duration_ms = end_ms - start_ms
                beep_sound = self._create_beep_sound(duration_ms)
                audio = audio[:start_ms] + beep_sound + audio[end_ms:]

        audio.export(output_path, format=output_format)
        return output_path

    def _create_beep_sound(self, duration_ms: float) -> AudioSegment:
        beep = Sine(1000).to_audio_segment(duration=duration_ms)
        return beep - 20  # Reduce volume

    @staticmethod
    def has_audio(input_path: str) -> bool:
        result = subprocess.run(
            ["ffprobe", "-i", input_path, "-show_streams", "-select_streams", "a"],
            capture_output=True,
            text=True,
        )
        return bool(result.stdout)


class VisualCensor:
    def censor(
        self,
        input_path: str,
        output_path: str,
        ban_class_idxs: list[int],
    ) -> str:
        """Censor video track and return censored video path"""
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        model = YOLO(settings.yolo_model_path)
        # Blur frames where ban classes detected
        for frame_data in model(input_path, classes=ban_class_idxs, stream=True):
            for box in frame_data.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                frame_data.orig_img[y1:y2, x1:x2] = cv2.GaussianBlur(
                    frame_data.orig_img[y1:y2, x1:x2], (151, 151), 0
                )
            out.write(frame_data.orig_img)

        # Release resources
        cap.release()
        out.release()

        return output_path


class VideoJobService:
    def __init__(self, videojob: VideoJob) -> None:
        self.vj = videojob

    def censor(self, tmp_files_dir: Path, output_path: str):
        """Apply visual and audio censorship and save result video"""
        if not self._has_audio_config() and not self._has_visual_config():
            return self._save_video_as_is(output_path)

        censored_audio_path = None
        censored_picture_path = None

        # Apply audio censorship if needed
        if self._has_audio_config():
            ban_words = self._get_ban_words()
            transcriber = Transcriber("medium", device="cpu", compute_type="int8")
            audio_censor = AudioCensor(transcriber)
            censored_audio_path = audio_censor.censor(
                self.vj.input_video_path,  # type: ignore
                str(tmp_files_dir / f"{uuid.uuid4()}.wav"),
                ban_words,
                self.vj.language.value,
            )

        # Apply visual censorship if needed
        if self._has_visual_config():
            ban_class_idxs = self._get_ban_class_idxs()
            censored_picture_path = VisualCensor().censor(
                self.vj.input_video_path,  # type: ignore
                str(tmp_files_dir / f"{uuid.uuid4()}.mp4"),
                ban_class_idxs,
            )

        # Save the censored video to result path
        self._save_video(output_path, censored_picture_path, censored_audio_path)

        # Clean up indermediate files
        if censored_audio_path and os.path.isfile(str(censored_audio_path)):
            os.remove(censored_audio_path)
        if censored_picture_path and os.path.isfile(str(censored_picture_path)):
            os.remove(censored_picture_path)

        return output_path

    def _has_audio_config(self) -> bool:
        ac = self.vj.audio_config
        return bool(ac and any((ac.profanity, ac.hate_speech, ac.own_words)))

    def _has_visual_config(self) -> bool:
        vc = self.vj.visual_config
        return bool(vc and any((vc.smoking, vc.gore)))

    def _get_ban_words(self) -> set[str]:
        """Collect ban words from own_words and corresponding files"""
        ban_words = set()
        own_words = self.vj.audio_config.own_words
        if own_words:
            own_words = own_words.lower().strip()
            ban_words.update({w for w in own_words.split(",") if w})

        @lru_cache(maxsize=None)
        def pull_words_from_file(file_path: str) -> set[str]:
            """Read file and return set of words"""
            with open(file_path, "r", encoding="utf8") as file:
                return {line.lower().strip() for line in file if line.strip()}

        # Collect ban words from predefined files
        if self.vj.audio_config.profanity:
            profanity_file = os.path.join(
                settings.ban_words_dir,
                f"profanity_{self.vj.language}.txt",
            )
            ban_words.update(pull_words_from_file(profanity_file))

        if self.vj.audio_config.hate_speech:
            hate_speech_file = os.path.join(
                settings.ban_words_dir,
                f"hate_speech_{self.vj.language}.txt",
            )
            ban_words.update(pull_words_from_file(hate_speech_file))

        return ban_words

    def _get_ban_class_idxs(self) -> list[int]:
        """Collect classes to ban in video"""
        classes = []
        if self.vj.visual_config.gore:
            classes.append(1)
        if self.vj.visual_config.smoking:
            classes.append(3)
        return classes

    def _save_video(
        self,
        output_path: str,
        censored_video_path: str | None = None,
        censored_audio_path: str | None = None,
    ):
        """Save censored video and audio to one output file"""
        # Merge censored parts if present
        stmt = [
            "ffmpeg",
            "-i",
            censored_video_path or self.vj.input_video_path,
            "-i",
            censored_audio_path or self.vj.input_video_path,
            "-c:v",
            "libx264" if censored_video_path else "copy",
            "-c:a",
            "aac" if censored_audio_path else "copy",
            "-map",
            "0:v:0",
            *(
                ["-map", "1:a:0"]
                if AudioCensor.has_audio(self.vj.input_video_path)  # type: ignore
                else []
            ),
            output_path,
        ]
        subprocess.run(stmt)

    def _save_video_as_is(self, output_path: str):
        """Save input video as is"""
        stmt = [
            "ffmpeg",
            "-i",
            self.vj.input_video_path,
            "-c:v",
            "copy",
            "-c:a",
            "copy",
            output_path,
        ]
        subprocess.run(stmt)
