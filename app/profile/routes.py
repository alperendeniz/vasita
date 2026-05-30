"""
app/profile/routes.py — Profil blueprint route'ları

Route'lar:
    GET  /profile        → profile()      — Kullanıcı profili + kendi şikayetleri
    GET  /profile/edit   → edit_profile() — Profil düzenleme formu
    POST /profile/edit   → edit_profile() — Bio ve avatar güncelle
"""

import os
import uuid

import sqlalchemy as sa
from flask import abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app import db
from app.main.forms import DeleteForm
from app.models import Complaint
from app.profile import profile
from app.profile.forms import EditProfileForm

# Kabul edilen dosya uzantıları — whitelist
ALLOWED_EXTENSIONS: set[str] = {"png", "jpg", "jpeg"}


def _allowed_file(filename: str) -> bool:
    """Dosya uzantısının whitelist'te olup olmadığını kontrol eder."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Profil Görüntüle
# ---------------------------------------------------------------------------

@profile.route("/")
@login_required
def profile_view():
    """Giriş yapmış kullanıcının profilini ve kendi şikayetlerini gösterir."""
    stmt = (
        sa.select(Complaint)
        .where(Complaint.user_id == current_user.id)
        .order_by(Complaint.created_at.desc())
    )
    my_complaints = db.session.execute(stmt).scalars().all()

    return render_template(
        "profile/profile.html",
        complaints=my_complaints,
        delete_form=DeleteForm(),
    )


# ---------------------------------------------------------------------------
# Profil Düzenle
# ---------------------------------------------------------------------------

@profile.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    """Kullanıcının bio ve profil fotoğrafını güncellemesini sağlar.

    Dosya Yükleme Güvenliği (4 katman):
        1. ALLOWED_EXTENSIONS whitelist  → .exe, .php vb. reddedilir.
        2. secure_filename()             → Path traversal engellenir.
        3. uuid.uuid4().hex prefix       → Dosya çakışması engellenir.
        4. Eski avatar cleanup           → Disk israfı engellenir (default.jpg korunur).
    """
    form = EditProfileForm()

    if form.validate_on_submit():
        # --- Bio güncelle ---------------------------------------------------
        bio_data = form.bio.data.strip() if form.bio.data else None
        current_user.bio = bio_data or None

        # --- Avatar yükle ---------------------------------------------------
        avatar_file = form.avatar.data
        if avatar_file and avatar_file.filename:
            if not _allowed_file(avatar_file.filename):
                flash("Yalnızca PNG, JPG veya JPEG dosyaları kabul edilmektedir.", "danger")
                return redirect(url_for("profile.edit_profile"))

            safe_name   = secure_filename(avatar_file.filename)
            unique_name = f"{uuid.uuid4().hex}_{safe_name}"
            pics_dir    = os.path.join(current_app.root_path, "static", "profile_pics")
            os.makedirs(pics_dir, exist_ok=True)
            save_path   = os.path.join(pics_dir, unique_name)
            avatar_file.save(save_path)

            # --- Storage Cleanup: eski avatarı sil (default değilse) --------
            old_avatar = current_user.avatar_file
            if old_avatar and old_avatar != "default.jpg":
                old_path = os.path.join(pics_dir, old_avatar)
                if os.path.exists(old_path):
                    os.remove(old_path)

            current_user.avatar_file = unique_name

        db.session.commit()
        flash("Profiliniz başarıyla güncellendi.", "success")
        return redirect(url_for("profile.profile_view"))

    # GET: Formu mevcut verilerle doldur
    if request.method == "GET":
        form.bio.data = current_user.bio

    return render_template("profile/edit_profile.html", form=form)

