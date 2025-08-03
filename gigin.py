import modi_plus
import time

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

def earth_quake():
    pass

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




if __name__ == "__main__":
    print("메인 루프 실행")
    while True:
        gamji_earth_quake(0, False)