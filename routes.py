from app import app,redis_cache
from flask import flash, json, jsonify, redirect, render_template,request, url_for
import hashlib
from auth import auth_required
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

    if request.is_json:
        data = request.get_json()
    else:
        data = {
            'username': request.form.get('username'),
            'password': request.form.get('password')
        }

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Usuario e senha são obrigatórios"}), 400
        
    #pega as informações enviadar por json
    username = data['username']
    password = data['password']

    #verifica se usuario existe
    user = User.query.filter_by(username=username).first()

    if user:
         #criptografa senha do formulario para comparar com senha salva
        if user.password == hashlib.sha256(password.encode('utf-8')).hexdigest(): #compara senha salva com a senha digitada
            last_session = UserSession.query.filter_by(user_id=user.id).order_by(UserSession.created_at.desc()).first()
            if last_session:
                last_session.valid = False
                db.session.commit()
            new_session = UserSession(user_id=user.id,session = UserSession.generate_token(), valid=True)
            db.session.add(new_session)
            db.session.commit()

            response = jsonify({"message": "Login realizado com sucesso!", "session_token": new_session.session})
            response.status_code = 200
            response.headers['Location'] = url_for('home')  
            return response
        else:
            response = jsonify({"message": "Senha invalida"})
            response.status_code = 401
            response.headers['Location'] = url_for('login')  
            return response
    else:
        return jsonify({"error": "Usuario inválido"}), 401


############# endpoints categoria #############

# endpoit para adicionar ou editar usuario
@app.route("/api/v1/user/upsert/", methods=['POST'])
@auth_required
def upsertUser():

    #recebe os parametros via json
    if not request.is_json:
        return jsonify({"message": "Json não encontrado!"})
    data = request.get_json()
    
    username = data['username']
    password = data['password']
    fullname = data['fullname']
    active = data['active'] if 'active' in data else True

    #criptografa a senha
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

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
            return jsonify({"message": "Erro ao criar usuario!"})
    
    db.session.commit()
    return jsonify({"message": "Usuario criado/alterado com sucesso!"})

# endpoit listar usuarios
@app.route("/api/v1/user/list/", methods=['GET'])
@auth_required
def getUser():
    users = User.query.all()
    users_list = [
        {
            "id": user.id,
            "username": user.username,
            "fullname": user.fullname,
            "created_at": user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "active": user.active
        }
        for user in users
    ]
    
    return jsonify(users_list), 200

############# endpoints categoria #############

# endpoit para adicionar ou editar categoria
@app.route("/api/v1/category/upsert/", methods=['POST'])
@auth_required
def upsertCategory():

    #deleta cache da categoria
    redis_cache.delete('category:all')

    #recebe os parametros via json
    if not request.is_json:
        return jsonify({"message": "Json não encontrado!"})
    data = request.get_json()
    
    name = data['name']
    description = data['description']
    order = data['order']

    #busca no banco se existe o usuario
    category = Category.query.filter_by(name=name).first()
    
    if category:  #se existe, entao atualiza
        category.description = description
        category.order = order
    else: #se nao existe, adiciona
        try:
            new_category = Category(name=name,description=description, order=order)
            db.session.add(new_category)
        except:
            return "Erro ao criar categoria!"
    
    db.session.commit()
    return jsonify({"message": "Categoria criado/alterado com sucesso!"})


#endpoint para deletar categoria
@app.route("/api/v1/category/delete/<int:category_id>", methods=['POST'])
@auth_required
def deleteCategory(category_id):

     #deleta cache da categoria
    redis_cache.delete('category:all')

    category = Category.query.get(category_id)
    if not category:
         return jsonify({"error": "Categoria não encontrado"}), 404
    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message": f"Categoria com ID {category_id} deletado com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()  
        return jsonify({"error": f"Erro ao deletar o categoria: {str(e)}"}), 500
    

# endpoit para listar categorias
@app.route("/api/v1/category/list/", methods=['GET'])
def getCategories():

    #set o nome da key e o cache
    cache_key = 'category:all'
    cached_categories = redis_cache.get(cache_key)

    #se encontrar cache, retorna ele
    if cached_categories:
       return jsonify(json.loads(cached_categories)), 200

    #busca listagem de categoria, ordenado por nome e ordem
    categories = Category.query.order_by(Category.name,Category.order).all()

    #configura json para mostrar na resposta
    category_list = [
        {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "order": category.order,
            "created_at": category.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "deleted": category.deleted
        }
        for category in categories
    ]

    #salva json no cache
    redis_cache.set(
       cache_key,
       json.dumps(category_list),
       ex=300  # 5minutos
    )
    
    return jsonify(category_list), 200


############# endpoints produto #############

# endpoit para adicionar ou editar produtos
@app.route("/api/v1/product/upsert/", methods=['POST'])
@auth_required
def upsertProduct():

     #deleta cache do menu
    redis_cache.delete('menu:all')

    #recebe os parametros via json
    if not request.is_json:
        return jsonify({"message": "Json não encontrado!"})
    data = request.get_json()
    
    name = data['name']
    description = data['description']
    order = data['order']
    price = data['price']
    category_id = data['category_id']
    
    #busca no banco se existe o usuario
    product = Product.query.filter_by(name=name).first()
    
    if product:  #se existe, entao atualiza
        product.description = description
        product.order = order
        product.price = price
        product.category_id = category_id
    else: #se nao existe, adiciona
        try:
            new_product = Product(name=name,description=description,order=order,price=price,category_id=category_id)
            db.session.add(new_product)
        except:
            return "Erro ao criar produto!"
    
    
    db.session.commit()
    return jsonify({"message": "Produto criado/alterado com sucesso!"})

#endpoint para deletar categoria
@app.route("/api/v1/product/delete/<int:product_id>", methods=['POST'])
@auth_required
def deletProduct(product_id):
    product = Category.query.get(product_id)
    
    if not product:
         return jsonify({"error": "Produto não encontrado"}), 404
    
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": f"Produto com ID {product_id} deletado com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()  
        return jsonify({"error": f"Erro ao deletar o produto: {str(e)}"}), 500
    
# endpoit para listar categorias
@app.route("/api/v1/product/list/", methods=['GET'])
def getProducts():
    products = Product.query.order_by(Product.name,Product.order).all()
    product_list = [
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "order": product.order,
            "price": product.price,
            "category_id": product.category_id,
            "deleted": product.deleted
        }
        for product in products
    ]
    
    return jsonify(product_list), 200



#endpot para listar menu
@app.route("/api/v1/menu/list/", methods=['GET'])
def getMenu():

    #set cache_key e busca o cache do redis se existir
    cache_key = 'menu:all'
    cached_menu = redis_cache.get(cache_key)

    if cached_menu:
       return jsonify(json.loads(cached_menu)), 200

    menus = Product.query.join(Category).order_by(Product.name, Product.order).all()
    menu_list = [
    {
        "id": menu.id,
        "name": menu.name,
        "description": menu.description,
        "order": menu.order,
        "price": menu.price,
        "category_id": menu.category_id,
        "category_name": menu.category.name,
        "deleted": menu.deleted
    }
    for menu in menus
]
    
    redis_cache.set(
        cache_key,
        json.dumps(menu_list),
        ex=300  # 5minutos
    )

    return jsonify(menu_list), 200