import cv2
import numpy as np

# Satranç tahtası boyutu (iç kare sayısı)
chessboard_size = (9, 6)

# Her bir karenin fiziksel boyutu (örneğin, 25 mm)
square_size = 25  # mm

# Dünya koordinatları (satranç tahtasının gerçek konumu)
obj_points = []
objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
objp *= square_size  # Kare boyutuyla çarp

# Görüntü ve dünya koordinatları eşleşmeleri
obj_points_list = []  # 3D noktalar
img_points_list = []  # 2D görüntü noktaları

# Kamerayla görüntü al ve köşeleri tespit et
cap = cv2.VideoCapture(0)
while len(obj_points_list) < 15:  # 15 görüntü toplayana kadar devam et
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)
    
    if ret:
        obj_points_list.append(objp)
        img_points_list.append(corners)

        # Köşeleri görselleştir
        cv2.drawChessboardCorners(frame, chessboard_size, corners, ret)
    
    cv2.imshow('Kalibrasyon', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Kamera kalibrasyonu
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_points_list, img_points_list, gray.shape[::-1], None, None)

# Kamera matrisini yazdır
print("Kamera Matris (mtx):\n", mtx)
print("Distorsiyon Katsayıları (dist):\n", dist)

# Odak uzaklığı (f_x ve f_y) ve optik merkez (c_x, c_y)
f_x = mtx[0, 0]
f_y = mtx[1, 1]
c_x = mtx[0, 2]
c_y = mtx[1, 2]
print("Odak Uzaklığı: f_x = {:.2f}, f_y = {:.2f}".format(f_x, f_y))
print("Optik Merkez: c_x = {:.2f}, c_y = {:.2f}".format(c_x, c_y))

# Görüntü boyutlarını alın
image_width = gray.shape[1]  # Görüntü genişliği (piksel)
image_height = gray.shape[0]  # Görüntü yüksekliği (piksel)

# Sensör boyutlarını tahmini olarak belirleyin (mm cinsinden, laptop kameraları için)
sensor_width_mm = 4.8  # Sensör genişliği (örneğin: 4.8 mm)
sensor_height_mm = 3.6  # Sensör yüksekliği (örneğin: 3.6 mm)

# Yatay ve dikey görüş açısını hesaplayın
theta_x = 2 * np.arctan((sensor_width_mm / 2) / f_x) * (180 / np.pi)  # Dereceye çevir
theta_y = 2 * np.arctan((sensor_height_mm / 2) / f_y) * (180 / np.pi)  # Dereceye çevir

print("Yatay Görüş Açısı (theta_x): {:.2f} derece".format(theta_x))
print("Dikey Görüş Açısı (theta_y): {:.2f} derece".format(theta_y))
