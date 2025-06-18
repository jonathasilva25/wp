# painel_usuarios.py
from flask import Flask, render_template_string, request, redirect
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

app = Flask(__name__)

TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Gerenciador de Usuários</title>
</head>
<body>
    <h2>Usuários</h2>
    <form method="POST" action="/add">
        Email: <input name="email" required>
        Senha: <input name="senha" type="password" required>
        Dias de Licença: <input name="dias" type="number" value="30" required>
        <button type="submit">Adicionar</button>
    </form>
    <br>
    <table border="1" cellpadding="5">
        <tr><th>Email</th><th>Expiração</th><th>Status</th><th>Ações</th></tr>
        {% for u in usuarios %}
        <tr>
            <td>{{ u['email'] }}</td>
            <td>{{ u['expiracao'] }}</td>
            <td>{{ 'Ativo' if u['ativo'] else 'Inativo' }}</td>
            <td>
                <a href="/toggle/{{ u['id'] }}">{{ 'Desativar' if u['ativo'] else 'Ativar' }}</a> |
                <a href="/delete/{{ u['id'] }}" onclick="return confirm('Confirma exclusão?')">Excluir</a>
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
'''

# Banco de dados compartilhado com servidor_licencas.py
def get_conexao():
    return sqlite3.connect("usuarios.db")

@app.route("/")
def home():
    conn = get_conexao()
    c = conn.cursor()
    c.execute("SELECT id, email, expiracao, ativo FROM usuarios")
    usuarios = [dict(id=row[0], email=row[1], expiracao=row[2], ativo=row[3]) for row in c.fetchall()]
    conn.close()
    return render_template_string(TEMPLATE, usuarios=usuarios)

@app.route("/add", methods=["POST"])
def add():
    email = request.form["email"]
    senha = request.form["senha"]
    dias = int(request.form["dias"])
    expiracao = (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")
    senha_hash = generate_password_hash(senha)
    conn = get_conexao()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO usuarios (email, senha_hash, expiracao) VALUES (?, ?, ?)", (email, senha_hash, expiracao))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()
    return redirect("/")

@app.route("/toggle/<int:uid>")
def toggle(uid):
    conn = get_conexao()
    c = conn.cursor()
    c.execute("UPDATE usuarios SET ativo = 1 - ativo WHERE id = ?", (uid,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete/<int:uid>")
def delete(uid):
    conn = get_conexao()
    c = conn.cursor()
    c.execute("DELETE FROM usuarios WHERE id = ?", (uid,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    import os
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))

