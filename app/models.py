"""
app/models.py — Vasıta Veritabanı Modelleri

Modeller:
    User        — Kayıtlı kullanıcılar (Flask-Login entegrasyonu)
    Vehicle     — Araç kataloğu (marka / model / yıl)
    Complaint   — Araçlara ait şikayetler / kronik sorunlar
    Comment     — Şikayetlere yapılan kullanıcı yorumları

Sözdizimi: SQLAlchemy 2.x  →  Mapped[T] + mapped_column()
"""

from __future__ import annotations

import sqlalchemy as sa
from datetime import datetime, timezone
from typing import Optional

from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


# ---------------------------------------------------------------------------
# User — Kullanıcı
# ---------------------------------------------------------------------------

class User(UserMixin, db.Model):
    """Sisteme kayıtlı kullanıcı.

    Flask-Login'in ihtiyaç duyduğu ``is_authenticated``, ``is_active``,
    ``is_anonymous`` ve ``get_id()`` metotları UserMixin aracılığıyla gelir.
    """

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(sa.String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(sa.String(120), unique=True, nullable=False)
    # OAuth gibi şifresiz girişlere olanak tanımak için nullable bırakıldı.
    password_hash: Mapped[Optional[str]] = mapped_column(sa.String(256))
    role: Mapped[str] = mapped_column(sa.String(20), nullable=False, default="user")
    bio: Mapped[Optional[str]] = mapped_column(sa.String(300))
    avatar_file: Mapped[str] = mapped_column(
        sa.String(120), nullable=False, default="default.jpg", server_default="default.jpg"
    )

    # İlişkiler — çift yönlü (back_populates)
    complaints: Mapped[list[Complaint]] = relationship(
        "Complaint", back_populates="author", cascade="all, delete-orphan"
    )
    comments: Mapped[list[Comment]] = relationship(
        "Comment", back_populates="author", cascade="all, delete-orphan"
    )
    upvotes: Mapped[list[Upvote]] = relationship(
        "Upvote", back_populates="user", cascade="all, delete-orphan"
    )

    # ------------------------------------------------------------------
    # Şifre yönetimi
    # ------------------------------------------------------------------

    def set_password(self, password: str) -> None:
        """Verilen düz-metin şifreyi hash'leyerek ``password_hash``'e yazar."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verilen düz-metin şifreyi saklanan hash ile karşılaştırır."""
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} role={self.role!r}>"


# ---------------------------------------------------------------------------
# Vehicle — Araç
# ---------------------------------------------------------------------------

class Vehicle(db.Model):
    """Araç kataloğu. Her şikayet bir araca bağlıdır."""

    __tablename__ = "vehicle"

    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(sa.String(80), nullable=False)
    model: Mapped[str] = mapped_column(sa.String(80), nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    image_file: Mapped[str] = mapped_column(
        sa.String(120), nullable=False, default="default_car.jpg", server_default="default_car.jpg"
    )

    # İlişkiler
    complaints: Mapped[list[Complaint]] = relationship(
        "Complaint", back_populates="vehicle", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Vehicle id={self.id} brand={self.brand!r} model={self.model!r} year={self.year}>"


# ---------------------------------------------------------------------------
# Complaint — Şikayet / Kronik Sorun
# ---------------------------------------------------------------------------

class Complaint(db.Model):
    """Bir araca ait kullanıcı şikayeti ya da kronik sorun bildirimi."""

    __tablename__ = "complaint"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text, nullable=False)
    is_verified: Mapped[bool] = mapped_column(nullable=False, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Yabancı anahtarlar
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("user.id"), nullable=False, index=True)
    vehicle_id: Mapped[int] = mapped_column(sa.ForeignKey("vehicle.id"), nullable=False, index=True)

    # İlişkiler — çift yönlü
    author: Mapped[User] = relationship("User", back_populates="complaints")
    vehicle: Mapped[Vehicle] = relationship("Vehicle", back_populates="complaints")
    comments: Mapped[list[Comment]] = relationship(
        "Comment", back_populates="complaint", cascade="all, delete-orphan"
    )
    upvotes: Mapped[list[Upvote]] = relationship(
        "Upvote", back_populates="complaint", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Complaint id={self.id} title={self.title!r} "
            f"is_verified={self.is_verified}>"
        )


# ---------------------------------------------------------------------------
# Comment — Yorum
# ---------------------------------------------------------------------------

class Comment(db.Model):
    """Bir şikayete yapılan kullanıcı yorumu."""

    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str] = mapped_column(sa.Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Yabancı anahtarlar
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("user.id"), nullable=False, index=True)
    complaint_id: Mapped[int] = mapped_column(sa.ForeignKey("complaint.id"), nullable=False, index=True)

    # İlişkiler — çift yönlü
    author: Mapped[User] = relationship("User", back_populates="comments")
    complaint: Mapped[Complaint] = relationship("Complaint", back_populates="comments")

    def __repr__(self) -> str:
        return f"<Comment id={self.id} user_id={self.user_id} complaint_id={self.complaint_id}>"


# ---------------------------------------------------------------------------
# Upvote — "Ben de yaşıyorum" Desteği
# ---------------------------------------------------------------------------

class Upvote(db.Model):
    """Bir kullanıcının bir şikayete verdiği destek oyu."""

    __tablename__ = "upvote"
    __table_args__ = (
        sa.UniqueConstraint("user_id", "complaint_id", name="uix_user_complaint_upvote"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Yabancı anahtarlar
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("user.id"), nullable=False, index=True)
    complaint_id: Mapped[int] = mapped_column(sa.ForeignKey("complaint.id"), nullable=False, index=True)

    # İlişkiler
    user: Mapped[User] = relationship("User", back_populates="upvotes")
    complaint: Mapped[Complaint] = relationship("Complaint", back_populates="upvotes")

    def __repr__(self) -> str:
        return f"<Upvote id={self.id} user_id={self.user_id} complaint_id={self.complaint_id}>"


# ---------------------------------------------------------------------------
# Flask-Login — Oturum kullanıcı yükleyici
# ---------------------------------------------------------------------------

from app import login_manager  # noqa: E402  (modül düzeyi import; circular-safe)


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    """Flask-Login'in her istekte oturumdaki kullanıcıyı yüklemek için çağırdığı fonksiyon.

    ``db.session.get()`` SQLAlchemy 2.x'in birincil anahtar ile
    tek kayıt çekme yöntemidir (eski ``Query.get()`` kaldırıldı).
    """
    return db.session.get(User, int(user_id))

