import cv2
import mediapipe as mp
import math
import time
import pyautogui
import threading
import numpy as np


width,height=pyautogui.size()
print(width,height)
screen_w,screen_h=width-300,height-150


#FPS ölçmek için
calculateFPS=False
prev_time = time.time()



# MediaPipe el takip modülü
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)


# Kamera başlatma
cap = cv2.VideoCapture(0)


#Titremeyi önlemek için yapılan değişkenler
smoothingValue=4
newPos = {
            'Right': {i: [width/2,height/2] for i in range(21)}, 
            'Left': {i: [width/2,height/2] for i in range(21)}  
        }


#Tuşa basma algılama ayarları
sensivity = 2
emptyValue = 22 #el ileri veya geri gittiğinde aradki mesafe değişiyor bu değer 0 ve 17 noktalarının arasındaki mesafeye göre hassasiyeti oranlayacak




UpperKeysv2 = [
    ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
    ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],
    ['Caps', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', '\'', 'Enter'],
    ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'Shift'],
    ['Ctrl', 'Win', 'Alt', 'Space', 'Alt', 'Fn', 'Ctrl'],
    ['Esc']
]

LowerKeysv2 = [
    ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
    ['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
    ['Caps', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', 'Enter'],
    ['Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'Shift'],
    ['Ctrl', 'Win', 'Alt', 'Space', 'Alt', 'Fn', 'Ctrl'],
    ['Esc']
]

space_between_kayboards=['6','Y','y','H','h','N','n']


# Klavye ayarları
special_keys_width = {
    'Space': 180,  # Space tuşunun genişliği
    'Backspace': 120,  # Backspace tuşunun genişliği
    'Shift': 140,  # Shift tuşunun genişliği
    'Tab': 100  # Tab tuşunun genişliği
}
key_width = 60  # Standart tuş genişliği
key_height = 60  # Standart tuş yüksekliği
keyboard_x = 100
keyboard_y = 100 # Klavye başlangıç konumu
shift=False
space_between_keys=10
keyboardCirclePoints=[int((keyboard_x+((key_width+space_between_keys)*len(UpperKeysv2[0])+special_keys_width['Backspace']))),int((keyboard_y+((key_height+space_between_keys)*len(UpperKeysv2))))]
keyboardCirclesDistance=int(math.sqrt((keyboardCirclePoints[0] - keyboard_x) ** 2 + (keyboardCirclePoints[1] - keyboard_y) ** 2 ))
column=((key_width+space_between_keys)*len(UpperKeysv2[0])+special_keys_width['Backspace'])  #sütun 
maxrow=((key_height+space_between_keys)*len(UpperKeysv2))  #satır
keyboardCirclesDistancex=keyboardCirclePoints[0]-maxrow
keyboardCirclesDistancey=keyboardCirclePoints[1]-column
lastPressedKeys={}
pressSecond=0.5





# pressedkey fonksiyonu
def pressedkey(finger_name, key):
    def press_key_in_background():
        global shift
        #print(f"{finger_name} ile tusa basildi : {key}")
        


        pyautogui.press(key)
        shift = False if shift and key == 'Caps' else True
        print(shift)

    

# Eğer Shift tuşu basılmışsa


    # Thread başlatmak
    threading.Thread(target=press_key_in_background).start()
        

    


def calculate_distance(fingertip, finger_base):
    return math.sqrt((fingertip.x - finger_base.x) ** 2 + (fingertip.y - finger_base.y) ** 2 )*100

def calculateSensivity(distance):
    return (distance*sensivity)/emptyValue




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
    coordinates={}   #{'a':(0,0)}
    global keyboardCirclesDistance
    for row_index, row in enumerate(UpperKeysv2 if shift else LowerKeysv2):
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
    keyboard_x=int(topLeft[0])
    keyboard_y=int(topLeft[1])
    keyboardCirclePoints[0]=int((keyboard_x+((key_width+space_between_keys)*len(UpperKeysv2[0])+special_keys_width['Backspace']) ))
    keyboardCirclePoints[1]=int((keyboard_y+((key_height+space_between_keys)*len(UpperKeysv2))))



       

def reSizeKeyboard(bottomRight):
    global key_width,key_height,keyboardCirclePoints,column,maxrow,keyboardCirclesDistancex,keyboardCirclesDistancey
    
    #(keyboard_x+((key_width+space_between_keys)*len(UpperKeysv2[0])+special_keys_width['Backspace']),keyboard_y+((key_height+space_between_keys)*len(UpperKeysv2)))
    #orjinal boyut dairesinin konumunu hesaplama denklemi
    column=((key_width+space_between_keys)*len(UpperKeysv2[0])+special_keys_width['Backspace'])  #sütun 
    maxrow=((key_height+space_between_keys)*len(UpperKeysv2))  #satır

    distance_between_bottomrightx_keyboard_X=bottomRight[0]-maxrow
    distance_between_bottomrighty_keyboard_y=bottomRight[1]-column

    key_width = int((distance_between_bottomrightx_keyboard_X*40)/keyboardCirclesDistancex)
    
    key_height = int((distance_between_bottomrighty_keyboard_y*40)/keyboardCirclesDistancey)
    if key_height < 1 : key_height = 1
    if key_width < 1 : key_width = 1
    if distance_between_bottomrightx_keyboard_X < 1 : distance_between_bottomrightx_keyboard_X = 1
    if distance_between_bottomrighty_keyboard_y < 1 : distance_between_bottomrighty_keyboard_y = 1



    keyboardCirclePoints=bottomRight

    
    



#Yön tuşlarını çizen fonksiyon
def draw_buttons(frame,coordinates=(50,50)):
    cv2.rectangle(frame,(coordinates[0]+key_width,coordinates[1]),(coordinates[0]+key_width*2,coordinates[1]+key_height),(0,255,0),6) #(x1,y1),(x2,y2)
    cv2.rectangle(frame,(coordinates[0],coordinates[1]+key_height),(coordinates[0]+key_width,coordinates[1]+key_height*2),(0,255,0),6)
    cv2.rectangle(frame,(coordinates[0]+key_width,coordinates[1]+key_height),(coordinates[0]+key_width*2,coordinates[1]+key_height*2),(0,255,0),6)
    cv2.rectangle(frame,(coordinates[0]+key_width*2,coordinates[1]+key_height),(coordinates[0]+key_width*3,coordinates[1]+key_height*2),(0,255,0),6)
    pass
    


#Ekrana tıklayınca klavyeyi taşıyan kısım
def on_click(event, x, y, p1,p2):
    global trainName, record , trainData
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
def calculateFingers(*landmarks,handLabel,handScore):




    for i,a in enumerate(landmarks[0]):
        newPos[handLabel][i]=smoother.add_position((int(a.x*screen_w),int(a.y*screen_h)),i,handLabel)
        cv2.circle(frame,(int(newPos[handLabel][i][0]),int(newPos[handLabel][i][1])),12,(255,0,0) if handLabel == "Right" else (0,0,255),5)
            


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
    #draw_buttons(frame,(50,50)) #Ok tuşlarını çizen fonksiyon
    #put_text_centered(frame, str(record), (50 , 50), font_scale=1, color=(255, 255, 255), thickness=2)
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            
            #cv2.circle(frame,(50,50,50),12,(255,0,0),2)
            hand_label = handedness.classification[0].label  # "Right" veya "Left"
            hand_score = handedness.classification[0].score  # Güven skoru
            
            _coordinates=draw_keyboard(frame,keyboard_x,keyboard_y)
            calculateFingers(hand_landmarks.landmark,handLabel=hand_label,handScore=hand_score)
            

            cv2.circle(frame,(keyboard_x,keyboard_y),20,(255,255,255),2)
            
            cv2.circle(frame,(int(keyboardCirclePoints[0]),int(keyboardCirclePoints[1])),20,(255,255,0),2)
            

            

            if (calculate_distance(hand_landmarks.landmark[4],hand_landmarks.landmark[8])<10):
                
                if math.sqrt((newPos[hand_label][8][0]-keyboard_x)**2+(newPos[hand_label][8][1]-keyboard_y)**2) < 100 :
                    moveKeyboard((newPos[hand_label][8][0],newPos[hand_label][8][1]))
                    
                
                if math.sqrt((newPos["Right"][8][0]-keyboardCirclePoints[0])**2+(newPos["Right"][8][1]-keyboardCirclePoints[1])**2) < 75:
                    reSizeKeyboard([newPos["Right"][8][0],newPos["Right"][8][1]])
                    
                    
            
            for a in range(0,21,4):
                if (calculate_distance(hand_landmarks.landmark[a],hand_landmarks.landmark[a-1]) < calculateSensivity(calculate_distance(hand_landmarks.landmark[0],hand_landmarks.landmark[17]))):
                    for i in _coordinates:
                        if (hand_landmarks.landmark[a-2].x*screen_w > _coordinates[i][0] and hand_landmarks.landmark[a-2].x*screen_w < _coordinates[i][0]+key_width) and (hand_landmarks.landmark[a-2].y*screen_h > _coordinates[i][1] and hand_landmarks.landmark[a-2].y*screen_h < _coordinates[i][1]+key_height): 
                            if calculatePress(i):
                                pressedkey(hand_label,i)
                                #cv2.circle(frame,(_coordinates[i][0],_coordinates[i][1]),13,(0,255,255),-1)
                                cv2.rectangle(frame,_coordinates[i],(_coordinates[i][0]+key_width,_coordinates[i][1]+key_height),(0,255,255) if hand_label == "Right" else (255,255,0),-1)
                                print(lastPressedKeys)

                
        
        




    # Görüntüyü göster
    cv2.imshow("Virtual Keyboard", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
