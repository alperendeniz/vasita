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

---

## Oturum 3 - 28 Mayıs 2026 16:09–16:29

### Hedef
Faz 2'de tanımlanan modellerin fiziksel SQLite veritabanına dönüştürülmesi. Flask-Migrate ile `db init`, `db migrate` ve `db upgrade` komutlarını çalıştırarak gerçek tablo yapısını oluşturmak.

### Kullandığım Mod ve Model
- Mod: —
- Model: Ajan kullanılmadı, terminalden manuel komutlar girildi.
- Görünüm: —

### Verdiğim Promptlar
—

### Ajanın Önerdiği Plan
—

### Plan'da Sorguladıklarım ve Üretilen Kodda Düzelttiklerim
—

### Karşılaştığım Hatalar ve Çözümler
- Hata: `flask db migrate` sırasında SQLite `"unable to open database file"` hatası verdi.
- Çözüm: Windows dosya sistemindeki ters eğik çizgi (`\`) sorunu ve `.env` dosyasındaki ezici (override) ayarlar nedeniyle göreceli yol çalışmadı. `config.py` içinde `os.path.abspath` kullanılarak mutlak (absolute) yol üretildi ve `.env` içindeki `DATABASE_URL` yorum satırı yapılarak sorun çözüldü.

![Faz 3 Veritabanı Kurulumu](docs/img/oturum-3-db.png)

### Bu Oturumdan Öğrendiğim
- Windows dosya sistemi ve Sqlite'ın dosya yolları ile ilgili farklılıklar.

### Sonraki Oturum İçin Notlar
- Faz 4: Kimlik Doğrulama (Auth) formları ve route'ları.

---

## Oturum 4 - 28 Mayıs 2026 17:39–18:00

### Hedef
Flask-WTF ve Flask-Login kullanarak auth blueprint'inin backend altyapısını kurmak.

### Kullandığım Mod ve Model
- Mod: Plan
- Model: Claude Sonnet 4.6 (Thinking)
- Görünüm: Manager

### Verdiğim Promptlar
1. `app/auth/forms.py` oluştur (RegistrationForm, LoginForm); `app/auth/routes.py` güncelle (register, login, logout); `app/models.py`'ye `user_loader` ekle — önce plan göster, onayımdan sonra uygula.
2. `routes.py`'de e-posta sanitizasyonu (`strip().lower()`) ve `forms.py`'de `Regexp` ile parola karmaşıklığı doğrulaması ekle.

### Ajanın Önerdiği Plan
Üç dosyada yapılacak değişiklikler planlandı ve onayımın ardından uygulandı:

| Dosya | İşlem | İçerik |
|---|---|---|
| `app/auth/forms.py` | 🆕 Oluşturuldu | `RegistrationForm` (unique validator'lar) + `LoginForm` |
| `app/auth/routes.py` | ✏️ Güncellendi | `register`, `login`, `logout` view'ları; open redirect koruması |
| `app/models.py` | ✏️ Güncellendi | `@login_manager.user_loader` + `load_user()` |

![Plan Resmi](docs/img/oturum-4-plan.png)

### Plan'da Sorguladıklarım ve Üretilen Kodda Düzelttiklerim
- Ajanın ürettiği varsayılan form ve route yapısında güvenlik eksikleri vardı. Kendi inisiyatifimle ajana şu iki "Defense in Depth" kuralını eklettirdim:
  1. Parola karmaşıklığını artırmak için wtforms `Regexp` kullanıldı.
  2. Veritabanı tutarlılığı için route tarafında e-posta verisine sanitization (`strip().lower()`) uygulandı.

### Karşılaştığım Hatalar ve Çözümler
- Hata: Ajan, import doğrulaması için sandbox terminalini kullandı; PowerShell `FileSystem` sürücüsü kısıtı nedeniyle komut başarısız oldu.
- Çözüm: Doğrulama (`python -c "from app.auth.forms import RegistrationForm, LoginForm; print('Import OK')"`) kendi terminalimde çalıştırıldı. Çıktı `Import OK` olarak döndü.

![Faz 4 Auth Backend ve Güvenlik](docs/img/oturum-4-auth.png)

### Bu Oturumdan Öğrendiğim
- Girdi Temizleme, Girdi Doğrulama ve Open Redirect koruması (Defense in Depth).

### Sonraki Oturum İçin Notlar
- Faz 5: Tailwind CSS ile Frontend ve Auth HTML şablonlarının oluşturulması.

---

## Oturum 5 - 29 Mayıs 2026 11:27–12:16

### Hedef
Tailwind CSS kullanılarak uygulamanın ana iskeletinin (`base.html`) ve kimlik doğrulama arayüzlerinin (`register.html`, `login.html`) oluşturulması.

### Kullandığım Mod ve Model
- Mod: Plan
- Model: Claude Sonnet 4.6 (Thinking)
- Görünüm: Manager

### Verdiğim Promptlar
1. `base.html` (Tailwind CDN, FontAwesome, Navbar, Flash mesajları), `auth/register.html` ve `auth/login.html` şablonlarını oluştur — önce plan göster, onayımdan sonra yaz.
2. `RegistrationForm`'daki `Regexp` kuralını esnet; özel karakter havuzunu genişlet ve kısıtlayıcı son bloğu `.{8,}$` yap.

### Ajanın Önerdiği Plan
Üç ana şablon ve destekleyici dosyalar oluşturuldu:

| Dosya | İşlem | İçerik |
|---|---|---|
| `app/templates/base.html` | 🆕 Oluşturuldu | Tailwind CDN, FontAwesome, sticky Navbar, Flash alert blokları, Footer |
| `app/templates/auth/register.html` | 🆕 Oluşturuldu | Gradient kart, CSRF `hidden_tag()`, şifre göster/gizle, hata mesajları |
| `app/templates/auth/login.html` | 🆕 Oluşturuldu | Aynı kart yapısı, Beni Hatırla checkbox, güvenlik notu |
| `app/templates/main/index.html` | 🆕 Oluşturuldu | `main.index` redirect'lerinin çökmemesi için yer tutucu |
| `app/main/routes.py` | ✏️ Güncellendi | `index` view fonksiyonu eklendi |


### Plan'da Sorguladıklarım ve Üretilen Kodda Düzelttiklerim
—Ajanın ürettiği arayüz ve doğrulama kodlarını uçtan uca test ederken üç kritik noktada koda ve ortama doğrudan müdahale etmem gerekti. İlk olarak, kayıt işlemi sırasında alınan "OperationalError" hatasını terminal stack trace üzerinden analiz ederek, SQLite tablolarının Flask uygulama bağlamında (app context) fiziksel olarak oluşmadığını tespit ettim ve flask shell üzerinden db.create_all() ile veritabanını manuel olarak inşa ettim. İkinci olarak, ajanın formda kullandığı Email() doğrulayıcısının arka plan bağımlılığı olan email_validator paketini sanal ortama dahil etmeyi unuttuğunu fark ettim ve paket yönetimini kendim sağladım. Son ve en kritik müdahalemi bir uç durum (edge case) testinde yaptım: "Alperen.2026!" gibi güçlü bir parolanın reddedildiğini gördüğümde, ajanın ürettiği Regexp kuralının nokta (.) gibi işaretleri dışlayarak siber güvenlik 'kullanılabilirlik' (usability) standartlarını ihlal ettiğini belirledim. Ajana komut vererek özel karakter havuzunu (.,_+-) genişlettirdim ve lookahead mantığını koruyarak şifre sonu kısıtlamasını .{8,}$ olarak güncellettirdim.

### Karşılaştığım Hatalar ve Çözümler
- **Hata 1 — Veritabanı Tablo Hatası:** İlk testte `sqlite3.OperationalError: no such table: user` hatası alındı. Uygulama bağlamında SQLite tablolarının fiziksel olarak tam oluşmadığı tespit edildi. Terminalde `flask shell` açılarak `db.create_all()` komutuyla tablolar manuel yaratıldı ve sorun çözüldü.
![Hata 1](docs/img/oturum-5-hata-1.png)
- **Hata 2 — Bağımlılık (`email_validator`) Hatası:** Form gönderiminde `ModuleNotFoundError` alındı. WTForms `Email` doğrulayıcısının arka plan bağımlılığı olan bu paket `pip install email-validator` komutuyla kurularak doğrulama zinciri onarıldı.
![Hata 2](docs/img/oturum-5-hata-2.png)
- **Hata 3 — Aşırı Kısıtlayıcı Regex (Uç Durum Testi):** `Alperen.2026!` gibi güçlü parolalar, varsayılan `Regexp` kuralındaki nokta (`.`) eksikliği nedeniyle reddedildi. Siber güvenlik kullanılabilirlik standartları gereği özel karakter havuzu (`.,_+-`) genişletildi ve kısıtlayıcı kural `.{8,}$` olarak esnetildi.
![Regexp Düzeltme Sonrası Başarı](docs/img/oturum-5-regexp-basari.png)

### Bu Oturumdan Öğrendiğim
- Regexp kısıtlamasının ne kadar katı olabileceği ve kullanılabilirlik açısından dengelenmesi gerektiği.

### Sonraki Oturum İçin Notlar
- Faz 6: Araç Kataloğu ve Şikayet Sistemi kapsamında `Vehicle` ve `Complaint` modelleri için ana rotaların ve detay sayfalarının oluşturulması.

---

## Oturum 6 - 29 Mayıs 2026 13:30–13:46

### Hedef
Araçların listelendiği ana sayfanın, araç detay sayfasının ve kitle kaynaklı şikayet ekleme sisteminin (`main` blueprint) oluşturulması.

### Kullandığım Mod ve Model
- Mod: Plan
- Model: Claude Sonnet 4.6 (Thinking)
- Görünüm: Manager

### Verdiğim Promptlar
1. `app/main/forms.py` (ComplaintForm), `app/main/routes.py` (index, vehicle_detail, create_complaint rotaları) ve ilgili HTML şablonlarını oluştur — önce plan göster, onayımdan sonra yaz.
2. `index()` rotasında `selectinload(Vehicle.complaints)` ile N+1 sorgu optimizasyonu ve `create_complaint()` rotasında `title.strip()` sanitizasyonunu koda dahil et.

### Ajanın Önerdiği Plan
Beş dosyada değişiklik planlandı ve onayımın ardından uygulandı:

| Dosya | İşlem | İçerik |
|---|---|---|
| `app/main/forms.py` | 🆕 Oluşturuldu | `ComplaintForm`: `title` (max 200) + `TextAreaField` |
| `app/main/routes.py` | ✏️ Güncellendi | 3 route, SQLAlchemy 2.x `select` API, `selectinload`, `title.strip()` |
| `app/templates/main/index.html` | ✏️ Yeniden Yazıldı | 3-sütun Tailwind Grid, renk kodlu şikayet badge |
| `app/templates/main/vehicle_detail.html` | 🆕 Oluşturuldu | Gradient başlık, `is_verified` badge, `strftime`, boş durum |
| `app/templates/main/create_complaint.html` | 🆕 Oluşturuldu | Auth kart stili, `hidden_tag()`, `resize-y` textarea, Vazgeç linki |

![Plan Resmi](docs/img/oturum-6-plan.png)

### Plan'da Sorguladıklarım ve Üretilen Kodda Düzelttiklerim
- Ajanın başlangıç planında, ana sayfadaki şikayet sayısını hesaplamak için Jinja2 seviyesinde `vehicle.complaints | length` kullanması N+1 SQL sorgusu problemi yaratıyordu. Bu performans açığı tespit edilerek ajana koda müdahale ettirildi ve `selectinload` stratejisiyle eager loading uygulandı.
- Ayrıca, güvenlik ve veri tutarlılığı için `create_complaint` rotasında formdan gelen başlık verisine `strip()` sanitization işlemi uygulattırıldı.

### Karşılaştığım Hatalar ve Çözümler
- Hata yok. Seed data (`flask shell` üzerinden Honda Civic, Toyota Corolla, Renault Megane) eklenerek sistem uçtan uca test edildi ve tüm rotalar başarıyla doğrulandı.

### Bu Oturumdan Öğrendiğim

### Sonraki Oturum İçin Notlar
- Faz 7: Arama/filtreleme altyapısının, sayfalama (pagination) işlemlerinin ve özel hata sayfalarının (404, 500) oluşturulması.




