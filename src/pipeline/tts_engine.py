"""
tts_engine.py

Offline TTS using pyttsx3.

This version is much more stable on Windows because a NEW engine is created
for every beat instead of reusing one engine for the whole job.
"""

import os
import time
import wave
import contextlib
from dataclasses import dataclass, field

import pyttsx3


class TTSError(Exception):
    pass


@dataclass
class BeatAudio:
    beat_index: int
    wav_path: str
    duration_sec: float


@dataclass
class AudioResult:
    beat_audios: list = field(default_factory=list)


def _wav_duration(path: str) -> float:
    with contextlib.closing(wave.open(path, "rb")) as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        return frames / float(rate)


def _create_engine(voice: str):
    engine = pyttsx3.init()

    if voice and voice.lower() != "default":
        try:
            for v in engine.getProperty("voices"):
                vid = (v.id or "").lower()
                vname = (v.name or "").lower()

                if voice.lower() in vid or voice.lower() in vname:
                    engine.setProperty("voice", v.id)
                    break
        except Exception:
            pass

    try:
        rate = engine.getProperty("rate")
        engine.setProperty("rate", rate - 10)
    except Exception:
        pass

    return engine


def synthesize(beats, voice: str, out_dir: str) -> AudioResult:
    os.makedirs(out_dir, exist_ok=True)

    result = AudioResult()

    print("=" * 60)
    print("TTS START")
    print("=" * 60)

    for beat in beats:

        wav_path = os.path.join(
            out_dir,
            f"beat_{beat.index:03d}.wav"
        )

        engine = None

        try:
            print()
            print(f"[Beat {beat.index}]")
            print("Text :", beat.text)
            print("Output :", wav_path)

            engine = _create_engine(voice)

            print("Saving...")

            engine.save_to_file(beat.text, wav_path)

            print("Running...")

            engine.runAndWait()

            print("Stopping...")

            engine.stop()

            # Wait for file to appear
            timeout = 10.0
            start = time.time()

            while not os.path.exists(wav_path):
                if time.time() - start > timeout:
                    raise TTSError("Timed out waiting for WAV file.")
                time.sleep(0.1)

            duration = _wav_duration(wav_path)

            print(f"Done ({duration:.2f}s)")

            result.beat_audios.append(
                BeatAudio(
                    beat_index=beat.index,
                    wav_path=wav_path,
                    duration_sec=duration,
                )
            )

            del engine

        except Exception as e:

            try:
                if engine:
                    engine.stop()
            except Exception:
                pass

            raise TTSError(
                f"TTS failed on beat {beat.index}\n"
                f"Text: {beat.text}\n"
                f"Reason: {e}"
            )

    print()
    print("=" * 60)
    print("TTS COMPLETE")
    print("=" * 60)

    return result