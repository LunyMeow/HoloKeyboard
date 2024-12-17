import cv2
import numpy as np
import math

# Resmi yükleyin
image = cv2.imread('image.jpg')  # Resim dosyasının yolunu belirtin
h, w, _ = image.shape

# Çemberin merkezi (resmin merkezi)
center_x, center_y = w // 2, h // 2
radius = 300  # Çemberin yarıçapı
theta = 45  # Çember üzerindeki açı (derece cinsinden)

# Radyan cinsine çevir
theta_rad = math.radians(theta)

# Çember üzerindeki kişinin pozisyonu
person_x = center_x + radius * math.cos(theta_rad)
person_y = center_y + radius * math.sin(theta_rad)

# Kamera parametreleri
focal_length = 800  # Odak uzaklığı
d = 1000  # Kişi ile merkezin arasındaki mesafe (metre cinsinden)

# Ölçek faktörü: Mesafeye göre köşe noktalarını küçültmek/büyütmek için
scale_factor = 1 / (d / 1000)  # Mesafe arttıkça küçülür, azalırsa büyür

# Perspektif dönüşüm için köşe noktaları
src_points = np.float32([
    [0, 0],          # Sol üst köşe
    [w - 1, 0],      # Sağ üst köşe
    [0, h - 1],      # Sol alt köşe
    [w - 1, h - 1],  # Sağ alt köşe
])

# Çember üzerindeki bakan kişiye göre yeni köşe noktaları
# Ölçek faktörünü kullanarak her bir köşe noktasını ölçeklendiriyoruz
dst_points = np.float32([
    [center_x + (person_x - center_x) * scale_factor, center_y + (person_y - center_y) * scale_factor],  # Sol üst
    [center_x + (person_x - center_x + w) * scale_factor, center_y + (person_y - center_y) * scale_factor],  # Sağ üst
    [center_x + (person_x - center_x) * scale_factor, center_y + (person_y - center_y + h) * scale_factor],  # Sol alt
    [center_x + (person_x - center_x + w) * scale_factor, center_y + (person_y - center_y + h) * scale_factor],  # Sağ alt
])

# Perspektif dönüşüm matrisi
matrix = cv2.getPerspectiveTransform(src_points, dst_points)

# Resmi dönüştür
transformed_image = cv2.warpPerspective(image, matrix, (w, h))

# Sonuçları göster
cv2.imshow('Original Image', image)
cv2.imshow('Transformed Image', transformed_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
