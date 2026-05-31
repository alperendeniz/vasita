# Vasıta - Araç Kronik Sorun ve Şikayet Platformu

Gazi Üniversitesi Bilişim Güvenliği ve Teknolojisi bölümü standartlarına uygun olarak tasarlanmış ve geliştirilmiş güvenli web uygulaması projesi.

**Yazar:** Ali Alperen Deniz

## Proje Amacı
Vasıta, kullanıcıların otomobillerle ilgili kronik sorunları ve şikayetleri güvenli bir ortamda paylaşabilmelerini sağlayan, uçtan uca Docker mimarisiyle yapılandırılmış bir platformdur. Geliştirme sürecinin temel odak noktası, modern web zafiyetlerine karşı koruma sağlamak ve endüstri standartlarında güvenli bir mimari kurgulamaktır.

## Teknoloji Yığını (Tech Stack)
*   **Web Çerçevesi (Framework):** Flask
*   **ORM Katmanı:** SQLAlchemy 2.x Standardı
*   **Veritabanı:** PostgreSQL
*   **Uygulama Sunucusu (WSGI):** Gunicorn
*   **Konteyner ve Dağıtım:** Docker & Docker Compose
*   **Arayüz ve Şekillendirme:** Tailwind CSS

## Öne Çıkan Güvenlik Mimarisi

*   **Stored XSS (Kalıcı Çapraz Site Betik) Koruması:** Kullanıcı girdilerinin (yorumlar vb.) işlenmesinde Jinja2'nin yerleşik `autoescape` özelliği aktif tutulmuş, riskli `| safe` filtrelerinin kullanımı tamamen yasaklanmıştır. Kullanıcıdan gelen metinlerdeki satır sonlarını (enter karakterleri) korumak için güvenli olan CSS `whitespace-pre-wrap` sınıfı kullanılarak HTML enjeksiyonu riski sıfırlanmıştır.
*   **User Enumeration (Kullanıcı Numaralandırma) Koruması:** Kimlik doğrulama modülünde ve özellikle şifre sıfırlama rotalarında, sisteme girilen e-postanın kayıtlı olup olmadığı bilgisi saldırganlara sızdırılmamıştır. E-posta var olsa da olmasa da sistem aynı "Başarılı" mesajını dönerek kötü niyetli taramaları engellemektedir.
*   **Kriptografik Token Mimarisi:** Parola sıfırlama sürecinde `itsdangerous` kütüphanesi ve `URLSafeTimedSerializer` yapısı kurgulanmıştır. Zaman damgalı ve kriptografik olarak imzalanmış bu tokenlar sayesinde URL üzerinden doğabilecek IDOR zafiyetleri ve yetkisiz erişimler engellenmiştir.
*   **CSRF (Siteler Arası İstek Sahtekarlığı) Koruması:** Durum değiştiren (POST, PUT, DELETE) tüm işlemler, WTForms yapısının sağladığı `hidden_tag()` kriptografik form alanları ile korunmuştur. Sadece JWT/Token mantığına uygun (stateless) olarak tasarlanan `/api/v1/` rotaları bu kalkan sisteminden muaf tutularak mimari uyum sağlanmıştır.

## Bonus Özellikler (Uygulanan Ekstra Kriterler)
*   **Tam Metin Arama (Full-text search):** Şikayet ve araç içeriklerinde yüksek performanslı arama mimarisi.
*   **Güvenli Avatar Yükleme:** Dosya uzantısı kontrolü (whitelist) ve UUID destekli benzersiz isimlerle IDOR ve shell upload korumalı dosya yükleme servisi.
*   **Token Tabanlı Şifre Sıfırlama:** Süresi dolabilen, güvenli ve imzalı e-posta tabanlı parola sıfırlama mimarisi.
*   **RESTful JSON API Katmanı:** Dış sistemler (mobil uygulamalar) için `flask.jsonify` destekli, sayfalama (pagination) özelliği içeren ve statik dosyaları Mutlak (Absolute) URL formatında (`_external=True`) dışa aktaran API uç noktaları.
*   **Race Condition Korumalı Upvote Sistemi:** Kullanıcıların "Ben de yaşıyorum" oylamasında çift oylamayı engellemek adına veritabanı seviyesinde `UniqueConstraint` (Kullanıcı ve Şikayet birleşimi) ile kurgulanan geri bildirim sistemi.

## Docker ile Kurulum ve Çalıştırma

Projeyi değerlendirmek ve tek tıkla ayağa kaldırmak için aşağıdaki adımları izleyebilirsiniz. Uygulama, Gunicorn sunucusu ve PostgreSQL veritabanıyla birlikte çalışacaktır.

Uygulamayı inşa etmek ve başlatmak için proje kök dizininde aşağıdaki komutu çalıştırın:
```bash
docker-compose up --build
```

Konteynerler ayağa kalktıktan sonra, veritabanı şemasını PostgreSQL içerisine kurmak için ayrı bir terminal sekmesi açarak aşağıdaki komutu çalıştırın:
```bash
docker-compose exec web flask db upgrade
```

Bu işlemlerden sonra uygulama `http://127.0.0.1:5000` adresi üzerinden erişilebilir olacaktır.

## API Kullanımı

Dış uygulamaların projeye erişmesi için `/api/v1/vehicles` uç noktası (endpoint) oluşturulmuştur.
*   **Araç Listesi Çekme:** Veritabanına yük bindirmemek için `GET` istekleri API seviyesinde sayfalandırılmıştır. Tarayıcınızdan veya Postman üzerinden `http://127.0.0.1:5000/api/v1/vehicles?page=1` adresi ile araç bilgilerine ulaşabilirsiniz.
*   **Araç Detayı:** Belirli bir araca ait JSON objesini görüntülemek ve araca ait onaylanmış şikayetleri çekmek için `http://127.0.0.1:5000/api/v1/vehicles/<id>` yapısını kullanabilirsiniz.