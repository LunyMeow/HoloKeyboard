import socket
import pickle
import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
cap = cv2.VideoCapture(0)

server_ip = '192.168.1.107'  # Server IP'sini girin
server_port = 9999

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((server_ip, server_port))

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame,1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(frame_rgb)

    hand_positions = {'Right': {}, 'Left': {}}
    if result.multi_hand_landmarks:
        for hand_landmarks,handedness in zip(result.multi_hand_landmarks,result.multi_handedness):
            for i, lm in enumerate(hand_landmarks.landmark):
                hand_positions[handedness.classification[0].label][i] = [lm.x, lm.y]  # Basitçe X ve Y pozisyonu

    try:
        client.sendall(pickle.dumps(hand_positions))
    except:
        break

cap.release()
client.close()
