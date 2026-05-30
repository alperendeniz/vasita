"""
app/main/forms.py — Ana blueprint form sınıfları

Formlar:
    ComplaintForm — Araç şikayeti ekleme formu.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class ComplaintForm(FlaskForm):
    """Araç şikayeti ekleme formu."""

    title = StringField(
        "Başlık",
        validators=[
            DataRequired(message="Başlık zorunludur."),
            Length(max=200, message="Başlık en fazla 200 karakter olabilir."),
        ],
    )
    description = TextAreaField(
        "Açıklama",
        validators=[
            DataRequired(message="Açıklama zorunludur."),
        ],
    )
    submit = SubmitField("Şikayet Bildir")


class DeleteForm(FlaskForm):
    """CSRF korumalı silme formu.

    Alan içermez; yalnızca ``hidden_tag()`` üretmek için kullanılır.
    Bu sayede şablon içindeki silme ``<form>`` etiketleri CSRF token taşır.
    """
    pass
