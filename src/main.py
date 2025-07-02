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

# --- CONFIGURAÇÃO DA BASE DE DADOS PARA POSTGRESQL NO RENDER ---
# Esta é a configuração recomendada e robusta para produção.
# O Render fornece a URL da base de dados através de uma variável de ambiente.
DATABASE_URL = os.environ.get('DATABASE_URL')

# O SQLAlchemy espera 'postgresql://' em vez de 'postgres://' que o Render fornece.
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

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
