from flask import Blueprint, jsonify

# Cria um 'blueprint'. É como um mini-aplicativo para organizar as rotas.
user_bp = Blueprint('user_bp', __name__)

# Exemplo de uma rota de utilizador
@user_bp.route('/users', methods=['GET'])
def get_users():
    # Aqui viria a lógica para buscar utilizadores na base de dados
    return jsonify({"message": "Rota de utilizadores a funcionar"})
