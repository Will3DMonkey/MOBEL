import os
from flask import Flask, send_from_directory
from flask_cors import CORS

# --- IMPORTS PARA ESTRUTURA COMPLETAMENTE PLANA ---
# Este código assume que TODOS os ficheiros .py estão na raiz do projeto,
# conforme a sua última imagem.

# Assumindo que 'db' e os modelos de dados estão em 'data_models.py'.
# Se 'db' estiver noutro ficheiro, terá de ajustar este import.
from data_models import db, DataSource, CollectedData, BusinessOpportunity, CollectionLog

# Importando os blueprints dos ficheiros de rotas existentes.
from data_routes import data_bp
from analysis_routes import analysis_bp
from reports_routes import reports_bp

# ATENÇÃO: O 'user_bp' não foi importado porque não encontrei um ficheiro
# 'user.py' ou 'user_routes.py' na sua imagem. Se este ficheiro existir,
# adicione o import correspondente (ex: from user_routes import user_bp)
# e descomente a linha de registo do blueprint abaixo.

# O 'static_folder' aponta para a pasta 'static' na raiz.
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Habilitar CORS para todas as rotas
CORS(app)

# Registar blueprints
# app.register_blueprint(user_bp, url_prefix='/api') # Descomente se tiver o user_bp
app.register_blueprint(data_bp, url_prefix='/api/data')
app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
app.register_blueprint(reports_bp, url_prefix='/api/reports')

# Configuração do banco de dados
# O caminho está correto para criar a pasta 'database' na raiz.
# ATENÇÃO: O banco de dados SQLite será APAGADO a cada deploy no Render.
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
