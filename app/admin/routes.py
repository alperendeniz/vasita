"""
app/admin/routes.py — Admin blueprint route'ları

Route'lar:
    GET  /admin/dashboard               → dashboard()        — Admin paneli (araçlar ve onay bekleyen şikayetler)
    GET  /admin/vehicle/add             → add_vehicle()      — Araç ekleme formu
    POST /admin/vehicle/add             → add_vehicle()      — Araç kaydet (resim upload)
    POST /admin/complaint/<id>/verify   → verify_complaint() — Şikayet onayla/kaldır (CSRF korumalı)
"""

import os
import uuid

import sqlalchemy as sa
from flask import abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy.orm import selectinload
from werkzeug.utils import secure_filename

from app import db
from app.admin import admin
from app.admin.forms import AddVehicleForm, VerifyForm
from app.decorators import admin_required
from app.models import Complaint, Vehicle

# Kabul edilen dosya uzantıları
ALLOWED_EXTENSIONS: set[str] = {"png", "jpg", "jpeg"}


def _allowed_file(filename: str) -> bool:
    """Dosya uzantısının whitelist'te olup olmadığını kontrol eder."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@admin.route("/dashboard")
@login_required
@admin_required
def dashboard():
    """Yönetici paneli ana sayfası.
    
    SQLAlchemy 2.x kullanılarak araçlar ve onay bekleyen şikayetler listelenir.
    """
    # Araçları çek
    stmt_vehicles = sa.select(Vehicle).order_by(Vehicle.brand, Vehicle.model, Vehicle.year)
    vehicles = db.session.execute(stmt_vehicles).scalars().all()

    # Onay bekleyen şikayetleri çek
    stmt_pending = (
        sa.select(Complaint)
        .where(Complaint.is_verified == False)
        .options(selectinload(Complaint.author), selectinload(Complaint.vehicle))
        .order_by(Complaint.created_at.asc())
    )
    pending_complaints = db.session.execute(stmt_pending).scalars().all()

    return render_template(
        "admin/dashboard.html",
        vehicles=vehicles,
        pending_complaints=pending_complaints,
        verify_form=VerifyForm(),
    )


@admin.route("/vehicle/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_vehicle():
    """Sisteme yeni araç ekleme formu ve dosya yükleme işlemi."""
    form = AddVehicleForm()

    if form.validate_on_submit():
        brand = form.brand.data.strip()
        model = form.model.data.strip()
        year = form.year.data

        # Aynı marka/model/yıl aracı var mı kontrolü (opsiyonel ama iyi bir pratik)
        existing = db.session.execute(
            sa.select(Vehicle).where(
                Vehicle.brand == brand,
                Vehicle.model == model,
                Vehicle.year == year
            )
        ).scalar_one_or_none()
        
        if existing:
            flash("Bu araç (Marka, Model, Yıl) sistemde zaten mevcut.", "warning")
            return redirect(url_for("admin.add_vehicle"))

        new_vehicle = Vehicle(brand=brand, model=model, year=year)

        # Fotoğraf yükleme katmanı
        image_file = form.image.data
        if image_file and image_file.filename:
            if not _allowed_file(image_file.filename):
                flash("Yalnızca PNG, JPG veya JPEG dosyaları kabul edilmektedir.", "danger")
                return redirect(url_for("admin.add_vehicle"))

            safe_name = secure_filename(image_file.filename)
            unique_name = f"{uuid.uuid4().hex}_{safe_name}"
            pics_dir = os.path.join(current_app.root_path, "static", "vehicle_pics")
            os.makedirs(pics_dir, exist_ok=True)
            save_path = os.path.join(pics_dir, unique_name)
            image_file.save(save_path)

            new_vehicle.image_file = unique_name

        db.session.add(new_vehicle)
        db.session.commit()
        flash(f"{brand} {model} aracı başarıyla eklendi.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/add_vehicle.html", form=form)


@admin.route("/complaint/<int:id>/verify", methods=["POST"])
@login_required
@admin_required
def verify_complaint(id: int):
    """Şikayet onaylama (is_verified toggle) rotası.
    
    Yalnızca POST isteği kabul edilir. CSRF koruması VerifyForm üzerinden sağlanır.
    """
    form = VerifyForm()
    if form.validate_on_submit():
        complaint = db.session.get(Complaint, id)
        if complaint is None:
            abort(404)

        # Toggle işlemi
        complaint.is_verified = not complaint.is_verified
        db.session.commit()
        
        status_text = "onaylandı" if complaint.is_verified else "onayı kaldırıldı"
        flash(f"Şikayet {status_text}.", "success")
    else:
        flash("Geçersiz işlem veya süresi dolmuş form.", "danger")

    return redirect(request.referrer or url_for("admin.dashboard"))
