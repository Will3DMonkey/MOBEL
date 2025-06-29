import os
from flask import Flask, send_from_directory
from flask_cors import CORS

# --- IMPORTS CORRIGIDOS PARA ESTRUTURA SEM 'src' ---
# Os imports agora são diretos, pois tudo está na raiz.
from models.user import db
from models.data_models import DataSource, CollectedData, BusinessOpportunity, CollectionLog
from routes.user import user_bp
from routes.data_routes import data_bp
from routes.analysis_routes import analysis_bp
from routes.reports_routes import reports_bp

# A variável 'app' precisa ser reconhecida pelo Gunicorn.
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Habilitar CORS para todas as rotas
CORS(app)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(data_bp, url_prefix='/api/data')
app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
app.register_blueprint(reports_bp, url_prefix='/api/reports')

# Configuração do banco de dados
# ATENÇÃO: O banco de dados SQLite será APAGADO a cada deploy no Render.
os.makedirs('database', exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///database/app.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Cria as tabelas do banco de dados se não existirem
with app.app_context():
    db.create_all()

# Rota para servir o Front-end
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
    app.run(host='0.0
