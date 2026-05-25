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
