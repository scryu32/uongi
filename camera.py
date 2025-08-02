import cv2
from datetime import datetime
import time
from main import predict_image
import tensorflow as tf

class Camera:
    def __init__(self, camera_index=1):
        self.cap = cv2.VideoCapture(1)
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

best_model = tf.keras.models.load_model('./best_model.h5')
# 사용 예
print("모드로델끝")
camera = Camera()
while True:
    a = input()
    pic_path = camera.capture_photo()
    print(pic_path)
    result = predict_image(best_model, pic_path)