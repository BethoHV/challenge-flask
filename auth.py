from functools import wraps
from models import UserSession

from flask import jsonify, request

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_token = request.headers.get('Authorization')

        if not auth_token:
            return jsonify({"error": "Autorização necessária"}), 401

        token_session = auth_token.replace("Bearer ", "")

        #buscando user_id pelo Authorization
        user_id = UserSession.query.filter_by(session=token_session,valid=True).first()
        if not user_id:
            return jsonify({"error": "Sessão inválida ou expirada"}), 401
       
        session = UserSession.query.filter_by(user_id=user_id.user_id, session=token_session,valid=True).first()
       
        if not session:
            return jsonify({"error": "Sessão inválida ou expirada"}), 401

        return f(*args, **kwargs)  # Continua se autenticado

    return decorated_function