"""
app/main/routes.py — Ana blueprint route'ları

Route'lar:
    GET  /                              → index()            — Araç listesi (arama + sayfalama)
    GET  /vehicle/<int:id>              → vehicle_detail()   — Araç detayı + şikayetler (sayfalama)
    GET  /vehicle/<int:id>/complaint    → create_complaint() — Şikayet ekleme formu
    POST /vehicle/<int:id>/complaint    → create_complaint() — Şikayet kaydet

Hata Yöneticileri:
    404 — Sayfa / kayıt bulunamadı
    500 — Sunucu hatası
"""

import sqlalchemy as sa
from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm import selectinload

from app import db
from app.main import main
from app.main.forms import ComplaintForm
from app.models import Complaint, Vehicle


# ---------------------------------------------------------------------------
# Ana Sayfa — Araç Listesi (arama + sayfalama)
# ---------------------------------------------------------------------------

@main.route("/")
def index():
    """Araç listesini arama ve sayfalama ile birlikte render eder.

    ``q``   — GET parametresi; Vehicle.brand veya Vehicle.model üzerinde
               büyük/küçük harf duyarsız (ilike) arama yapar.
    ``page`` — GET parametresi; geçersiz değerde 404 fırlatmak yerine
               boş sayfa döner (error_out=False).
    ``selectinload`` N+1 optimizasyonu korunur.
    """
    q    = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)

    stmt = (
        sa.select(Vehicle)
        .options(selectinload(Vehicle.complaints))
        .order_by(Vehicle.brand, Vehicle.model, Vehicle.year)
    )

    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(
            sa.or_(
                Vehicle.brand.ilike(pattern),
                Vehicle.model.ilike(pattern),
            )
        )

    # db.paginate() — Flask-SQLAlchemy 3.x / SQLAlchemy 2.x API
    # Eski Query.paginate() kullanılmıyor.
    pagination = db.paginate(stmt, page=page, per_page=9, error_out=False)

    return render_template(
        "main/index.html",
        pagination=pagination,
        vehicles=pagination.items,
        q=q,
    )


# ---------------------------------------------------------------------------
# Araç Detayı (şikayet sayfalama)
# ---------------------------------------------------------------------------

@main.route("/vehicle/<int:id>")
def vehicle_detail(id: int):
    """Seçilen aracın detayını ve şikayetlerini sayfalama ile gösterir."""
    vehicle = db.session.get(Vehicle, id)
    if vehicle is None:
        abort(404)

    page = request.args.get("page", 1, type=int)
    stmt = (
        sa.select(Complaint)
        .where(Complaint.vehicle_id == id)
        .order_by(Complaint.created_at.desc())
    )
    pagination = db.paginate(stmt, page=page, per_page=10, error_out=False)

    return render_template(
        "main/vehicle_detail.html",
        vehicle=vehicle,
        complaints=pagination.items,
        pagination=pagination,
    )


# ---------------------------------------------------------------------------
# Şikayet Ekle
# ---------------------------------------------------------------------------

@main.route("/vehicle/<int:id>/complaint", methods=["GET", "POST"])
@login_required
def create_complaint(id: int):
    """Giriş yapmış kullanıcının seçilen araca şikayet eklemesini sağlar.

    title alanına ``strip()`` uygulanarak baş/sondaki boşluklar temizlenir.
    Başarılı kayıt sonrası araç detay sayfasına yönlendirilir.
    """
    vehicle = db.session.get(Vehicle, id)
    if vehicle is None:
        abort(404)

    form = ComplaintForm()

    if form.validate_on_submit():
        complaint = Complaint(
            title=form.title.data.strip(),
            description=form.description.data,
            user_id=current_user.id,
            vehicle_id=vehicle.id,
        )
        db.session.add(complaint)
        db.session.commit()
        flash("Şikayetiniz başarıyla iletildi.", "success")
        return redirect(url_for("main.vehicle_detail", id=vehicle.id))

    return render_template(
        "main/create_complaint.html",
        vehicle=vehicle,
        form=form,
    )


# ---------------------------------------------------------------------------
# Hata Yöneticileri — uygulama genelinde (app_errorhandler)
# ---------------------------------------------------------------------------

@main.app_errorhandler(404)
def not_found(e):
    """404 — Sayfa veya kayıt bulunamadı."""
    return render_template("errors/404.html"), 404


@main.app_errorhandler(500)
def server_error(e):
    """500 — Beklenmedik sunucu hatası."""
    return render_template("errors/500.html"), 500
