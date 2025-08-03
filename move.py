import modi_plus
import time

bundle = modi_plus.MODIPlus()
motor1 = bundle.motors[0] #왼쪽 뒤
motor2 = bundle.motors[1] #오른쪽 앞
motor3 = bundle.motors[2] #왼쪽 앞
motor4 = bundle.motors[3] #오른쪽 뒤
imu = bundle.imus[0]
dis = bundle.displays[0]
speaker1 = bundle.speakers[0]
speaker2 = bundle.speakers[1]


def angleunji(): # 각도 정상화(0~359도), 180도랑 360도 없음
    angle = imu.angle_z
    if angle < 0:
        angle += 360
        if angle == 181:
            angle = 180
    else:
        if angle == 179:
            angle = 180
    dis.text = f"{angle}"
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
            angle_diff = abs(angle_diff-360)  # 반대방향으로 회전하도록 변경
        
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
            motor_speed = 25  # 각도 차이가 작으면 느리게 회전
        else:
            motor_speed = 14  # 각도 차이가 매우 작으면 더 천천히 회전

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
            angle_diff = abs(angle_diff-360)  # 반대방향으로 회전하도록 변경
        
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
            motor_speed = 25  # 각도 차이가 작으면 느리게 회전
        else:
            motor_speed = 14  # 각도 차이가 매우 작으면 더 천천히 회전

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

def bbi_bbo():
    speaker1.set_tune(500, 100)
    speaker2.set_tune(500, 100)
    time.sleep(0.7)
    speaker1.set_tune(750, 100)
    speaker2.set_tune(750, 100)
    time.sleep(0.7)

right_turn(90)
right_turn(270)