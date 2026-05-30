"""
app/main/forms.py — Ana blueprint form sınıfları

Formlar:
    ComplaintForm — Araç şikayeti ekleme formu.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class ComplaintForm(FlaskForm):
    """Kullanıcıların yeni şikayet bildirdiği veya mevcut şikayetini düzenlediği form."""

    title = StringField(
        "Şikayet Başlığı",
        validators=[
            DataRequired(message="Lütfen bir başlık giriniz."),
            Length(
                min=5, max=200, message="Başlık 5 ile 200 karakter arasında olmalıdır."
            ),
        ],
    )
    description = TextAreaField(
        "Şikayet Detayı",
        validators=[
            DataRequired(message="Lütfen şikayetinizin detaylarını açıklayınız."),
            Length(min=20, message="Açıklama en az 20 karakter olmalıdır."),
        ],
    )
    submit = SubmitField("Şikayeti Kaydet")


class DeleteForm(FlaskForm):
    """
    Sadece CSRF koruması sağlamak amacıyla oluşturulmuş boş form.
    Silme işlemleri POST metodu ile yapılacağı için hidden_tag() üretir.
    """
    pass


class ActionForm(FlaskForm):
    """
    Buton tıklamaları (örneğin Upvote) için CSRF koruması sağlayan boş form.
    """
    pass


class CommentForm(FlaskForm):
    """Şikayetlere yorum yapma formu."""

    body = TextAreaField(
        "Yorumunuz",
        validators=[
            DataRequired(message="Yorum boş bırakılamaz."),
            Length(max=1000, message="Yorum en fazla 1000 karakter olabilir."),
        ],
    )
    submit = SubmitField("Yorum Yap")
