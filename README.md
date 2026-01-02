# 🚀 QoS Tabanlı Çok Amaçlı Ağ Rotalama Probleminin Sezgisel Algoritmalar ile Çözülmesi

Bu proje, **250 düğümlü bir ağ topolojisinde**, **QoS (Quality of Service)** kriterleri dikkate alınarak kaynak ve hedef düğüm arasındaki en uygun rotanın bulunmasını amaçlamaktadır.  
Farklı yapay zekâ ve sezgisel optimizasyon algoritmaları kullanılarak sonuçlar karşılaştırılmıştır.

---

## 📌 İçerik
- [📖 Proje Hakkında](#proje-hakkinda)
- [🧠 Kullanılan Yöntemler](#kullanilan-yontemler)
- [🛠️ Kullanılan Teknolojiler](#kullanilan-teknolojiler)
- [🧩 Sistem Mimarisi](#sistem-mimarisi)
- [⚙️ Kurulum](#kurulum)
- [▶️ Kullanım](#kullanim)
- [👥 Proje Ekibi](#-proje-ekibi)
---

## <a name="proje-hakkinda"></a>📖 Proje Hakkında
Projede ağ yönlendirme problemi, **çok amaçlı optimizasyon** yaklaşımıyla ele alınmıştır.  
Gecikme, bant genişliği, güvenilirlik ve maliyet gibi QoS metrikleri dikkate alınarak en uygun rota hesaplanmaktadır.  
Kullanıcı, grafiksel arayüz üzerinden algoritma ve parametre seçimlerini yapabilmektedir.

---

## <a name="kullanilan-yontemler"></a>🧠 Kullanılan Yöntemler
Bu projede aşağıdaki algoritmalar kullanılmıştır:
- 🔹 **Q-Learning**
- 🐜 **Karınca Kolonisi Optimizasyonu (ACO)**
- 🧬 **Genetik Algoritma (GA)**

---

## <a name="kullanilan-teknolojiler"></a>🛠️ Kullanılan Teknolojiler
- 🐍 **Python**
- 🌐 **NetworkX**
- 📊 **Matplotlib**
- 🖥️ **Tkinter**
- 📁 **CSV veri dosyaları**

---

## <a name="sistem-mimarisi"></a>🧩 Sistem Mimarisi
Proje üç ana katmandan oluşmaktadır:
- ⚙️ **Algoritma Katmanı:** Q-Learning, ACO, Genetik Algoritma  
- 🌐 **Ağ & Veri Katmanı:** NetworkX ile oluşturulan ağ topolojisi ve QoS metrikleri  
- 🖥️ **Arayüz Katmanı:** Tkinter tabanlı grafiksel kullanıcı arayüzü  

---

## <a name="kurulum"></a>⚙️ Kurulum
```python
git clone https://github.com/eminabaz/QoS-Cok-Amacli-Rotalama
cd /QoS-Cok-Amacli-Rotalama
pip install -r requirements.txt
```

## <a name="kullanim"></a>▶️ Kullanım
```python
python main.py
```

🎯 Kaynak ve hedef düğüm belirlenir

🧠 Algoritma seçimi yapılır

📶 İstenen bant genişliği (Demand – Mbps) değeri yazılır.

📊 QoS parametreleri girilir

📈 Sonuçlar grafiksel olarak görüntülenir


## <a name="proje-ekibi"></a>👥 Proje Ekibi

- [Emin Abaz](https://github.com/eminabaz)
- [Tuğçenur Araz](https://github.com/tugcearaz)
- [Ela Sudem Gökdemir](https://github.com/ElaSudemGokdemir)
- [Doğa Doğanay](https://github.com/dogadoganay)
- [Menekşe Sena Melek](https://github.com/Sena1881)
- [Mohammed Qatran](https://github.com/GF65-9)
- [Mohammed Aboubaker](https://github.com/mohamedaaboubakeraboubaker-maker)
- [Yiğit Sağ](https://github.com/yigitsag)

🎓 **Akademik Danışman:** [Evrim Güler](https://github.com/evrimguler)