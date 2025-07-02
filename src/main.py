import os
from flask import Flask, send_from_directory
from flask_cors import CORS

# --- IMPORTS PARA ESTRUTURA COM 'SRC' ---
from .models.user import db
from .models.data_models import DataSource, CollectedData, BusinessOpportunity, CollectionLog
from .routes.user import user_bp
from .routes.data_routes import data_bp
from .routes.analysis_routes import analysis_bp
from .routes.reports_routes import reports_bp

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(data_bp, url_prefix='/api/data')
app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
app.register_blueprint(reports_bp, url_prefix='/api/reports')

# --- CONFIGURAÇÃO DA BASE DE DADOS PARA POSTGRESQL (COM DEPURAÇÃO ROBUSTA) ---
DATABASE_URL = os.environ.get('DATABASE_URL')

# Passo 1: Imprimir o valor bruto que recebemos do Render
print(f"--- DEBUG PASSO 1: Valor bruto de DATABASE_URL recebido: '{DATABASE_URL}'")

# Passo 2: Validar se a variável existe e não está vazia
if not DATABASE_URL or not DATABASE_URL.strip():
    raise ValueError("ERRO CRÍTICO: A variável de ambiente 'DATABASE_URL' não foi encontrada ou está vazia. Verifique a configuração no Render.")

# Passo 3: Corrigir o prefixo da URL se necessário
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print(f"--- DEBUG PASSO 2: URL corrigida para: '{DATABASE_URL}'")

# Passo 4: Aplicar a configuração ao Flask
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print("--- DEBUG PASSO 3: Configuração da base de dados aplicada. A tentar inicializar db.init_app(app)...")

# Inicializar a base de dados
db.init_app(app)

print("--- DEBUG PASSO 4: db.init_app(app) concluído com sucesso.")


with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        index_path = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(app.static_folder, 'index.html')
        else:
            return "index.html não encontrado na pasta static.", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
