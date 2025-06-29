# Dentro do arquivo: src/models/user.py

from flask_sqlalchemy import SQLAlchemy

# Esta é a linha que define o 'db' que seu main.py tenta importar.
# Ele será inicializado no main.py com a configuração do app.
db = SQLAlchemy()
