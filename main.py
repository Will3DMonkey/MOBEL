import os
from flask import Flask, send_from_directory
from flask_cors import CORS

# --- ALTERAÇÃO CRÍTICA: Imports Corrigidos para a Estrutura 'src' ---
# Como todo o nosso código está dentro do pacote 'src', todos os imports
# locais devem começar com 'src.'.
from src.models.user import db
from src.models.data_models import DataSource, CollectedData, BusinessOpportunity, CollectionLog
from src.routes.user import user_bp
from src.routes.data_routes import data_bp
from src.routes.analysis_routes import analysis_bp
from src.routes.reports_routes import reports_bp

# A variável 'app' precisa de ser reconhecida pelo Gunicorn.
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Habilitar CORS para todas as rotas
CORS(app)

# Registar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(data_bp, url_prefix='/api/data')
app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
app.register_blueprint(reports_bp, url_prefix='/api/reports')

# Configuração do banco de dados
# ATENÇÃO: O banco de dados SQLite será APAGADO a cada deploy no Render.
# Para produção, use o serviço de PostgreSQL do Render.
db_path = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(db_path, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(db_path, 'app.db')}"
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
            return "index.html não encontrado na pasta static. Verifique o build do seu front-end.", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
