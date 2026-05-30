"""
app/main/routes.py — Ana blueprint route'ları

Route'lar:
    GET  /                              → index()             — Araç listesi (arama + sayfalama)
    GET  /vehicle/<int:id>              → vehicle_detail()    — Araç detayı + şikayetler (sayfalama)
    GET  /vehicle/<int:id>/complaint    → create_complaint()  — Şikayet ekleme formu
    POST /vehicle/<int:id>/complaint    → create_complaint()  — Şikayet kaydet
    GET  /complaint/<int:id>/edit       → edit_complaint()    — Şikayet düzenleme (IDOR korumalı)
    POST /complaint/<int:id>/edit       → edit_complaint()    — Şikayet güncelle
    POST /complaint/<int:id>/delete     → delete_complaint()  — Şikayet sil (IDOR korumalı)

Hata Yöneticileri:
    403, 404, 500
"""

import sqlalchemy as sa
from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm import selectinload

from app import db
from app.main import main
from app.main.forms import ComplaintForm, DeleteForm, CommentForm, ActionForm
from app.models import Complaint, Vehicle, Comment, Upvote


# ---------------------------------------------------------------------------
# Ana Sayfa — Araç Listesi (arama + sayfalama)
# ---------------------------------------------------------------------------

@main.route("/")
def index():
    """Araç listesini arama ve sayfalama ile birlikte render eder."""
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
        .options(
            selectinload(Complaint.author),
            selectinload(Complaint.comments).selectinload(Comment.author),
            selectinload(Complaint.upvotes)
        )
        .order_by(Complaint.created_at.desc())
    )
    pagination = db.paginate(stmt, page=page, per_page=10, error_out=False)

    upvoted_complaint_ids = set()
    if current_user.is_authenticated and pagination.items:
        c_ids = [c.id for c in pagination.items]
        stmt_upvotes = sa.select(Upvote.complaint_id).where(
            Upvote.user_id == current_user.id,
            Upvote.complaint_id.in_(c_ids)
        )
        upvoted_complaint_ids = set(db.session.execute(stmt_upvotes).scalars().all())

    return render_template(
        "main/vehicle_detail.html",
        vehicle=vehicle,
        complaints=pagination.items,
        pagination=pagination,
        delete_form=DeleteForm(),
        comment_form=CommentForm(),
        action_form=ActionForm(),
        upvoted_complaint_ids=upvoted_complaint_ids,
    )


# ---------------------------------------------------------------------------
# Şikayet Ekle
# ---------------------------------------------------------------------------

@main.route("/vehicle/<int:id>/complaint", methods=["GET", "POST"])
@login_required
def create_complaint(id: int):
    """Giriş yapmış kullanıcının seçilen araca şikayet eklemesini sağlar."""
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
# Şikayet Düzenle — IDOR Korumalı
# ---------------------------------------------------------------------------

@main.route("/complaint/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_complaint(id: int):
    """Şikayet sahibinin kendi şikayetini düzenlemesini sağlar.

    IDOR Koruması: Şikayet başka bir kullanıcıya aitse 403 döner.
    """
    complaint = db.session.get(Complaint, id)
    if complaint is None:
        abort(404)
    # ── IDOR KORUMASI ────────────────────────────────────────────────────────
    if complaint.user_id != current_user.id:
        abort(403)
    # ─────────────────────────────────────────────────────────────────────────

    form = ComplaintForm(obj=complaint)

    if form.validate_on_submit():
        complaint.title       = form.title.data.strip()
        complaint.description = form.description.data
        db.session.commit()
        flash("Şikayetiniz başarıyla güncellendi.", "success")
        return redirect(url_for("main.vehicle_detail", id=complaint.vehicle_id))

    return render_template(
        "main/create_complaint.html",
        vehicle=complaint.vehicle,
        form=form,
        edit_mode=True,
        complaint_id=complaint.id,
    )


# ---------------------------------------------------------------------------
# Şikayet Sil — IDOR Korumalı, yalnızca POST
# ---------------------------------------------------------------------------

@main.route("/complaint/<int:id>/delete", methods=["POST"])
@login_required
def delete_complaint(id: int):
    """Şikayet sahibinin kendi şikayetini silmesini sağlar.

    IDOR Koruması: Şikayet başka bir kullanıcıya aitse 403 döner.
    Yalnızca POST kabul edilir; GET isteği 405 döner.
    CSRF koruması: Şablondaki DeleteForm.hidden_tag() ile sağlanır.
    """
    complaint = db.session.get(Complaint, id)
    if complaint is None:
        abort(404)
    # ── IDOR KORUMASI ────────────────────────────────────────────────────────
    if complaint.user_id != current_user.id:
        abort(403)
    # ─────────────────────────────────────────────────────────────────────────

    # commit öncesi vehicle_id'yi hafızaya al — silinmiş nesneden erişilemez
    vehicle_id = complaint.vehicle_id
    db.session.delete(complaint)
    db.session.commit()
    flash("Şikayetiniz silindi.", "info")

    # Kullanıcıyı geldiği sayfaya geri gönder; referrer yoksa profile'a yönlendir
    next_page = request.referrer or url_for("profile.profile_view")
    return redirect(next_page)


# ---------------------------------------------------------------------------
# Sosyal Etkileşim: Yorum ve Upvote
# ---------------------------------------------------------------------------

@main.route("/complaint/<int:id>/comment", methods=["POST"])
@login_required
def comment_complaint(id: int):
    """Şikayete yorum ekler."""
    form = CommentForm()
    if form.validate_on_submit():
        complaint = db.session.get(Complaint, id)
        if complaint is None:
            abort(404)

        comment = Comment(
            body=form.body.data,
            user_id=current_user.id,
            complaint_id=complaint.id
        )
        db.session.add(comment)
        db.session.commit()
        flash("Yorumunuz eklendi.", "success")
    else:
        for _, errors in form.errors.items():
            for error in errors:
                flash(error, "danger")

    return redirect(request.referrer or url_for("main.index"))


@main.route("/complaint/<int:id>/upvote", methods=["POST"])
@login_required
def upvote_complaint(id: int):
    """Şikayeti upvote eder veya varsa kaldırır."""
    form = ActionForm()
    if form.validate_on_submit():
        complaint = db.session.get(Complaint, id)
        if complaint is None:
            abort(404)

        # Kullanıcının bu şikayete upvote'u var mı kontrol et
        existing_upvote = db.session.execute(
            sa.select(Upvote).where(
                Upvote.user_id == current_user.id,
                Upvote.complaint_id == complaint.id
            )
        ).scalar_one_or_none()

        if existing_upvote:
            # Varsa sil (toggle)
            db.session.delete(existing_upvote)
            db.session.commit()
            flash("Sorun desteğiniz kaldırıldı.", "info")
        else:
            # Yoksa ekle
            new_upvote = Upvote(user_id=current_user.id, complaint_id=complaint.id)
            db.session.add(new_upvote)
            db.session.commit()
            flash("Bu sorunu yaşadığınızı belirttiniz.", "success")
    else:
        flash("Geçersiz işlem.", "danger")

    return redirect(request.referrer or url_for("main.index"))


# ---------------------------------------------------------------------------
# Hata Yöneticileri — uygulama genelinde (app_errorhandler)
# ---------------------------------------------------------------------------

@main.app_errorhandler(403)
def forbidden(e):
    """403 — Yetkisiz erişim."""
    return render_template("errors/403.html"), 403


@main.app_errorhandler(404)
def not_found(e):
    """404 — Sayfa veya kayıt bulunamadı."""
    return render_template("errors/404.html"), 404


@main.app_errorhandler(500)
def server_error(e):
    """500 — Beklenmedik sunucu hatası."""
    return render_template("errors/500.html"), 500
