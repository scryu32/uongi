import os
import modi_plus
import requests
import time
from road import find_optimal_path
import struct
from pydub import AudioSegment
import io
import pyaudio
from datetime import datetime
import math
from pathlib import Path

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
            angle_diff = abs(angle_diff-360) 
        
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
            angle_diff = abs(angle_diff-360) 
        
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
def move(direction, current_direction, now_num):
    global bibi

    if direction < current_direction:
        if current_direction-direction < 180:
            bibi = bbi_bbo(bibi)
            left_turn(current_direction-direction)
        elif current_direction-direction > 190:
            bibi = bbi_bbo(bibi)
            right_turn(current_direction-direction-180)
        else:
            bibi = bbi_bbo(bibi)
            right_turn(current_direction-direction)


    elif direction > current_direction:
        if now_num < 14:
            if direction - current_direction < 180:
                bibi = bbi_bbo(bibi)
                right_turn(direction - current_direction)
            elif current_direction-direction > 190:
                bibi = bbi_bbo(bibi)
                left_turn(direction-current_direction-180)
            else:
                bibi = bbi_bbo(bibi)
                left_turn(direction-current_direction)
        else:
            if direction - current_direction < 180:
                bibi = bbi_bbo(bibi)
                right_turn(direction - current_direction)
            else:
                bibi = bbi_bbo(bibi)
                left_turn(direction-current_direction-180)
    else:
        pass
    time.sleep(0.5)
    if 350 < abs(direction) < 361 or -1 < abs(direction) < 10 or 170 < abs(direction) < 190:
        print("뺀거절댓값", abs(direction-current_direction))
        print("디렉션, 커렌트 디렉션", direction, current_direction)
        bibi = bbi_bbo(bibi)
        front(1.3)
    else:
        print("뺀거절댓값", abs(direction-current_direction))
        print("디렉션, 커렌트 디렉션", direction, current_direction)
        bibi = bbi_bbo(bibi)
        front(1.88)
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
            front(1.88)
            break
            
        print(f"숫자 {target_number}로 이동 중...")
        print(f"현재 방향: {current_direction}")
        print(f"현재 위치: {current_pos}, 목표 위치: {target_pos}")
        

        if current_pos is not None:
            for name, pos in danger_loc.items():
                if pos[0] == current_pos[0] and pos[1] == current_pos[1]: # 자료형 차이 오류 방지
                    print("위험 지역 감지")
                    if name == "SK 아트리움":
                        pic_path = "./image/col.png"
                    elif name == "아주대학교 병원":
                        pic_path = "./image/no2.png"
                    elif name == "화성행궁":
                        pic_path = "./image/no.png"
                    elif name == "수원역":
                        pic_path = "./image/col2.png"
                    elif name == "통닭거리":
                        pic_path = "./image/col.png"
                    elif name == "스타필드 수원":
                        pic_path = "./image/no.png"
                    elif name == "광교 테크노벨리":
                        pic_path = "./image/no.png"
                    print('')
                    if 'a' == 'collapsed':
                        alert_oneonenine(name)
                    break

            direction = calculate_direction(current_pos, target_pos)
            if direction is not None:
                print(f"방향: {direction}도로 이동")
                move(direction, current_direction, target_number    )
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
    if before_gamjied == False:
        gamji_earth_quake(0, True)
    else:
        map_path = find_optimal_path(map_data, map_size)
        navigate_through_map(map_path)

# 메인 실행 코드
if __name__ == "__main__":
    print("메인 루프 실행")
    map_path = find_optimal_path(map_data, map_size)