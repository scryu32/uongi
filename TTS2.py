from openai import OpenAI
import os
import pyaudio
from pydub import AudioSegment
import io

client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))

response =  client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="coral",
    input="Today is a wonderful day to build something people love!",
    instructions="Speak in a cheerful and positive tone.",
)

with open("speech.mp3", "wb") as f:
    f.write(response.content)

audio = AudioSegment.from_mp3("speech.mp3")

# WAV 데이터를 메모리에 저장
wav_io = io.BytesIO()
audio.export(wav_io, format="wav")
wav_io.seek(0)

# PyAudio 초기화
p = pyaudio.PyAudio()

# 오디오 스트림 열기
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=audio.frame_rate,
                output=True,
                frames_per_buffer=1024)

# WAV 데이터를 스트리밍하여 출력
chunk_size = 1024
while chunk := wav_io.read(chunk_size):
    stream.write(chunk)

# 스트림 종료
stream.stop_stream()
stream.close()
p.terminate()