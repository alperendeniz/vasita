"""
app/profile/forms.py — Profil düzenleme form sınıfı
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Length, Optional


class EditProfileForm(FlaskForm):
    """Kullanıcı profili düzenleme formu.

    ``bio``    — Opsiyonel; en fazla 300 karakter.
    ``avatar`` — Opsiyonel dosya alanı. Uzantı doğrulaması route katmanında
                 whitelist ile yapılır (daha güvenli ve esnek).
    """

    bio = TextAreaField(
        "Hakkımda",
        validators=[
            Optional(),
            Length(max=300, message="Biyografi en fazla 300 karakter olabilir."),
        ],
    )
    avatar = FileField("Profil Fotoğrafı")
    submit = SubmitField("Kaydet")
