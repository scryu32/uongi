from openai import OpenAI
import os
import modi_plus
import requests
import time
from road import find_optimal_path
from dl import predict_image
import struct
from pydub import AudioSegment
import io
import pyaudio
import numpy as np
import cv2
from datetime import datetime
import math
import tensorflow as tf
from pathlib import Path

client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))
best_model = tf.keras.models.load_model('./best_model.h5')
map_size = 7
map_data = [
    [1,1,2,1,1,2,1],
    [2,1,1,1,1,1,1],
    [1,1,1,1,1,1,1],
    [1,2,1,0,1,1,1],
    [1,1,1,1,1,2,1],
    [1,2,1,1,1,1,1],
    [1,1,1,1,2,1,1],
]
danger_loc = {
    "SK 아트리움": [0, 2],
    "아주대학교 병원": [0, 5],
    "화성행궁": [1, 0],
    "수원역": [3, 1],
    "통닭거리": [4, 5],
    "스타필드 수원": [5, 1],
    "광교 테크노벨리": [6, 4],
}

bundle = modi_plus.MODIPlus()
bundle.modules
led = bundle.leds[0]
motor1 = bundle.motors[0] #왼쪽 뒤
motor2 = bundle.motors[1] #오른쪽 앞
motor3 = bundle.motors[2] #왼쪽 앞
motor4 = bundle.motors[3] #오른쪽 뒤
imu = bundle.imus[0]
display = bundle.displays[0]
speaker = bundle.speakers[0]
speaker2 = bundle.speakers[1]

# dir = os.path.join(os.path.dirname(__file__), "example_wavs")
# example_wav = "example.wav"
# api_url = "http://127.0.0.1:9880/tts"

messages = [
    {"role": "system", "content": "당신은 지진이 멈추기 전에 사람들에게 행동 요령을 알려주는 인공지능입니다. TTS로 사람들에게 메세지가 전달될것이기 때문에 이모지는 사용하지 마세요. 너무 많은 정보를 제공하려하지 마세요."},
]

class Camera:
    def __init__(self, camera_index=1):
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise Exception("카메라를 열 수 없습니다!")
        # 카메라가 안정화될 때까지 잠시 대기
        time.sleep(1)
    
    def capture_photo(self):
        ret, frame = self.cap.read()
        if not ret:
            print("사진을 찍을 수 없습니다!")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photo_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"사진이 저장되었습니다: {filename}")
        return filename
    
    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

camera = Camera()
# def request_tts(text: str):
#     payload = {
#         "text": text,
#         "text_lang": "ko",
#         "ref_audio_path": f"{dir}\\{example_wav}",
#         "aux_ref_audio_path": [f"{dir}\\example_wavs\\{i}_audio.wav" for i in range(11)],
#         "prompt_text": "",
#         "prompt_lang": "ko",
#         "text_split_method": "cut5",
#         "batch_size": 1,
#         "media_type": "wav",
#         "streaming_mode": "true"
#     }
#     try:
#         response = requests.get(api_url, params=payload, stream=True)
#         response.raise_for_status()
#         audio_data = b""
#         for chunk in response.iter_content(chunk_size=8192):
#             if chunk:
#                 audio_data += chunk
#         if len(audio_data) < 44:
#             raise ValueError("오디오 데이터가 유효하지 않음")
#         total_size = len(audio_data)
#         data_size = total_size - 44
#         audio_data = (
#             audio_data[:4] + struct.pack('<I', total_size - 8) +
#             audio_data[8:40] + struct.pack('<I', data_size) + audio_data[44:]
#         )
#         header = audio_data[:44]
#         audio_format, num_channels, sample_rate, byte_rate, block_align, bits_per_sample = struct.unpack('<HHIIHH', header[20:36])
#         audio_bytes = audio_data[44:44+data_size]
#         return (audio_bytes, sample_rate, num_channels, bits_per_sample)
#     except Exception as e:
#         print(f"TTS 요청 실패: {e}")
#         return None

# def play_tts_audio(audio_bytes, sample_rate, num_channels, bits_per_sample):
#     """
#     TTS 오디오를 컴퓨터 스피커로 재생하는 함수
#     """
#     try:
#         # PyAudio 초기화
#         p = pyaudio.PyAudio()
        
#         # 오디오 데이터를 numpy 배열로 변환
#         if bits_per_sample == 16:
#             audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
#         elif bits_per_sample == 8:
#             audio_array = np.frombuffer(audio_bytes, dtype=np.uint8)
#         else:
#             # 32비트 float로 가정
#             audio_array = np.frombuffer(audio_bytes, dtype=np.float32)
        
#         # 스트림 열기
#         stream = p.open(
#             format=pyaudio.paInt16 if bits_per_sample == 16 else pyaudio.paFloat32,
#             channels=num_channels,
#             rate=sample_rate,
#             output=True
#         )
        
#         # 오디오 재생
#         stream.write(audio_bytes)
        
#         # 스트림 정리
#         stream.stop_stream()
#         stream.close()
#         p.terminate()
        
#         print("TTS 오디오 재생 완료")
        
#     except Exception as e:
#         print(f"오디오 재생 실패: {e}")

# def speak_text(text: str):
#     """
#     텍스트를 TTS로 변환하고 컴퓨터 스피커로 출력하는 함수
#     """
#     print(f"TTS 요청: {text}")
    
#     # TTS 요청
#     result = request_tts(text)
    
#     if result is not None:
#         audio_bytes, sample_rate, num_channels, bits_per_sample = result
#         print(f"오디오 정보 - 샘플레이트: {sample_rate}, 채널: {num_channels}, 비트: {bits_per_sample}")
        
#         # 컴퓨터 스피커로 재생
#         play_tts_audio(audio_bytes, sample_rate, num_channels, bits_per_sample)
#     else:
#         print("TTS 변환 실패")

def tts(text):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=text,
        instructions="단호한 목소리로 말하세요.",
    ) as response:
        response.stream_to_file(speech_file_path)
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

def gamji_earth_quake(gamji_second, before_gamjied):
    global map_data, map_size
    if imu.acceleration_z > -47 or imu.acceleration_z < -51:
        if gamji_second < 5 and gamji_second > -3:
            display.write_text(f"지진감지 중입니다. {gamji_second}초 경과")
            print(f"지진감지 중입니다. {gamji_second}초 경과")
            time.sleep(1)
            gamji_earth_quake(gamji_second + 1, before_gamjied)
        else:
            earth_quake(map_data, map_size, before_gamjied = False)
    else:
        if before_gamjied:
            if gamji_second < 5 and gamji_second > -3:
                display.write_text(f"지진 멈춤 감지 중입니다. {gamji_second}초 경과")
                print(f"지진 멈춤 감지 중입니다. {gamji_second}초 경과")
                time.sleep(1)
                gamji_earth_quake(gamji_second - 1, before_gamjied)
            else:
                earth_quake(map_data, map_size, before_gamjied = True)

# 지진이 났을때 경보를 출력함
def streaming_chat(messages):
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=messages,
        stream=True
    )
    result = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            result += content
            # display.write_text(result)
            print(content, end="", flush=True)
    lines = result.splitlines()
    # for text in lines:
    #     speak_text(text)
    tts(result)

    print("\n")
    return result

def angleunji(): # 각도 정상화(0~359도), 180도랑 360도 없음
    angle = imu.angle_z
    if angle < 0:
        angle += 360
        if angle == 181:
            angle = 180
    else:
        if angle == 179:
            angle = 180
    display.text = f"{angle}"
    # print(dis.text)
    return angle

def front(x): # 가로 2.1, 세로 1.4
    motor1.set_speed(50)
    motor2.set_speed(50)
    motor3.set_speed(-50)
    motor4.set_speed(-50)
    time.sleep(x)
    motor1.set_speed(0)
    motor2.set_speed(0)
    motor3.set_speed(0)
    motor4.set_speed(0)

def back(x):
    motor1.set_speed(-50)
    motor2.set_speed(-50)
    motor3.set_speed(50)
    motor4.set_speed(50)
    time.sleep(x)
    motor1.set_speed(0)
    motor2.set_speed(0)
    motor3.set_speed(0)
    motor4.set_speed(0)

def right_turn(x):  # 오른쪽으로 x도 회전
    current_angle = angleunji()  # 현재 각도 읽기
    # print(f"{x}도까지 오른쪽으로 돌거임, 현재 각도: {current_angle}")
    
    # 목표 각도 계산: 현재 각도에서 x도 회전
    target_angle = (current_angle + x) % 360 + 1 # 목표 각도
    # print(f"목표 각도: {target_angle}도")
    if target_angle == 181 or target_angle == 179:
        target_angle = 180
    while True:
        current_angle = angleunji()  # 현재 각도 계속 업데이트
        angle_diff = (target_angle - current_angle + 360) % 360  # 각도 차이 계산 (음수일 경우 보정)
        
        # 각도 차이가 180도를 초과하면 반대방향으로 회전하는 방식도 고려
        if angle_diff > 180:
            angle_diff -= 360  # 반대방향으로 회전하도록 변경
        
        # 디버깅용 출력
        # print(f"현재 각도: {current_angle}, 목표 각도와의 차이: {angle_diff}")
        
        # 목표 각도에 가까워지면 속도를 줄이거나 멈춤
        if abs(angle_diff) < 1:  # ±1도 오차 범위
            # print(f"목표 각도에 도달했음, 현재 각도: {current_angle}")
            break

        # 각도 차이에 비례하여 속도 조절
        if abs(angle_diff) > 100:
            motor_speed = 50  # 각도 차이가 크면 빠르게 회전
        elif abs(angle_diff) > 50:
            motor_speed = 40  # 각도 차이가 중간이면 중간 속도로 회전
        elif abs(angle_diff) > 10:
            motor_speed = 30  # 각도 차이가 작으면 느리게 회전
        else:
            motor_speed = 18  # 각도 차이가 매우 작으면 더 천천히 회전

        # 오른쪽 회전 모터 설정 (시계방향 회전)
        motor1.set_speed(motor_speed)
        motor2.set_speed(-motor_speed)
        motor3.set_speed(motor_speed)
        motor4.set_speed(-motor_speed)
        
    # 회전이 끝나면 모터 멈추기
    motor1.set_speed(0)
    motor2.set_speed(0)
    motor3.set_speed(0)
    motor4.set_speed(0)

def left_turn(x):  # 왼쪽으로 x도 회전
    current_angle = angleunji()  # 현재 각도 읽기
    # print(f"{x}도까지 왼쪽으로 돌거임, 현재 각도: {current_angle}")
    
    # 목표 각도 계산: 현재 각도에서 x도 반대 방향으로 회전
    target_angle = (current_angle - x) % 360  # 목표 각도
    if target_angle == 181 or target_angle == 179:
        target_angle = 180

    # print(f"목표 각도: {target_angle}도")
    
    while True:
        current_angle = angleunji()  # 현재 각도 계속 업데이트
        angle_diff = (current_angle - target_angle + 360) % 360  # 각도 차이 계산 (음수일 경우 보정)
        
        # 각도 차이가 180도를 초과하면 반대방향으로 회전하는 방식도 고려
        if angle_diff > 180:
            angle_diff -= 360  # 반대방향으로 회전하도록 변경
        
        # 디버깅용 출력
        # print(f"현재 각도: {current_angle}, 목표 각도와의 차이: {angle_diff}")
        
        # 목표 각도에 가까워지면 속도를 줄이거나 멈춤
        if abs(angle_diff) < 1:  # ±1도 오차 범위
            # print(f"목표 각도에 도달했음, 현재 각도: {current_angle}")
            break

        # 각도 차이에 비례하여 속도 조절
        if abs(angle_diff) > 100:
            motor_speed = 50  # 각도 차이가 크면 빠르게 회전
        elif abs(angle_diff) > 50:
            motor_speed = 40  # 각도 차이가 중간이면 중간 속도로 회전
        elif abs(angle_diff) > 10:
            motor_speed = 30  # 각도 차이가 작으면 느리게 회전
        else:
            motor_speed = 18  # 각도 차이가 매우 작으면 더 천천히 회전

        # 왼쪽 회전 모터 설정 (반시계방향 회전)
        motor1.set_speed(-motor_speed)
        motor2.set_speed(motor_speed)
        motor3.set_speed(-motor_speed)
        motor4.set_speed(motor_speed)

    # 회전이 끝나면 모터 멈추기
    motor1.set_speed(0)
    motor2.set_speed(0)
    motor3.set_speed(0)
    motor4.set_speed(0)

def bbi():
    led.set_rgb(255, 0, 0)
    speaker.set_tune(750, 100)
    speaker2.set_tune(750, 100)

def bbo():
    led.set_rgb(0, 0, 255)
    speaker.set_tune(500, 100)
    speaker2.set_tune(500, 100)
bibi = False

def bbi_bbo(bi):
    if bi:
        bbo()
        return False
    else:
        bbi()
        return True

# 우옹이를 움직이는 능력
def move(direction, current_direction):
    global bibi
    if direction < current_direction:
        bibi = bbi_bbo(bibi)
        left_turn(current_direction-direction)

    elif direction > current_direction:
        bibi = bbi_bbo(bibi)
        right_turn(direction - current_direction)

    else:
        pass
    time.sleep(0.5)
    if 350 < current_direction < 361 or -1 < current_direction < 10 or 170 < current_direction < 190:
        bibi = bbi_bbo(bibi)
        front(1.1)
    else:
        bibi = bbi_bbo(bibi)
        front(2)
    pass

# 지도에서 특정 숫자의 위치를 찾는 함수
def find_number_position(map_data, target_number):
    for i in range(len(map_data)):
        for j in range(len(map_data[i])):
            if map_data[i][j] == target_number:
                return (i, j)
    return None

# 두 점 사이의 방향을 계산하는 함수
def calculate_direction(current_pos, target_pos):
    dx = target_pos[0] - current_pos[0]
    dy = target_pos[1] - current_pos[1]
    
    if dx > 0:  # 아래쪽
        return 180
    elif dx < 0:  # 위쪽
        return 0
    elif dy > 0:  # 오른쪽
        return 90
    elif dy < 0:  # 왼쪽
        return 270
    else:
        return None  # 같은 위치

def alert_oneonenine(building_name):
    display.write_text(f"{building_name} 건물이 붕괴되었습니다. 119에 신고합니다.")
    print(f"{building_name}  건물이 붕괴되었습니다. 119에 신고합니다.")
    time.sleep(1)

# 지도에서 순차적으로 이동하는 메인 함수
def navigate_through_map(path_map):
    global danger_loc
    current_pos = None
    current_direction = 0  # 초기 방향 (위쪽)
    target_number = 4
    start = [map_size // 2, map_size// 2]
    
    # 시작 위치 찾기 (가장 작은 숫자부터)
    while True:
        target_pos = find_number_position(path_map, target_number)
        if target_pos is None:
            print(f"숫자 {target_number}을 찾을 수 없습니다. 경로 완료!")
            break
            
        print(f"숫자 {target_number}로 이동 중...")
        print(f"현재 방향: {current_direction}")
        print(f"현재 위치: {current_pos}, 목표 위치: {target_pos}")
        

        if current_pos is not None:
            for name, pos in danger_loc.items():
                if pos[0] == current_pos[0] and pos[1] == current_pos[1]: # 자료형 차이 오류 방지
                    print("위험 지역 감지")
                    pic_path = camera.capture_photo()
                    result = predict_image(best_model, pic_path)
                    print(result)
                    if result == 'collapsed':
                        alert_oneonenine(name)
                    break

            direction = calculate_direction(current_pos, target_pos)
            if direction is not None:
                print(f"방향: {direction}도로 이동")
                move(direction, current_direction)
                current_direction = direction
                # distance = math.sqrt((start[0] - target_pos[0])**2 + (start[1] - target_pos[1])**2)
                delta_x = (start[0] - target_pos[0])
                delta_y = start[1] - target_pos[1]
                if delta_x != 0:
                    delta = delta_y/delta_x
                else:
                    delta = 0
                if delta < 0:
                    if delta_x > 0:
                        display.write_text(f"지진이 발생했습니다! 대피소는 아래쪽 {abs(delta_y)}m, 오른쪽 {abs(delta_x)}m 떨어져있습니다.")
                    else:
                        display.write_text(f"지진이 발생했습니다! 대피소는 위쪽 {abs(delta_y)}m, 왼쪽 {abs(delta_x)}m 떨어져있습니다.")
                elif delta > 0:
                    if delta_x > 0:
                        display.write_text(f"지진이 발생했습니다! 대피소는 아래쪽 {abs(delta_y)}m, 오른쪽 {abs(delta_x)}m 떨어져있습니다.")
                    else:
                        display.write_text(f"지진이 발생했습니다! 대피소는 위쪽 {abs(delta_y)}m, 왼쪽 {abs(delta_x)}m 떨어져있습니다.")
                else:
                    if delta_x == 0:
                        if delta_y < 0:
                            display.write_text(f"지진이 발생했습니다! 대피소는 아래쪽 {abs(delta_y)}m 떨어져있습니다.")
                        else:
                            display.write_text(f"지진이 발생했습니다! 대피소는 위쪽 {abs(delta_y)}m 떨어져있습니다.")
                    else:
                        if delta_x > 0:
                            display.write_text(f"지진이 발생했습니다! 대피소는 오른쪽 {abs(delta_x)}m 떨어져있습니다.")
                        else:
                            display.write_text(f"지진이 발생했습니다! 대피소는 왼쪽 {abs(delta_x)}m 떨어져있습니다.")
        
        current_pos = target_pos
        target_number += 1
        
        # 잠시 대기
        time.sleep(0.5)

def earth_quake(map_data, map_size, before_gamjied):
    global messages
    if before_gamjied == False:
        messages.append({"role": "user", "content": "현재 대한민국 경기도 수원시에 지진이 발생했습니다. 지진이 멈추기 전에 사람들에게 행동 요령을 알려주세요."})
        result = streaming_chat(messages)
        messages.append({"role": "assistant", "content": result})
        gamji_earth_quake(0, True)
    else:
        map_path = find_optimal_path(map_data, map_size)
        navigate_through_map(map_path)

# 메인 실행 코드
if __name__ == "__main__":
    while True:
        gamji_earth_quake(0, False)




