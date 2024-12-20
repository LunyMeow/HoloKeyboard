import os
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
    try:
        while True:
            data = client_socket.recv(4096)
            if not data:
                print(f"Bağlantı kesildi: {address}")
                break  # Döngüyü kır, bağlantı kesildi
            hand_data = pickle.loads(data)
            positions[address] = hand_data
            print(f"Handled: {hand_data}")
    except Exception as e:
        print(f"Hata: {e} - Bağlantı: {address}")
    finally:
        # Bağlantı kesildiğinde temizleme işlemleri
        positions.pop(address, None)  # `positions` listesinden kaldır
        if client_socket in clients:
            clients.remove(client_socket)  # `clients` listesinden kaldır
        client_socket.close()  # Soketi kapat
        print(f"Bağlantı kapatıldı: {address}")


def broadcast():
    global last_sent_positions
    while True:
        if positions:  # Eğer pozisyonlar varsa
            current_positions = pickle.dumps(positions)
            if current_positions != last_sent_positions:
                to_remove = []  # Kaldırılacak soketler listesi
                for client_socket in clients:
                    try:
                        client_socket.sendall(current_positions)
                        print(f"Sending: {positions}")
                    except Exception as e:
                        print(f"Send hatası: {e} - Soket: {client_socket}")
                        to_remove.append(client_socket)  # Hatalı soketi ekle
                for client_socket in to_remove:
                    clients.remove(client_socket)  # Hatalı soketi kaldır
                last_sent_positions = current_positions  # Gönderilen pozisyonları güncelle
        time.sleep(0.1)  # CPU kullanımı için bekleme


def wait_for_exit():
    while True:
        if keyboard.is_pressed('q'):  # 'q' tuşuna basıldığında
            print("Çıkış yapılıyor...")
            for client_socket in clients:
                client_socket.close()  # Tüm soketleri kapat
            server.close()  # Server'ı kapat
            os._exit(0)  # Programı tamamen sonlandır


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 9999))
server.listen(5)
print("Server başlatıldı...")

# Çıkış tuşunu dinleyecek thread'i başlat
threading.Thread(target=wait_for_exit, daemon=True).start()

# Broadcast işlemi için thread başlat
threading.Thread(target=broadcast, daemon=True).start()

while True:
    try:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()
    except OSError as e:
        print(f"Server durduruldu: {e}")
        break  # Döngüyü durdur
    except Exception as e:
        print(f"Hata: {e}")
