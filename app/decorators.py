"""
app/decorators.py — Özel Dekoratörler

RBAC (Rol Tabanlı Erişim Kontrolü) için kullanılan güvenlik katmanları.
"""

from functools import wraps

from flask import abort
from flask_login import current_user


def admin_required(f):
    """
    Kullanıcının 'admin' rolüne sahip olup olmadığını kontrol eden dekoratör.
    Eğer kullanıcı giriş yapmamışsa veya rolü 'admin' değilse 403 (Forbidden) fırlatır.
    Bu dekoratör genellikle @login_required ile birlikte veya onun yerine (eğer authenticate kontrolü içeriyorsa) kullanılır.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
