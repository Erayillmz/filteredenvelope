import pandas as pd                              # CSV okuma ve DataFrame işlemleri için
import numpy as np                               # Sayısal hesaplamalar ve dizi işlemleri için
import matplotlib.pyplot as plt                  # Grafik çizmek için
from scipy.signal import butter, filtfilt, hilbert  # Butterworth filtresi, faz kaymasız süzme ve Hilbert dönüşümü
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset
#  Bu kod, bir titreşim verisini okur, band-pass filtresi uygular ve zarf analizi yapar.
#  Band-pass filtresi oluşturacak fonksiyon
def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs                               # Nyquist frekansı = örnekleme frekansının yarısı
    low = lowcut / nyq                           # Alt kesimi normalize etme
    high = highcut / nyq                         # Üst kesimi normalize etme
    b, a = butter(order, [low, high], btype='band')  # Butterworth band-pass filtresi katsayıları
    return b, a                                  # (b, a) tuple’ını döndür

#  Bu filtreden yararlanarak sinyali ileri-geri süzecek fonksiyon
def apply_bandpass(data, lowcut, highcut, fs, order=4):
    b, a = butter_bandpass(lowcut, highcut, fs, order)  # (b,a) katsayılarını al
    return filtfilt(b, a, data)                     # filtfilt ile ileri-geri süz, faz kaymasını önle

#  Veriyi oku ve zaman eksenini oluştur
file_path = "./XYZ_IR(1002).csv"                 # Proje klasöründeki CSV dosyasının yolu
df = pd.read_csv(
    file_path,
    header=None,                                  # Başlık satırı yok
    names=["vibration_x","vibration_y","vibration_z"]  # Kolon adları
)
fs = 1000                                        # Örnekleme frekansı (Hz)
t = np.arange(len(df)) / fs                      # Örnek indekslerini saniyeye çevir → zaman vektörü

#  Band-pass parametreleri
lowcut, highcut = 20.0, 200.0                    # İlgi bandı: 20–200 Hz

#  Her eksene band-pass filtre uygula
x_bp = apply_bandpass(df["vibration_x"].values, lowcut, highcut, fs)  
y_bp = apply_bandpass(df["vibration_y"].values, lowcut, highcut, fs)  
z_bp = apply_bandpass(df["vibration_z"].values, lowcut, highcut, fs)  

#  Filtrelenmiş sinyalin zarfını (envelope) hesapla: |Hilbert( ... )|
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


    axins = inset_axes(ax,
                       width="30%", height="30%",  # inset boyutu
                       loc='upper right',           # konumu
                       borderpad=2)
    axins.plot(t, env, color='m', linewidth=0.8)  # aynı sinyali inset içinde çiz
    axins.set_xlim(4, 6)                           # zoom aralığı: 4–6 s
    mask = (t >= 4) & (t <= 6)
    axins.set_ylim(env[mask].min(), env[mask].max())  # dikey ölçek
    axins.set_xticks([]); axins.set_yticks([])       # temiz görünüm
    mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5")
axs[-1].set_xlabel("Zaman (s)")                   # Sadece alttaki grafiğe X-etiketi
plt.show()

#  Zarfın spektrumunu (FFT) çıkar ve çiz
from scipy.fft import fft, fftfreq

# FFT için pencere: tüm sinyal
N = len(env_x)                                   # Örnek sayısı
f = fftfreq(N, d=1/fs)[:N//2]                    # Pozitif frekans ekseni
X_env_fft = fft(env_x)                           # X ekseni zarf sinyalinin FFT’si
Y_env_fft = fft(env_y)                           # Y ekseni zarfı FFT
Z_env_fft = fft(env_z)                           # Z ekseni zarfı FFT
 # Inset eksenleri için etiketleri kapat (daha temiz görünsün)
  
# Grafik
plt.figure(figsize=(10,6))
plt.plot(f, np.abs(X_env_fft)[:N//2], label="X Envelope")
plt.plot(f, np.abs(Y_env_fft)[:N//2], label="Y Envelope", alpha=0.7)
plt.plot(f, np.abs(Z_env_fft)[:N//2], label="Z Envelope", alpha=0.7)
plt.xlabel("Frekans (Hz)"); plt.ylabel("Genlik")
plt.title("Envelope FFT - Spektrum")
plt.legend(); plt.grid(linestyle=':', linewidth=0.5)
plt.xlim(0, 500)                                  # 0–500 Hz arası görünür
plt.tight_layout(); plt.show()
