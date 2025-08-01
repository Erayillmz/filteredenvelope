# filteredenvelope
Bu kod, gerekli araçları importlayıp Butterworth band-pass filter ile 20-200 Hz arası filtreleyip her eksenn için x_bp , y_bp ve z_bp serilerini elde ediyoruz. Bu filtreleri uyguladıktan sonra sinyalın zarfını hesaplıyor kod. Hesaplanan sinyalin grafiğini oluşturup zaman serisi oluşturuluyor ve 4-6s arası büyüteç eklenir. Ve ardından bu sinyalin FFTsi çıkarılır.
## Veri Seti
Motor içi titreşim sensöründen alınmış verilerle hazırlandı kod. Github dosya kısmına eklendi.
## Kod Açıklaması
**1. İçe aktarımlar**\
Amaç: Gerekli kütüphaneleri içe aktarmak\
Kullanım:
```
import pandas as pd                              # CSV okuma ve DataFrame işlemleri için
import numpy as np                               # Sayısal hesaplamalar ve dizi işlemleri için
import matplotlib.pyplot as plt                  # Grafik çizmek için
from scipy.signal import butter, filtfilt, hilbert  # Butterworth filtresi, faz kaymasız süzme ve Hilbert dönüşümü
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset
```
**2. Filtre Uygulamak**\
Amaç: Elimizdeki titreşim sensörü verisine 20-200 Hz arası Butterwoth bandpass filtresi uygulamak\
Kullanım:
```
#  Bu filtreden yararlanarak sinyali ileri-geri süzecek fonksiyon
def apply_bandpass(data, lowcut, highcut, fs, order=4):
    b, a = butter_bandpass(lowcut, highcut, fs, order)  # katsayıları al
    return filtfilt(b, a, data)
#  Bandpass parametreleri
lowcut, highcut = 20.0, 200.0                    # İlgi bandı: 20–200 Hz

#  Her eksene bandpass filtre uygula
x_bp = apply_bandpass(df["vibration_x"].values, lowcut, highcut, fs)  
y_bp = apply_bandpass(df["vibration_y"].values, lowcut, highcut, fs)  
z_bp = apply_bandpass(df["vibration_z"].values, lowcut, highcut, fs)
```
**3. Zarf Eklemek**\
Amaç: Daha net bir görüntü elde etmek için envelope hesabı kullanılır\
Kullanım:
```
#  Filtrelenmiş sinyalin zarfını hesapla
env_x = np.abs(hilbert(x_bp))                    # X ekseni zarfı
env_y = np.abs(hilbert(y_bp))                    # Y ekseni zarfı
env_z = np.abs(hilbert(z_bp))                    # Z ekseni zarfı

#  Zarf sinyalini zaman-domeninde çiz
fig, axs = plt.subplots(3, 1, figsize=(10,8), sharex=True)
plt.tight_layout()
for ax, env, label in zip(axs, [env_x, env_y, env_z], ["X","Y","Z"]):
    ax.plot(t, env, linewidth=0.8, color='m')     # Zarfı çiz (mor renk)
    ax.set_ylabel("Envelope\nAmplitude")          # Y ekseni etiketi
    ax.set_title(f"{label} Aksı Zarf Analizi")    # Her panelin başlığı
```
**4. Çizdirdiğimiz grafiğe büyüeç ekleme**\
Amaç: 4-6s arası büyüteç ekleniyor\
Kullanım:
```
    axins = inset_axes(ax,
                       width="30%", height="30%",  # inset boyutu
                       loc='upper right',           # konumu
                       borderpad=2)
    axins.plot(t, env, color='m', linewidth=0.8)  # aynı sinyali inset içinde çiz
    axins.set_xlim(4, 6)                           # zoom aralığı: 4–6 s
```
**5. FFT çizdirmek**\
Amaç: FFT için eksenleri hazırlayıp grafiği çizdirip ve gösteriyoruz\
Kullanım:
```
#  Zarfın spektrumunu çıkarır ve çizdirir
from scipy.fft import fft, fftfreq

# FFT için pencere: tüm sinyal
N = len(env_x)                                   # Örnek sayısı
f = fftfreq(N, d=1/fs)[:N//2]                    # Pozitif frekans ekseni
X_env_fft = fft(env_x)                           # X ekseni zarf sinyalinin FFT si
Y_env_fft = fft(env_y)                           # Y ekseni zarfı FFT
Z_env_fft = fft(env_z)                           # Z ekseni zarfı FFT
# Grafik
plt.figure(figsize=(10,6))
plt.plot(f, np.abs(X_env_fft)[:N//2], label="X Envelope")
plt.plot(f, np.abs(Y_env_fft)[:N//2], label="Y Envelope", alpha=0.7)
plt.plot(f, np.abs(Z_env_fft)[:N//2], label="Z Envelope", alpha=0.7)
plt.xlabel("Frekans (Hz)"); plt.ylabel("Genlik")
plt.title("Envelope FFT - Spektrum")
plt.legend(); plt.grid(linestyle=':', linewidth=0.5)
plt.xlim(0, 200)                                  # 0–200 Hz arası görünür
plt.tight_layout(); plt.show()
```
## Çıktılar
**Zaman serisi grafiği:**
<img width="1919" height="947" alt="Ekran görüntüsü 2025-08-01 153126" src="https://github.com/user-attachments/assets/717c5a57-431c-45d2-b2d1-086b37f55195" />
**FFT Grafiği:**

<img width="1884" height="893" alt="Ekran görüntüsü 2025-08-01 153138" src="https://github.com/user-attachments/assets/f385ee61-8619-404a-b95a-b45556537be7" />

