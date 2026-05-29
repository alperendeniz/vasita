"""
app/auth/forms.py — Kimlik doğrulama form sınıfları

Formlar:
    RegistrationForm — Kullanıcı kaydı; username ve email benzersizliği
                       validate_<field> convention ile otomatik doğrulanır.
    LoginForm        — Kullanıcı girişi; remember_me seçeneği ile.
"""

import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import BooleanField, EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError

from app import db
from app.models import User


# ---------------------------------------------------------------------------
# Kayıt Formu
# ---------------------------------------------------------------------------

class RegistrationForm(FlaskForm):
    """Yeni kullanıcı kayıt formu."""

    username = StringField(
        "Kullanıcı Adı",
        validators=[
            DataRequired(message="Kullanıcı adı zorunludur."),
            Length(min=3, max=80, message="Kullanıcı adı 3–80 karakter arasında olmalıdır."),
        ],
    )
    email = EmailField(
        "E-posta",
        validators=[
            DataRequired(message="E-posta adresi zorunludur."),
            Email(message="Geçerli bir e-posta adresi girin."),
        ],
    )
    password = PasswordField(
        "Şifre",
        validators=[
            DataRequired(message="Şifre zorunludur."),
            Length(min=8, message="Şifre en az 8 karakter olmalıdır."),
            Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&.,_+\-]).{8,}$',
                message="Şifreniz en az bir büyük harf, bir küçük harf, bir rakam ve bir özel karakter (@$!%*?&.,_+-) içermelidir.",
            ),
        ],
    )
    confirm_password = PasswordField(
        "Şifre Tekrar",
        validators=[
            DataRequired(message="Şifre tekrarı zorunludur."),
            EqualTo("password", message="Şifreler eşleşmiyor."),
        ],
    )
    submit = SubmitField("Kayıt Ol")

    # ------------------------------------------------------------------
    # Custom validator'lar — Flask-WTF, validate_<field_name> adlı
    # metotları otomatik olarak doğrulama zinciri içinde çağırır.
    # ------------------------------------------------------------------

    def validate_username(self, field: StringField) -> None:
        """Kullanıcı adının veritabanında benzersiz olduğunu doğrular."""
        stmt = sa.select(User).filter_by(username=field.data)
        user = db.session.execute(stmt).scalar_one_or_none()
        if user is not None:
            raise ValidationError("Bu kullanıcı adı zaten alınmış, başka bir tane deneyin.")

    def validate_email(self, field: EmailField) -> None:
        """E-posta adresinin veritabanında benzersiz olduğunu doğrular."""
        stmt = sa.select(User).filter_by(email=field.data)
        user = db.session.execute(stmt).scalar_one_or_none()
        if user is not None:
            raise ValidationError("Bu e-posta adresi zaten kayıtlı.")


# ---------------------------------------------------------------------------
# Giriş Formu
# ---------------------------------------------------------------------------

class LoginForm(FlaskForm):
    """Kullanıcı giriş formu."""

    email = EmailField(
        "E-posta",
        validators=[
            DataRequired(message="E-posta adresi zorunludur."),
            Email(message="Geçerli bir e-posta adresi girin."),
        ],
    )
    password = PasswordField(
        "Şifre",
        validators=[
            DataRequired(message="Şifre zorunludur."),
        ],
    )
    remember_me = BooleanField("Beni Hatırla")
    submit = SubmitField("Giriş Yap")
