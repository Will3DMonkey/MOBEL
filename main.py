import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Importar blueprints diretamente, sem o prefixo 'src.'
# Assumindo que user_routes.py, data_routes.py, analysis_routes.py, reports_routes.py estão na pasta 'routes'
from routes.user_routes import user_bp
from routes.data_routes import data_bp
from routes.analysis_routes import analysis_bp
from routes.reports_routes import reports_bp

# Importar db diretamente, sem o prefixo 'src.'
# Assumindo que db é inicializado em models/data_models.py ou models/user.py
# Vou assumir que db é inicializado em models/data_models.py como no protótipo original
from models.data_models import db

app = Flask(__name__)
CORS(app) # Habilitar CORS para todas as rotas

# Configuração do banco de dados (SQLite para protótipo)
# Render pode precisar de uma variável de ambiente para o DB, como DATABASE_URL
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///site.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix="/api")
app.register_blueprint(data_bp, url_prefix="/api/data")
app.register_blueprint(analysis_bp, url_prefix="/api/analysis")
app.register_blueprint(reports_bp, url_prefix="/api/reports")

@app.route("/")
def home():
    return "API do Mapa de Oportunidade por Bairro está online!"

if __name__ == "__main__":
    with app.app_context():
        db.create_all() # Cria as tabelas do banco de dados
    # Usar a porta fornecida pelo ambiente (Render) ou 5000 como fallback
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
