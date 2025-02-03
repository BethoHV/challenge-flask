#Commands

instale, crie e rode o ambiente virtual venv

```bash
    sudo apt install python3.10-venv            
    python3 -m venv .venv 
    . .venv/bin/activate                      
```

instale as dependencias: flask, SQLAlchemy, redis

```bash
    pip install Flask
    pip install -U Flask-SQLAlchemy
    pip install flask-redis
```

inicie o projeto e o redis

```bash
    flask --app app run
    redis-cli
```

instalar e abrir banco sqlite

```bash
    sudo apt install sqlite3
    sqlite3 instace/challenge.db
```