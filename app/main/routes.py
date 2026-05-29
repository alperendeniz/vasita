"""
app/main/routes.py — Ana blueprint route'ları

Route'lar:
    GET  /                              → index()           — Araç listesi
    GET  /vehicle/<int:id>              → vehicle_detail()  — Araç detayı + şikayetler
    GET  /vehicle/<int:id>/complaint    → create_complaint() — Şikayet ekleme formu
    POST /vehicle/<int:id>/complaint    → create_complaint() — Şikayet kaydet
"""

import sqlalchemy as sa
from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm import selectinload

from app import db
from app.main import main
from app.main.forms import ComplaintForm
from app.models import Complaint, Vehicle


# ---------------------------------------------------------------------------
# Ana Sayfa — Araç Listesi
# ---------------------------------------------------------------------------

@main.route("/")
def index():
    """Veritabanındaki tüm araçları şikayet sayılarıyla birlikte listeler.

    ``selectinload`` ile N+1 sorgu problemi önlenir: Vehicle listesi tek
    sorguda çekilir, her aracın ``complaints`` ilişkisi ikinci bir toplu
    sorguda (SELECT ... WHERE vehicle_id IN (...)) yüklenir.
    """
    stmt = (
        sa.select(Vehicle)
        .options(selectinload(Vehicle.complaints))
        .order_by(Vehicle.brand, Vehicle.model, Vehicle.year)
    )
    vehicles = db.session.execute(stmt).scalars().all()
    return render_template("main/index.html", vehicles=vehicles)


# ---------------------------------------------------------------------------
# Araç Detayı
# ---------------------------------------------------------------------------

@main.route("/vehicle/<int:id>")
def vehicle_detail(id: int):
    """Seçilen aracın detayını ve o araca ait şikayetleri gösterir."""
    vehicle = db.session.get(Vehicle, id)
    if vehicle is None:
        abort(404)

    stmt = (
        sa.select(Complaint)
        .where(Complaint.vehicle_id == id)
        .order_by(Complaint.created_at.desc())
    )
    complaints = db.session.execute(stmt).scalars().all()

    return render_template(
        "main/vehicle_detail.html",
        vehicle=vehicle,
        complaints=complaints,
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
