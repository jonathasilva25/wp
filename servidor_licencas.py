# servidor_licencas.py
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# ======== BANCO DE DADOS ==============
def init_db():
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    senha_hash TEXT NOT NULL,
                    ativo INTEGER DEFAULT 1,
                    expiracao TEXT DEFAULT NULL
                )''')
    conn.commit()
    conn.close()

def criar_usuario(email, senha, dias_validade=30):
    senha_hash = generate_password_hash(senha)
    expiracao = (datetime.now() + timedelta(days=dias_validade)).strftime("%Y-%m-%d")
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO usuarios (email, senha_hash, expiracao) VALUES (?, ?, ?)",
                  (email, senha_hash, expiracao))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Usuário já existe.")
    conn.close()

# ======== API ENDPOINTS ==============
@app.route("/login", methods=["POST"])
def login():
    dados = request.json
    email = dados.get("email")
    senha = dados.get("senha")

    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT senha_hash, ativo, expiracao FROM usuarios WHERE email = ?", (email,))
    resultado = c.fetchone()
    conn.close()

    if not resultado:
        return jsonify({"status": "erro", "mensagem": "Usuário não encontrado."}), 404

    senha_hash, ativo, expiracao = resultado

    if not check_password_hash(senha_hash, senha):
        return jsonify({"status": "erro", "mensagem": "Senha incorreta."}), 401

    if not ativo:
        return jsonify({"status": "erro", "mensagem": "Usuário desativado."}), 403

    if expiracao and datetime.strptime(expiracao, "%Y-%m-%d") < datetime.now():
        return jsonify({"status": "expirado", "mensagem": "Licença expirada."}), 403

    return jsonify({"status": "ok", "mensagem": "Login autorizado."}), 200

# ======== INICIALIZAÇÃO ==============
if __name__ == "__main__":
    init_db()
    # Exemplo de criação manual de usuário:
    # criar_usuario("cliente1@teste.com", "123456", dias_validade=15)
    app.run(host="0.0.0.0", port=5000, debug=True)
