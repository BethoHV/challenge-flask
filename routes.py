from app import app
from flask import jsonify, redirect, render_template,request
import hashlib
from models import *

@app.route("/")
def home():
    return 'bem vindo'

# rota da pagina de login
@app.route("/login")
def loginPage():
    return render_template('login.html')

# endpoit para autenticar usuario
@app.route("/api/v1/login/", methods=['POST'])
def login():
    if request.method == 'POST':

        #pega as informações digitadas no formulario
        username = request.form.get('username')
        password = request.form.get('password')

        #verifica se usuario existe
        user = User.query.filter_by(username=username).first()

        if user:
            hashed_password = hashlib.md5(password.encode()).hexdigest() #criptografa senha do formulario para comparar com senha salva

            if user.password == hashed_password:
                return jsonify({"message": "Login realizado com sucesso!", "username": user.username})
            else:
                return jsonify({"error": "Senha inválidas"}), 401
        else:
            return jsonify({"error": "Usuario inválido"}), 401



# endpoit para adicionar ou editar usuario
@app.route("/api/v1/user/upsert/", methods=['POST'])
def upsertUser():

    #recebe os parametros via querystring
    username = request.args.get('username')
    password = request.args.get('password')
    fullname = request.args.get('fullname')
    active = request.args.get('active')
    
    #criptografa a senha
    hashed_password = hashlib.md5(password.encode()).hexdigest()

    #busca no banco se existe o usuario
    user = User.query.filter_by(username=username).first()
                
    if user:  #se existe, entao atualiza
        user.password = hashed_password
        user.fullname = fullname
        user.active = active
    else: #se nao existe, adiciona
        try:
            new_user = User(username=username, password=hashed_password, fullname=fullname)
            db.session.add(new_user)
        except:
            return "Erro ao criar usuario!"
    
    db.session.commit()
    return jsonify({"message": "Usuario criado/alterado com sucesso!", "username": user.username})
