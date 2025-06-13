import cv2
import mediapipe as mp
import math
import time
import pyautogui
import threading
import numpy as np
from keyboard import is_pressed
#Sunucu eklemeleri

width,height=pyautogui.size()
print(width,height)
screen_w,screen_h=width-300,height-150


runOnline = False
if runOnline:
    import socket
    import pickle
    data = b""
    onlinePos = {} #{addr:{Right:()}}
    server_ip = '192.168.1.103'  # Server IP'sini girin
    server_port = 9999

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))
    print("Connected")

    def onlineBackgroundPart():
        global frame
        frame=np.zeros((screen_w, screen_h, 3), dtype=np.uint8)
        
        
        while True:
            try:
                
                data = b""  # Her döngüde data'yı sıfırla
                while True:
                    packet = client.recv(4096)  # 4096 byte al
                    if not packet:  # Eğer veri gelmiyorsa, bağlantı kesilmiştir
                        print("Bağlantı kesildi.")
                        break
                    data += packet  # Alınan veriyi birleştir

                    # Eğer verinin tamamı gelmediyse, devam et
                    if len(packet) < 4096:
                        break
                    
                if data:
                    try:

                        positions = pickle.loads(data)  # Veriyi çöz
                        

                        
                        for addr, hands in positions.items():
                            for hand, points in hands.items():
                                for i, pos in points.items():
                                    x, y = int(pos[0] * screen_w), int(pos[1] * screen_h)
                                    #cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
                                    
                                    


                        # Görselleştirmeyi buradan yapıyoruz
                        
                        if cv2.waitKey(10) & 0xFF == ord('q'):  # 10ms bekleme
                            break
                        
                    except pickle.UnpicklingError as e:
                        print(f"UnpicklingError: {e}")
                    except EOFError as e:
                        print(f"EOFError: Veri eksik veya bozuk: {e}")
                    except Exception as e:
                        print(f"Beklenmeyen bir hata: {e}")
                else:
                    print("Veri alınamadı.")
                    break
            except Exception as e:
                print(f"Genel hata: {e}")
                break

        client.close()
        cv2.destroyAllWindows()
    threading.Thread(target=onlineBackgroundPart).start()




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


#Tuşa basma algılama ayarları
pressSensivity = 2.5
emptyValue = 22 #el ileri veya geri gittiğinde aradki mesafe değişiyor bu değer 0 ve 17 noktalarının arasındaki mesafeye göre hassasiyeti oranlayacak

UpperKeysv2 = [
    ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
    ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],
    ['CapsLock', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', '\'', 'Enter'],
    ['LShift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'Shift'],
    ['CtrlL', 'Fn','Win', 'Alt', 'Space', 'Alt Gr', 'CtrlR'],
    ['Esc']
]

LowerKeysv2 = [
    ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
    ['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
    ['CapsLock', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', 'Enter'],
    ['LShift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'Shift'],
    ['CtrlL', 'Fn','Win', 'Alt', 'Space', 'Alt Gr', 'CtrlR'],
    ['Esc']
]

#space_between_kayboards=['6','Y','y','H','h','N','n']


# Klavye ayarları
key_width = 60  # Standart tuş genişliği
key_height = 60  # Standart tuş yüksekliği
keyboard_x = 100
keyboard_y = 100 # Klavye başlangıç konumu
special_keys_width = {
    'Space': key_width*3,  # Space tuşunun genişliği
    'Backspace': key_width*2,  # Backspace tuşunun genişliği
    'Shift': key_width*2,
    'LShift':int(key_width*1.2),  # Shift tuşunun genişliği
    'Tab': int(key_width*1.5),
    'CapsLock':int(key_width*2)  # Tab tuşunun genişliği
}
caps=is_pressed('caps lock')
space_between_keys=10


defaultcolumn = space_between_keys*len(UpperKeysv2[0])
for i in range(len(UpperKeysv2[0])):
    defaultcolumn += key_width + 0 if UpperKeysv2[0][i] not in special_keys_width else special_keys_width[UpperKeysv2[0][i]]
    
    
defaultrow = space_between_keys*len(UpperKeysv2)
defaultrow += key_height*len(UpperKeysv2)

keyboardCirclePoints=[keyboard_x+defaultcolumn,keyboard_y+defaultrow]

lastPressedKeys={}
pressSecond=0.25
is_fist=False


# Global değişkenler
stickyButtons = {'Shift': False, 'LShift': False, 'CtrlL': False, 'CtrlR': False, 'Alt': False, 'Alt Gr': False, 'Fn': False}
key_mapping = {
    'Shift': 'shift',
    'LShift': 'shiftleft',
    'CtrlL': 'ctrlleft',
    'CtrlR': 'ctrlright',
    'Alt': 'altleft',
    'Alt Gr': 'altright',
    'Fn': 'fn'
}
print(pyautogui.KEY_NAMES)
active_keys=[]
def pressedkey(finger_name, key):
    def press_key_in_background():
        global  caps,stickyButtons, active_keys

        # CapsLock kontrolü
        if key == 'CapsLock':
            caps = False if caps else True
            
            
        # Tuşu bastıktan sonra yapılacak işlemler
        #print(f"{finger_name} ile tuşa basıldı: {key}")
        

        # Sticky tuşlar aktifse, hotkey kullan
        active_keys = [k for k, v in stickyButtons.items() if v]  # True olan tuşları al
        pyKeys = {key_mapping[k]: True for k in active_keys if k in key_mapping}

        
        if active_keys:
            pyautogui.hotkey(*pyKeys, key)  # * ile unpack ederek hotkey'e gönder
            print("pressed:",pyKeys,key)
        else:
            # Sticky olmayan tuşlar için normal basma
            
            pyautogui.press(key)

        # Sticky tuş durumunu güncelle
        if key in stickyButtons:
            stickyButtons[key] = True
        elif key not in stickyButtons:
            # Eğer key stickyButtons içinde değilse, tüm tuşları False yap
            stickyButtons = {k: False for k in stickyButtons}
        

    # Arka planda tuşa basma işlemi

    # Thread başlatmak
    threading.Thread(target=press_key_in_background).start()
        

    


def calculate_distance(fingertip, finger_base):
    return math.sqrt((fingertip.x - finger_base.x) ** 2 + (fingertip.y - finger_base.y) ** 2 )*100
def calculateDistance(posOne,posTwo):
    return math.sqrt((posOne[0] - posTwo[0]) ** 2 + (posOne[1] - posTwo[1]) ** 2 )


def calculateSensivity(distance,sens=pressSensivity): #el uzaklaştıkça aradaki mesafeler kısaldığından dolayı belli bir değerde oranlaman gerekiyor. 0 ve 17 nolu boğumlar arası uzaklığa göre yani elin hemen hemen z eksenine göre hassaslığı yeniden hesaplıyor.
    #distance = 0 ve 17 numaralı boğumlar arası o anki uzaklık
    #emptyValue = el hemen hemen 40 50 cm uzaktayken (varsayılan kullanım) 0 ve 17 boğum arası uzaklık
    #sens = oranlamak istediğin hassasiyet değeri
    return (distance*sens)/emptyValue




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



# Klavye tuşlarını çizme fonksiyonu
def draw_keyboard(image, top_left_x, top_left_y):
    global caps
    coordinates={}   #{'a':(0,0)}
    for row_index, row in enumerate(UpperKeysv2 if caps else LowerKeysv2):
        
        current_x = top_left_x  # Her satır için x koordinatını sıfırlayın
        for col_index, key in enumerate(row):
            # Özel tuşlar için genişlik kullan, diğer tuşlar için normal genişlik
            width = special_keys_width.get(key, key_width)

            # Tuşun koordinatlarını hesapla
            x = current_x
            y = top_left_y + row_index * (key_height + space_between_keys)

            # Tuşu çiz
            cv2.rectangle(image, (x, y), (x + width, y + key_height), (255, 255, 255), 2)
            # Tuşun ismini yaz
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(image, key, (x + space_between_keys, y + 35), font, 0.7, (255, 255, 255), 2)
            

            # X koordinatını sonraki tuş için güncelle
            current_x = x + width + space_between_keys
            coordinates[key]=(x,y)

            if key in stickyButtons:
                if stickyButtons[key]:
                    cv2.rectangle(image,(x,y),(x+width,y+key_height),(0,255,190),12)

    return coordinates


def calculatePress(key):
    if key in lastPressedKeys:
        if time.time()- lastPressedKeys[key] <pressSecond:
            return False
        else:
            lastPressedKeys[key]=time.time()
            return True
    else:
        lastPressedKeys[key]=time.time()
        return True



def moveKeyboard(topLeft):
    global keyboard_x,keyboard_y,keyboardCirclePoints
    newTopLeft=[]
    newTopLeft.append(topLeft[0]-(key_width*7+space_between_keys*6))
    newTopLeft.append(topLeft[1]-(key_height*3+space_between_keys*2))
    keyboard_x=int(newTopLeft[0])
    keyboard_y=int(newTopLeft[1])

    column = space_between_keys*len(UpperKeysv2[0])
    for i in range(len(UpperKeysv2[0])):
        column += key_width + 0 if UpperKeysv2[0][i] not in special_keys_width else special_keys_width[UpperKeysv2[0][i]]
        
        
    row = space_between_keys*len(UpperKeysv2)
    row += key_height*len(UpperKeysv2)
    
    keyboardCirclePoints[0]=int(keyboard_x+column)
    keyboardCirclePoints[1]=int(keyboard_y+row)



       

def reSizeKeyboard(frame,bottomRight):
    global key_width,key_height,keyboardCirclePoints,defaultcolumn,defaultrow
    
    cv2.line(frame,(int(keyboard_x),int(keyboard_y)),(int(bottomRight[0]),int(bottomRight[1])),(255,100,100),2)

    keyboardCirclePoints[0] = bottomRight[0]
    keyboardCirclePoints[1] = bottomRight[1]

    column = space_between_keys*len(UpperKeysv2[0])
    for i in range(len(UpperKeysv2[0])):
        column += key_width + 0 if UpperKeysv2[0][i] not in special_keys_width else special_keys_width[UpperKeysv2[0][i]]
        
        
    row = space_between_keys*len(UpperKeysv2)
    row += key_height*len(UpperKeysv2)

    key_width=int((keyboardCirclePoints[0]-keyboard_x)*60/defaultcolumn)
    key_height=int((keyboardCirclePoints[1]-keyboard_y)*60/defaultrow)
    #print(key_width,key_height)

    #keyboardCirclePoints[0] = keyboard_x + column
    #keyboardCirclePoints[1] = keyboard_y + row



    
    




    


#Ekrana tıklayınca klavyeyi taşıyan kısım
def on_click(event, x, y, p1,p2):
    global keyboard_y,keyboard_x
    if event == cv2.EVENT_LBUTTONDOWN:
        #cv2.circle(frame, (x, y), 3, (255, 0, 0), -1)
        moveKeyboard((x,y))
        
            
            
cv2.namedWindow("Virtual Keyboard") 
cv2.setMouseCallback("Virtual Keyboard", on_click)



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
        if i %4 == 0 and i != 0:
            cv2.circle(frame,(int(newPos[handLabel][i-2][0]),int(newPos[handLabel][i-2][1])),12,(255,0,0) if handLabel == "Right" else (0,0,255),5)
        

    #cv2.circle(frame,(int(newPos[handLabel][a-2][0]),int(newPos[handLabel][a-2][1])),12,(255,0,0) if handLabel == "Right" else (0,0,255),5)


def checkFist(hand_landmarks):
    global is_fist
    finger_tips = [
                    mp_hands.HandLandmark.THUMB_TIP,
                    mp_hands.HandLandmark.INDEX_FINGER_TIP,
                    mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                    mp_hands.HandLandmark.RING_FINGER_TIP,
                    mp_hands.HandLandmark.PINKY_TIP,
                ]
    # Yumruk kontrolü
    is_fist = True
    for tip in finger_tips:
        fingertip = hand_landmarks.landmark[tip]
        # Mesafeyi hesapla
        distance = calculate_distance(hand_landmarks.landmark[0], fingertip)
        # Mesafe eşiği
        if distance > calculateSensivity(calculate_distance(hand_landmarks.landmark[0],hand_landmarks.landmark[17]),sens=31):  # Bu değeri ihtiyaca göre ayarlayın
            is_fist = False
            break
    return is_fist



while cap.isOpened():

    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    frame=cv2.resize(frame,(screen_w,screen_h))
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # El işleme
    results = hands.process(rgb_frame)




    if calculateFPS:
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        ortalama_ekle(int(fps))
    
    #draw_keyboard(frame, (keyboard_x,keyboard_y), (keyboard_x+200,keyboard_y+200)) #Klavyeyi çizen fonksiyon
    #put_text_centered(frame, str(record), (50 , 50), font_scale=1, color=(255, 255, 255), thickness=2)
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            
            #cv2.circle(frame,(50,50,50),12,(255,0,0),2)
            hand_label = handedness.classification[0].label  # "Right" veya "Left"
            hand_score = handedness.classification[0].score  # Güven skoru
            
            _coordinates=draw_keyboard(frame,keyboard_x,keyboard_y)
            calculateFingers(hand_landmarks.landmark,frame=frame,handLabel=hand_label,handScore=hand_score)
            

            cv2.circle(frame,(keyboard_x,keyboard_y),20,(255,255,255),2)
            
            cv2.circle(frame,(int(keyboardCirclePoints[0]),int(keyboardCirclePoints[1])),20,(255,255,0),2)
            

            
            
            if checkFist(hand_landmarks) :
                moveKeyboard((newPos[hand_label][0][0],newPos[hand_label][0][1]))

            if (calculateDistance(newPos['Right'][4],newPos['Right'][8])<calculateSensivity(calculateDistance(newPos['Right'][0],newPos['Right'][17]),sens=7)):
                #print(calculateDistance(newPos['Right'][8],[keyboardCirclePoints[0],keyboardCirclePoints[1]]),calculateSensivity(calculateDistance(newPos['Right'][0],newPos['Right'][17]),sens=7))
            
                if calculateDistance(newPos['Right'][8],[keyboardCirclePoints[0],keyboardCirclePoints[1]]) < calculateSensivity(calculateDistance(newPos['Right'][0],newPos['Right'][17]),sens=7):
                    reSizeKeyboard(frame,[newPos["Right"][8][0],newPos["Right"][8][1]])
            

                    
                    
            
            for a in range(0,21,4):
                if (calculate_distance(hand_landmarks.landmark[a],hand_landmarks.landmark[a-1]) < calculateSensivity(calculate_distance(hand_landmarks.landmark[0],hand_landmarks.landmark[17]),sens=pressSensivity)):
                    for i in _coordinates:
                        if (hand_landmarks.landmark[a-2].x*screen_w > _coordinates[i][0] and hand_landmarks.landmark[a-2].x*screen_w < _coordinates[i][0] + special_keys_width.get(i,key_width)) and (hand_landmarks.landmark[a-2].y*screen_h > _coordinates[i][1] and hand_landmarks.landmark[a-2].y*screen_h < _coordinates[i][1]+key_height): 
                            if calculatePress(i) and is_fist == False:
                                pressedkey(hand_label,i)
                                #cv2.circle(frame,(_coordinates[i][0],_coordinates[i][1]),13,(0,255,255),-1)

                                cv2.rectangle(frame,_coordinates[i],(_coordinates[i][0] + special_keys_width.get(i,key_width),_coordinates[i][1]+key_height),(0,255,255) if hand_label == "Right" else (255,255,0),-1)
                                
                                
                                #print(lastPressedKeys)

                
        
        




    # Görüntüyü göster
    cv2.imshow("Virtual Keyboard", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
