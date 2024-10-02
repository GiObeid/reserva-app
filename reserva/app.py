from flask import Flask, render_template, redirect, url_for, request
import uuid

app = Flask(__name__)

def cadastrar_sala(s):
    sala_id = str(uuid.uuid4())
    linha = f"{sala_id},{s['tipo']},{s['capacidade']},{s['descricao']},Sim\n"
    with open("salas.csv", "a") as file:
        file.write(linha)

def carregar_salas():
    salas = []
    with open("salas.csv", "r") as file:
        for linha in file:
            sala_id, tipo, capacidade, descricao, ativa = linha.strip().split(",")
            sala = {
                "id": sala_id,
                "tipo": tipo,
                "capacidade": capacidade,
                "descricao": descricao,
                "ativa": ativa
            }
            salas.append(sala)
    return sorted(salas, key=lambda x: x['tipo'])  # Ordena por tipo

def carregar_usuarios():
    usuarios = []
    with open("usuarios.csv", "r") as file:
        for linha in file:
            nome, email, password = linha.strip().split(",")
            usuario = {
                "nome": nome,
                "email": email,
                "password": password
            }
            usuarios.append(usuario)
    return sorted(usuarios, key=lambda u: u['email'])  # Ordena por email

def busca_binaria(lista, chave, chave_ordenacao):
    baixo = 0
    alto = len(lista) - 1
    
    while baixo <= alto:
        meio = (baixo + alto) // 2
        if lista[meio][chave_ordenacao] == chave:
            return meio  # Retorna o índice se encontrado
        elif lista[meio][chave_ordenacao] < chave:
            baixo = meio + 1
        else:
            alto = meio - 1
            
    return -1  # Retorna -1 se não encontrado

def usuario_existe(email):
    usuarios = carregar_usuarios()
    return busca_binaria(usuarios, email, 'email') != -1

def sala_existe(tipo):
    salas = carregar_salas()
    return busca_binaria(salas, tipo, 'tipo') != -1

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        password = request.form.get("password")

        if usuario_existe(email):
            return "Usuário já existe", 400
        
        cadastrar_usuario({"nome": nome, "email": email, "password": password})
        return redirect(url_for("index"))
    return render_template("cadastro.html")

@app.route("/gerenciar/lista-salas")
def lista_salas():
    salas = carregar_salas()
    return render_template("listar-salas.html", salas=salas)

@app.route("/gerenciar/cadastrar-salas", methods=["GET", "POST"])
def cadastrar_salas():
    if request.method == "POST":
        tipo = request.form.get("tipo")
        capacidade = request.form.get("capacidade")
        descricao = request.form.get("descricao")

        if sala_existe(tipo):
            return "Sala já existe", 400
        
        cadastrar_sala({"tipo": tipo, "capacidade": capacidade, "descricao": descricao})
        return redirect(url_for("lista_salas"))
    return render_template("cadastrar-sala.html")

@app.route("/gerenciar/excluir-sala/<sala_id>", methods=["POST"])
def excluir_sala(sala_id):
    salas = carregar_salas()
    salas = [sala for sala in salas if sala["id"] != sala_id]
    
    with open("salas.csv", "w") as file:
        for sala in salas:
            linha = f"{sala['id']},{sala['tipo']},{sala['capacidade']},{sala['descricao']},{sala['ativa']}\n"
            file.write(linha)
    
    return redirect(url_for("lista_salas"))

@app.route("/gerenciar/desativar-sala/<sala_id>", methods=["POST"])
def desativar_sala(sala_id):
    salas = carregar_salas()
    for sala in salas:
        if sala["id"] == sala_id:
            sala["ativa"] = "Não" if sala["ativa"] == "Sim" else "Sim"
    
    with open("salas.csv", "w") as file:
        for sala in salas:
            linha = f"{sala['id']},{sala['tipo']},{sala['capacidade']},{sala['descricao']},{sala['ativa']}\n"
            file.write(linha)
    
    return redirect(url_for("lista_salas"))

@app.route("/reservas")
def reservas():
    return render_template("reservas.html")

@app.route("/detalhe-reserva")
def detalhe_reserva():
    return render_template("detalhe_reserva.html")

@app.route("/reservar")
def reservar_sala():
    return render_template("reservar-sala.html")

def cadastrar_usuario(u):
    linha = f"{u['nome']},{u['email']},{u['password']}\n"
    with open("usuarios.csv", "a") as file:
        file.write(linha)

def validar_usuario(email, password):
    usuarios = carregar_usuarios()
    index = busca_binaria(usuarios, email, 'email')
    if index != -1 and usuarios[index]['password'] == password:
        return True
    return False

if __name__ == "__main__":
    app.run(debug=True)
