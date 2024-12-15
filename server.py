import socket
import threading
import pickle
import keyboard  # Tuş dinleyicisi
import time

clients = []
positions = {}
last_sent_positions = None  # En son gönderilen pozisyonları saklamak için

def handle_client(client_socket, address):
    global positions
    print(f"Bağlandı: {address}")
    while True:
        try:
            data = client_socket.recv(4096)
            if not data:
                break
            hand_data = pickle.loads(data)
            positions[address] = hand_data
            print(f"Handled: {hand_data}")
            
        except:
            break
    print(f"Bağlantı kesildi: {address}")
    positions[address] = {}
    clients.remove(client_socket)
    client_socket.close()

def broadcast():
    global last_sent_positions
    while True:
        if positions:  # Eğer pozisyonlar varsa
            # Yeni pozisyonları oluştur
            current_positions = pickle.dumps(positions)
            # Eğer önceki gönderilen pozisyonlarla aynı değilse gönder
            if current_positions != last_sent_positions:
                for client_socket in clients:
                    try:
                        client_socket.sendall(current_positions)
                        print(f"Sending: {positions}")
                    except:
                        try:
                            clients.remove(client_socket)
                            positions[addr] = {}
                        except ValueError:
                            pass  # Soket zaten listede değilse hatayı yok say
                last_sent_positions = current_positions  # Gönderilen pozisyonları güncelle
        #time.sleep(0.1)  # Biraz bekle, böylece CPU'yu aşırı kullanmaz

def wait_for_exit():
    while True:
        if keyboard.is_pressed('q'):  # 'q' tuşuna basıldığında
            print("Çıkış yapılıyor...")
            server.close()  # Server'ı kapat
            exit()
            break

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 9999))
server.listen(5)
print("Server başlatıldı...")

# Çıkış tuşunu dinleyecek thread'i başlat
threading.Thread(target=wait_for_exit, daemon=True).start()

# Broadcast işlemi için thread başlat
threading.Thread(target=broadcast, daemon=True).start()

# Client bağlantılarını bekle
while True:
    client_socket, addr = server.accept()
    clients.append(client_socket)
    threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()