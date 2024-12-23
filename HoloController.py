import cv2
import mediapipe as mp
import math
import time
import pyautogui
import threading
import json
import numpy as np
from keyboard import is_pressed
#Sunucu eklemeleri

width,height=pyautogui.size()
print(width,height)
screen_w,screen_h=700,700

#FPS ölçmek için
calculateFPS=False
prev_time = time.time()


# MediaPipe el takip modülü
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)


# Kamera başlatma
cap = cv2.VideoCapture(0)


#Titremeyi önlemek için yapılan değişkenler
#newPos = {'Right':{0:(200,200)}}
smoothingValue=4
newPos = {
            'Right': {i: [width/2,height/2] for i in range(21)}, 
            'Left': {i: [width/2,height/2] for i in range(21)}  
        }


def calculateDistance(posOne,posTwo):
    return math.sqrt((posOne[0] - posTwo[0]) ** 2 + (posOne[1] - posTwo[1]) ** 2 )


toplam=0
sayi_adedi=0
def ortalama_ekle(yeni_deger):
        global toplam, sayi_adedi
        toplam += yeni_deger
        sayi_adedi += 1
        #print(toplam / sayi_adedi)


def put_text_centered(image, text, position, font=cv2.FONT_HERSHEY_COMPLEX, font_scale=1, color=(255, 255, 255), thickness=2):
    # Metnin boyutunu hesapla
    (text_width, text_height), baseline = cv2.getTextSize(str(text), font, font_scale, thickness)
    # Hedef koordinatları
    x, y = position
    # Metnin sol alt köşesinin koordinatlarını hesapla
    text_x = x - (text_width // 2)
    text_y = y + (text_height // 2)
    # Metni yazdır
    cv2.putText(image, str(text), (text_x, text_y), font, font_scale, color, thickness)


#Ekrana tıklayınca klavyeyi taşıyan kısım
def on_click(event, x, y, p1,p2):
    if event == cv2.EVENT_LBUTTONDOWN:
        #cv2.circle(frame, (x, y), 3, (255, 0, 0), -1)
        print(x,y)

cv2.namedWindow("Holo Controller")
cv2.setMouseCallback("Holo Controller", on_click)


#elin titremesini önleme
class SmoothHandMovement:
    def __init__(self, window_size=5):
        self.window_size = window_size
        # Her el ve parmak için ayrı pozisyon listeleri
        self.positions = {
            'Right': {i: [] for i in range(21)}, 
            'Left': {i: [] for i in range(21)}  
        }

    def add_position(self, new_position, finger, hand):
        """Yeni pozisyonu ekle ve yumuşatılmış pozisyonu döndür."""
        if hand not in self.positions:
            raise ValueError("Geçersiz el türü. El türü 'left' veya 'right' olmalıdır.")
        if finger not in self.positions[hand]:
            raise ValueError("Geçersiz parmak türü. Parmak türü 0-4 arasında olmalıdır.")
        
        # Yeni pozisyonu ilgili el ve parmak listesine ekle
        self.positions[hand][finger].append(new_position)
        
        # Eğer pozisyon sayısı pencere boyutundan fazlaysa, en eski pozisyonu çıkar
        if len(self.positions[hand][finger]) > self.window_size:
            self.positions[hand][finger].pop(0)
        
        # Yumuşatılmış pozisyonu hesapla
        smoothed_position = np.mean(self.positions[hand][finger], axis=0)
        return smoothed_position


# Kullanım
smoother = SmoothHandMovement(window_size=smoothingValue)

#Elin noktalarını gelecekte yapacağım geliştirme ile sunuculardan gelen bilgilere göre çizme işlemi
def calculateFingers(*landmarks,frame,handLabel,handScore):
    
    for i,a in enumerate(landmarks[0]):
        newPos[handLabel][i]=smoother.add_position((int(a.x*screen_w),int(a.y*screen_h)),i,handLabel)
        cv2.circle(frame,(int(newPos[handLabel][i][0]),int(newPos[handLabel][i][1])),12,(255,0,0) if handLabel == "Right" else (0,0,255),5)




# JSON dosyasını oku
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Çerçeve çizme fonksiyonu
def draw_frame(image, frame_data):
# Eğer frameColor zaten bir tuple ise doğrudan kullan
    if isinstance(frame_data["frameColor"], tuple):
        color = frame_data["frameColor"]
    else:
        # Eğer string ise tuple'a dönüştür
        color_str = frame_data["frameColor"]
        color = tuple(map(int, color_str.strip("()").split(",")))



    top_left_x = int(frame_data["topLeft"]["x"] * image.shape[1])
    top_left_y = int(frame_data["topLeft"]["y"] * image.shape[0])
    down_right_x = int(frame_data["downRight"]["x"] * image.shape[1])
    down_right_y = int(frame_data["downRight"]["y"] * image.shape[0])

    # Dikdörtgeni çiz
    cv2.rectangle(image, (top_left_x, top_left_y), (down_right_x, down_right_y), color, 2)

json_data = load_json('design.json')  # JSON dosyasının yolu


while cap.isOpened():

    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    frame=cv2.resize(frame,(screen_w,screen_h))
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # El işleme
    results = hands.process(rgb_frame)

    # JSON verisindeki her çerçeveyi çiz
    for frame_name in json_data:
        draw_frame(frame, json_data[frame_name])


    if calculateFPS:
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        ortalama_ekle(int(fps))

    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            
            #cv2.circle(frame,(50,50,50),12,(255,0,0),2)
            hand_label = handedness.classification[0].label  # "Right" veya "Left"
            hand_score = handedness.classification[0].score  # Güven skoru
            
            calculateFingers(hand_landmarks.landmark,frame=frame,handLabel=hand_label,handScore=hand_score)


    # Görüntüyü göster
    cv2.imshow("Holo Controller", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()