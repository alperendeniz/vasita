"""
app/admin/forms.py — Yönetici formu tanımları
"""
from datetime import datetime

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class AddVehicleForm(FlaskForm):
    """Sisteme yeni araç ekleme formu."""

    brand = StringField(
        "Marka",
        validators=[
            DataRequired(message="Marka alanı zorunludur."),
            Length(max=80, message="Marka en fazla 80 karakter olabilir."),
        ],
    )
    model = StringField(
        "Model",
        validators=[
            DataRequired(message="Model alanı zorunludur."),
            Length(max=80, message="Model en fazla 80 karakter olabilir."),
        ],
    )
    year = IntegerField(
        "Yıl",
        validators=[
            DataRequired(message="Yıl alanı zorunludur."),
            NumberRange(
                min=1900,
                max=datetime.now().year + 1,
                message="Geçerli bir yıl giriniz.",
            ),
        ],
    )
    image = FileField("Araç Fotoğrafı")
    submit = SubmitField("Aracı Ekle")


class VerifyForm(FlaskForm):
    """
    Şikayet onaylama (is_verified toggle) işlemi için boş form.
    Sadece CSRF hidden_tag() üretmek maksadıyla kullanılır.
    """
    pass
