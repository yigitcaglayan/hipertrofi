# 💪 Hipertrofi — İnteraktif Kas & Egzersiz Rehberi

> Vücudunuzdaki her kasa tıklayın, o kası hedefleyen egzersizleri anında keşfedin. Flask tabanlı, kullanıcı hesaplı ve favori sistemiyle donatılmış interaktif antrenman rehberi.

---

## 📸 Ekran Görüntüleri

> *(Görseller eklenecek)*

| Ana Sayfa — Kas Haritası | Egzersiz Paneli | Favorilerim |
|:---:|:---:|:---:|
| ![Ana Sayfa](screenshots/index.png) | ![Egzersizler](screenshots/exercises.png) | ![Favoriler](screenshots/favorites.png) |

---

## 🚀 Özellikler

- 🗺️ **İnteraktif Kas Haritası** — Ön ve arka vücut görünümüyle 16 farklı kas grubunu haritalar; bir kasa tıklamak o kasın egzersizlerini listeler
- 🏋️ **Zengin Egzersiz Veritabanı** — Göğüs, sırt, omuz, biceps, triceps, karın, quadriceps, hamstring, baldır ve kalça için 80+ egzersiz; her biri açıklama, zorluk seviyesi, ekipman, set ve tekrar bilgisiyle birlikte
- 🔐 **Kullanıcı Sistemi** — Kayıt, giriş ve oturum yönetimi; kullanıcı adı veya e-posta ile giriş desteği
- ⭐ **Favori Sistemi** — Beğendiğin egzersizleri kaydet, kişisel listenle takip et
- 🔄 **Ön / Arka Görünüm** — Vücut modelini öne ve arkaya çevirerek farklı kas gruplarına ulaş
- 🌐 **REST API** — Kas ve egzersiz verileri JSON API üzerinden servis edilir; frontend ile backend tamamen ayrılmış mimari
- 💾 **SQLite Veritabanı** — Sıfır konfigürasyonla çalışır; PythonAnywhere gibi platformlara kolayca deploy edilir

---

## 🛠️ Kullanılan Teknolojiler

| Katman | Teknoloji |
|--------|-----------|
| **Backend** | Python 3, Flask |
| **Veritabanı** | SQLite, sqlite3 |
| **Auth** | Flask Session, Werkzeug |
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) |
| **API** | RESTful JSON API |

---

## 📁 Proje Yapısı

```
hipertrofi/
│
├── app.py                  # Ana uygulama; route'lar, API endpoint'leri ve DB init
├── muscle_trainer.db       # SQLite veritabanı (otomatik oluşturulur)
├── requirements.txt        # Python bağımlılıkları
│
├── templates/
│   └── index.html          # Tek sayfa uygulama arayüzü
│
└── static/
    ├── style.css           # Uygulama stilleri
    ├── script.js           # Kas haritası etkileşimi ve API çağrıları
    └── images/
        └── exercises/      # Egzersiz görselleri (muscle_exercise_N.png formatı)
```

---

## 🗃️ Veritabanı Modelleri

```
users
├── id (PK)
├── username (unique)
├── email (unique)
└── password (hash)

muscle_groups
├── id (PK)
├── name (İngilizce)
├── turkish_name
├── coordinates (JSON)
└── side → "front" | "back"

exercises
├── id (PK)
├── muscle_id (FK → muscle_groups)
├── name / turkish_name
├── description
├── difficulty → "Başlangıç" | "Orta" | "İleri"
├── equipment
├── sets
└── reps

favorites
├── id (PK)
├── user_id (FK → users)
├── exercise_id (FK → exercises)
└── created_at
```

---

## 🔗 API Endpoint'leri

| Method | Endpoint | Açıklama | Auth |
|--------|----------|----------|------|
| `GET` | `/api/muscles` | Tüm kas gruplarını listeler | — |
| `GET` | `/api/exercises/<muscle_id>` | Kas grubuna göre egzersizleri getirir | — |
| `POST` | `/api/register` | Yeni kullanıcı kaydı | — |
| `POST` | `/api/login` | Kullanıcı girişi | — |
| `POST` | `/api/logout` | Oturumu kapatır | ✅ |
| `GET` | `/api/check_auth` | Oturum durumunu kontrol eder | — |
| `GET` | `/api/favorites` | Kullanıcının favorilerini listeler | ✅ |
| `POST` | `/api/favorites` | Favorilere egzersiz ekler | ✅ |
| `DELETE` | `/api/favorites` | Favoriden egzersiz çıkarır | ✅ |

---

## ⚙️ Kurulum

### Gereksinimler

- Python 3.8+
- pip

### Adımlar

```bash
# 1. Repoyu klonla
git clone https://github.com/yigitcaglayan/hipertrofi.git
cd hipertrofi

# 2. Sanal ortam oluştur ve aktif et
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Uygulamayı başlat
python app.py
```

Uygulama ilk çalıştırmada veritabanını, tüm kas gruplarını ve 80+ egzersizi otomatik olarak oluşturur.
Ardından `http://localhost:5000` adresini tarayıcında aç.

---

## 🫀 Desteklenen Kas Grupları

| Ön Görünüm | Arka Görünüm |
|------------|-------------|
| Göğüs | Sırt |
| Ön Kol (Biceps) | Arka Kol (Triceps) |
| Karın | Kalça |
| Ön Bacak (Quadriceps) | Arka Bacak (Hamstrings) |
| Omuz | Baldır |

---

## 👨‍💻 Geliştirici

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/yigitcaglayan">
        <img src="https://github.com/yigitcaglayan.png" width="80px" style="border-radius:50%" alt="Yiğit Çağlayan"/><br/>
        <sub><b>Yiğit Çağlayan</b></sub>
      </a>
    </td>
  </tr>
</table>

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.
