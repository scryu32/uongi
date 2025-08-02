import requests
import struct
import pyaudio
import os
import numpy as np

dir = os.path.join(os.path.dirname(__file__), "example_wavs")
example_wav = "example.wav"
api_url = "http://127.0.0.1:9880/tts"

def request_tts(text: str):
    payload = {
        "text": text,
        "text_lang": "ko",
        "ref_audio_path": f"{dir}\\{example_wav}",
        "aux_ref_audio_path": [f"{dir}\\example_wavs\\{i}_audio.wav" for i in range(11)],
        "prompt_text": "",
        "prompt_lang": "ko",
        "text_split_method": "cut5",
        "batch_size": 1,
        "media_type": "wav",
        "streaming_mode": "true"
    }
    try:
        response = requests.get(api_url, params=payload, stream=True)
        response.raise_for_status()
        audio_data = b""
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                audio_data += chunk
        if len(audio_data) < 44:
            raise ValueError("오디오 데이터가 유효하지 않음")
        total_size = len(audio_data)
        data_size = total_size - 44
        audio_data = (
            audio_data[:4] + struct.pack('<I', total_size - 8) +
            audio_data[8:40] + struct.pack('<I', data_size) + audio_data[44:]
        )
        header = audio_data[:44]
        audio_format, num_channels, sample_rate, byte_rate, block_align, bits_per_sample = struct.unpack('<HHIIHH', header[20:36])
        audio_bytes = audio_data[44:44+data_size]
        return (audio_bytes, sample_rate, num_channels, bits_per_sample)
    except Exception as e:
        print(f"TTS 요청 실패: {e}")
        return None

def play_tts_audio(audio_bytes, sample_rate, num_channels, bits_per_sample):
    """
    TTS 오디오를 컴퓨터 스피커로 재생하는 함수
    """
    try:
        # PyAudio 초기화
        p = pyaudio.PyAudio()
        
        # 오디오 데이터를 numpy 배열로 변환
        if bits_per_sample == 16:
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        elif bits_per_sample == 8:
            audio_array = np.frombuffer(audio_bytes, dtype=np.uint8)
        else:
            # 32비트 float로 가정
            audio_array = np.frombuffer(audio_bytes, dtype=np.float32)
        
        # 스트림 열기
        stream = p.open(
            format=pyaudio.paInt16 if bits_per_sample == 16 else pyaudio.paFloat32,
            channels=num_channels,
            rate=sample_rate,
            output=True
        )
        
        # 오디오 재생
        stream.write(audio_bytes)
        
        # 스트림 정리
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        print("TTS 오디오 재생 완료")
        
    except Exception as e:
        print(f"오디오 재생 실패: {e}")

def speak_text(text: str):
    """
    텍스트를 TTS로 변환하고 컴퓨터 스피커로 출력하는 함수
    """
    print(f"TTS 요청: {text}")
    
    # TTS 요청
    result = request_tts(text)
    
    if result is not None:
        audio_bytes, sample_rate, num_channels, bits_per_sample = result
        print(f"오디오 정보 - 샘플레이트: {sample_rate}, 채널: {num_channels}, 비트: {bits_per_sample}")
        
        # 컴퓨터 스피커로 재생
        play_tts_audio(audio_bytes, sample_rate, num_channels, bits_per_sample)
    else:
        print("TTS 변환 실패")


speak_text("안녕")