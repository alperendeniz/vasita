## Oturum 1 - 25 Mayıs 2026 18:00–18:40

### Hedef
Flask 3.x ile Application Factory pattern kullanan, `main` ve `auth` blueprint'lerine ayrılmış, temiz bir proje iskeleti kurmak. Hiçbir model, route veya template yazmadan yalnızca klasör yapısını ve başlatıcı dosyaları oluşturmak.

### Kullandığım Mod ve Model
- Mod: Plan
- Model: Claude Sonnet 4.6
- Görünüm: Manager

### Verdiğim Promptlar
1. BLG106 İnternet Programcılığı dersi için "Vasıta" projesinin Flask 3.x iskeleti kurulsun; Application Factory + Blueprint mimarisi, sadece 6 paket (flask, flask-sqlalchemy, flask-migrate, flask-login, flask-wtf, python-dotenv), model/route/template olmadan yalnızca iskelet, `.env` gizlensin ve her klasörde `__init__.py` bulunsun — önce plan göster, onayımdan sonra dosyaları oluştur.

### Ajanın Önerdiği Plan
Aşağıdaki klasör iskeleti planlandı ve onayımın ardından uygulandı:

```
vasita/
├── app/
│   ├── __init__.py       ← create_app() factory
│   ├── models.py         ← boş placeholder
│   ├── main/
│   │   ├── __init__.py   ← main Blueprint
│   │   └── routes.py     ← boş placeholder
│   ├── auth/
│   │   ├── __init__.py   ← auth Blueprint (url_prefix=/auth)
│   │   └── routes.py     ← boş placeholder
│   ├── templates/        ← .gitkeep
│   └── static/           ← .gitkeep
├── migrations/           ← .gitkeep
├── tests/
│   └── __init__.py
├── config.py             ← Dev / Prod / Test sınıfları
├── requirements.txt      ← 6 paket
├── .env.example
├── .gitignore            ← .env dahil
└── run.py
```

![Plan Resmi](docs/img/oturum-1-plan.png)

### Plan'da Sorguladıklarım
Bu aşamada plana müdahale etmedim çünkü güvenlik kısıtlarına ve paket sayılarına uygun bir iskelet sundun.

### Üretilen Kodda Düzelttiklerim
Henüz kod üretilmedi, sadece iskelet kuruldu.

### Karşılaştığım Hatalar ve Çözümler
- Hata: Ajan terminal üzerinden `python -m venv .venv` komutunu çalıştırmaya çalıştı; ancak sandbox ortamındaki PowerShell `FileSystem` sürücüsü kısıtı nedeniyle komut başarısız oldu.
- Çözüm: Sanal ortam kurulumu, paket yüklemesi (`pip install -r requirements.txt`) ve Git commit işlemi terminal kısıtı aşılarak manuel olarak gerçekleştirildi. 16 dosya başarıyla commit edildi (`340fdf7`).

### Bu Oturumdan Öğrendiğim
- Application Factory pattern'in ne olduğunun ne işe yaradığını,
- Blueprint'lerin ne olduğunun ne işe yaradığını,
### Sonraki Oturum İçin Notlar
- Faz 2: SQLAlchemy 2.x Veritabanı Modelleri ve Migrasyonlar aşamasına geçilecek.

---

## Oturum 2 - 28 Mayıs 2026 15:46–16:09

### Hedef
Faz 1'de kurulan Application Factory + Blueprint mimarisinin üzerine, `app/models.py` dosyasını SQLAlchemy 2.x standartlarıyla oluşturmak. User, Vehicle, Complaint ve Comment modellerini, aralarındaki çift yönlü ilişkilerle birlikte yazmak.

### Kullandığım Mod ve Model
- Mod: Plan
- Model: Claude Sonnet 4.6 (Thinking)
- Görünüm: Manager

### Verdiğim Promptlar
1. `app/models.py` dosyası içine SQLAlchemy 2.x sözdizimini (`Mapped[T]` + `mapped_column()`) kullanarak User, Vehicle, Complaint ve Comment modellerini, `back_populates` ile çift yönlü ilişkilerle birlikte yaz; önce plan göster, onayımdan sonra kodu yaz.
2. Complaint ve Comment modellerindeki yabancı anahtar sütunlarına ve `is_verified` alanına `index=True` parametresini ekle.

### Ajanın Önerdiği Plan
Dört model için aşağıdaki tablo ve ilişki yapısı planlandı, onayımın ardından uygulandı:

| Model | Temel Alanlar | Özellikler |
|---|---|---|
| `User` | id, username, email, password_hash, role | `UserMixin`, `set_password()`, `check_password()` |
| `Vehicle` | id, brand, model, year | FK olmayan bağımsız tablo |
| `Complaint` | id, title, description, is_verified, created_at, user_id, vehicle_id | Hem User hem Vehicle'a FK |
| `Comment` | id, content, created_at, user_id, complaint_id | Hem User hem Complaint'e FK |

İlişki yönü: `User → Complaint`, `User → Comment`, `Vehicle → Complaint`, `Complaint → Comment` (hepsi `back_populates` ile çift yönlü).

![Faz 2 Modeller ve İndeksleme](docs/img/oturum-2-modeller.png)

### Plan'da Sorguladıklarım ve Üretilen Kodda Düzelttiklerim
- Ajanın yazdığı kodda yabancı anahtarlara (FK) ve sık filtrelenen `is_verified` alanına indeks atanmamıştı. Arama performansını artırmak için ilgili alanlara manuel olarak `index=True` parametresini eklettirdim.

### Karşılaştığım Hatalar ve Çözümler
- Hata: Ajan, import doğrulaması için terminal üzerinden Python komutunu çalıştırmaya çalıştı; ancak sandbox ortamındaki PowerShell `FileSystem` sürücüsü kısıtı nedeniyle komut başarısız oldu.
- Çözüm: Doğrulama (`python -c "from app.models import ..."`) manuel olarak kendi terminalimde çalıştırıldı. Çıktı `OK` olarak döndü.

### Bu Oturumdan Öğrendiğim
- İndeksleme (index=True) işleminin veritabanı sorgularında ne işe yaradığı, avantajları ve dezavantajları.
- Hard Delete ve Soft Delete kavramları. Hangisinin nerede kullanılması gerektiği, faydaları ve zararları.

### Sonraki Oturum İçin Notlar
- Faz 3: Flask-Migrate ile veritabanı fiziksel kurulumu (db init, migrate, upgrade).
