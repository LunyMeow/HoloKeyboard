import socket
import pickle
import cv2
import numpy as np

server_ip = '192.168.1.107'  # Server IP'sini girin
server_port = 9999

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((server_ip, server_port))
print("Connected")
width, height = 640, 480

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
                
                
                canvas = np.zeros((height, width, 3), dtype=np.uint8)
                for addr, hands in positions.items():
                    for hand, points in hands.items():
                        for i, pos in points.items():
                            x, y = int(pos[0] * width), int(pos[1] * height)
                            cv2.circle(canvas, (x, y), 5, (0, 255, 0), -1)

                # Görselleştirmeyi buradan yapıyoruz
                cv2.imshow("El Noktaları", canvas)
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