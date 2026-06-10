import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import os
import time

# ── Load Whisper model ─────────────────────────────────────
print("Loading Whisper model... (first time takes 1-2 mins)")
model = whisper.load_model("base")
print("✅ Whisper model loaded!")

# ── Audio settings ─────────────────────────────────────────
SAMPLE_RATE    = 16000   # Whisper needs 16kHz
RECORD_SECONDS = 5       # Record 5 seconds at a time

# ── Filler words to detect ─────────────────────────────────
FILLER_WORDS = [
    "um", "uh", "umm", "uhh",
    "like", "basically", "actually",
    "you know", "i mean", "sort of",
    "kind of", "right", "okay so",
    "so basically", "and um", "and uh"
]

def record_audio(duration=RECORD_SECONDS):
    """Record audio from microphone"""
    print(f"🎙️  Recording for {duration} seconds...")
    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='float32'
    )
    sd.wait()  # Wait until recording is done
    print("✅ Recording done!")
    return audio.flatten()


def transcribe_audio(audio):
    """Convert audio to text using Whisper"""
    # Save to temp file (Whisper needs a file)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    wav.write(tmp_path, SAMPLE_RATE, audio)

    # Transcribe
    result = model.transcribe(tmp_path, language="en")
    os.unlink(tmp_path)  # Delete temp file

    return result["text"].strip()


def detect_filler_words(text):
    """Count filler words in transcribed text"""
    text_lower = text.lower()
    found = []

    for filler in FILLER_WORDS:
        count = text_lower.count(filler)
        if count > 0:
            found.append({"word": filler, "count": count})

    total = sum(f["count"] for f in found)
    return found, total


def get_speech_pace(text, duration):
    """
    Calculate words per minute
    Normal pace = 120-150 WPM
    Too fast    = > 180 WPM
    Too slow    = < 90 WPM
    """
    words      = len(text.split())
    minutes    = duration / 60
    wpm        = int(words / minutes) if minutes > 0 else 0

    if wpm > 180:
        pace_label = "Too Fast"
        pace_color = "🔴"
    elif wpm < 90:
        pace_label = "Too Slow"
        pace_color = "🟡"
    else:
        pace_label = "Good Pace"
        pace_color = "🟢"

    return wpm, pace_label, pace_color


def get_speech_score(filler_count, wpm):
    """
    Score speech quality 0-100
    Penalize for filler words and bad pace
    """
    score = 100

    # Penalize filler words
    score -= filler_count * 10

    # Penalize bad pace
    if wpm > 180:
        score -= 20
    elif wpm < 90 and wpm > 0:
        score -= 15

    return max(0, min(100, score))


def analyze_speech(text, duration):
    """Full speech analysis"""
    fillers, filler_count = detect_filler_words(text)
    wpm, pace_label, pace_color = get_speech_pace(text, duration)
    score = get_speech_score(filler_count, wpm)

    return {
        "text":          text,
        "word_count":    len(text.split()),
        "wpm":           wpm,
        "pace_label":    pace_label,
        "filler_words":  fillers,
        "filler_count":  filler_count,
        "speech_score":  score
    }


# ── Main — test it ─────────────────────────────────────────
if __name__ == "__main__":
    print("\n🎯 PrepSense Speech Detector")
    print("="*40)
    print("Speak naturally for 5 seconds when prompted")
    print("Try using some filler words like 'umm' or 'basically'")
    print("="*40)

    while True:
        input("\nPress ENTER to start recording (or Ctrl+C to quit)...")

        start = time.time()
        audio = record_audio(RECORD_SECONDS)
        duration = time.time() - start

        print("Transcribing...")
        text = transcribe_audio(audio)

        if not text:
            print("❌ No speech detected. Try again.")
            continue

        result = analyze_speech(text, duration)

        print("\n" + "="*40)
        print("📝 TRANSCRIPTION:")
        print(f"   {result['text']}")
        print(f"\n📊 ANALYSIS:")
        print(f"   Words spoken:   {result['word_count']}")
        print(f"   Speech pace:    {result['wpm']} WPM — {result['pace_label']}")
        print(f"   Filler words:   {result['filler_count']}")

        if result['filler_words']:
            for f in result['filler_words']:
                print(f"   → '{f['word']}' used {f['count']} time(s)")

        print(f"\n🎯 Speech Score: {result['speech_score']}/100")
        print("="*40)