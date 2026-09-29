"""
Serviço de contato do portfólio.

Recebe o POST do formulário (JSON) em /api/contato, valida os campos e envia o
e-mail via API do Resend. Usa somente a biblioteca padrão do Python.

Deve rodar atrás do Apache (ProxyPass), nunca exposto à internet.
Variáveis lidas do arquivo .env (fora do repositório):
    API_KEY_RESEND, EMAIL_REMETENTE, EMAIL_DESTINATARIO, PORTA e HOST (opcionais;
    HOST padrão 127.0.0.1, use o IP da bridge do Docker se o Apache roda em container)
Para testar localmente sem o Apache: SERVIR_SITE=1 python3 servidor.py
e abrir http://127.0.0.1:8787/ (também serve o site, exceto a pasta contato/).
"""

import json
import mimetypes
import os
import re
import time
import urllib.request
from collections import defaultdict, deque
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DIRETORIO = Path(__file__).resolve().parent
ROTA = "/api/contato"
URL_RESEND = "https://api.resend.com/emails"

MAX_NOME = 100
MAX_EMAIL = 254
MAX_MENSAGEM = 5000
MAX_CORPO_BYTES = 16 * 1024

# Rate limit por IP: no máximo LIMITE envios a cada JANELA segundos
LIMITE = 3
JANELA = 600
envios = defaultdict(deque)

REGEX_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def carregarEnvs():
    caminho = DIRETORIO / ".env"
    if not caminho.is_file():
        raise RuntimeError(f"Arquivo .env não encontrado em {caminho}")
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))


def limiteExcedido(ip):
    agora = time.monotonic()
    fila = envios[ip]
    while fila and agora - fila[0] > JANELA:
        fila.popleft()
    if len(fila) >= LIMITE:
        return True
    fila.append(agora)
    return False


def enviarEmail(nome, email, mensagem):
    html = (
        "<h2>Nova mensagem pelo portfólio</h2>"
        f"<p><b>Nome:</b> {escape(nome)}<br><b>Email:</b> {escape(email)}</p>"
        f"<p style=\"white-space:pre-wrap\">{escape(mensagem)}</p>"
    )
    corpo = {
        "from": os.environ["EMAIL_REMETENTE"],
        "to": os.environ["EMAIL_DESTINATARIO"],
        "reply_to": email,
        "subject": f"Contato do portfólio: {nome}"[:150],
        "html": html,
        "text": f"Nome: {nome}\nEmail: {email}\n\n{mensagem}",
    }
    requisicao = urllib.request.Request(
        URL_RESEND,
        data=json.dumps(corpo).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {os.environ['API_KEY_RESEND']}",
            "Content-Type": "application/json",
            # Evita bloqueio 403 do WAF da Cloudflare a clientes sem User-Agent
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) portfolio-contato/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(requisicao, timeout=10):
        return


class Handler(BaseHTTPRequestHandler):
    server_version = "contato"

    def responder(self, codigo, mensagem):
        dados = json.dumps({"mensagem": mensagem}).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def do_POST(self):
        if self.path != ROTA:
            return self.responder(404, "Não encontrado.")

        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            tamanho = 0
        if tamanho <= 0 or tamanho > MAX_CORPO_BYTES:
            return self.responder(400, "Requisição inválida.")

        try:
            dados = json.loads(self.rfile.read(tamanho))
            nome = str(dados.get("name", "")).strip()
            email = str(dados.get("email", "")).strip()
            mensagem = str(dados.get("assunto", "")).strip()
            armadilha = str(dados.get("website", "")).strip()
        except (ValueError, AttributeError):
            return self.responder(400, "Requisição inválida.")

        # Honeypot: campo oculto que só bots preenchem. Finge sucesso.
        if armadilha:
            return self.responder(200, "Mensagem enviada!")

        if (not nome or len(nome) > MAX_NOME
                or not REGEX_EMAIL.match(email) or len(email) > MAX_EMAIL
                or not mensagem or len(mensagem) > MAX_MENSAGEM):
            return self.responder(400, "Confira os campos e tente novamente.")

        # IP do visitante. Em produção o site fica atrás da Cloudflare e o
        # firewall só deixa a Cloudflare chegar ao Apache, então
        # CF-Connecting-IP é confiável (ela o sobrescreve). Sem ele (testes
        # locais), usa a última entrada de X-Forwarded-For, a acrescentada
        # pelo Apache; as anteriores podem ser forjadas pelo visitante.
        ip = (self.headers.get("CF-Connecting-IP")
              or (self.headers.get("X-Forwarded-For") or self.client_address[0]).split(",")[-1]).strip()
        if limiteExcedido(ip):
            return self.responder(429, "Muitas mensagens. Tente novamente mais tarde.")

        try:
            enviarEmail(nome, email, mensagem)
        except Exception as erro:
            self.log_error("Falha ao enviar e-mail: %s", erro)
            return self.responder(502, "Não foi possível enviar agora. Tente mais tarde.")

        self.responder(200, "Mensagem enviada!")

    def do_GET(self):
        # Modo de desenvolvimento: serve o site para testar sem o Apache
        if not os.environ.get("SERVIR_SITE"):
            return self.responder(405, "Método não permitido.")

        raiz = DIRETORIO.parent.resolve()
        caminho = self.path.split("?", 1)[0]
        alvo = (raiz / caminho.lstrip("/")).resolve()
        if alvo.is_dir():
            alvo = alvo / "index.html"
        bloqueado = alvo == DIRETORIO or DIRETORIO in alvo.parents
        if raiz not in alvo.parents and alvo != raiz or bloqueado or not alvo.is_file():
            return self.responder(404, "Não encontrado.")

        tipo = mimetypes.guess_type(alvo.name)[0] or "application/octet-stream"
        dados = alvo.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def log_message(self, formato, *args):
        # Não registra conteúdo das mensagens, apenas eventos
        print(f"{self.log_date_time_string()} {formato % args}", flush=True)


if __name__ == "__main__":
    carregarEnvs()
    porta = int(os.environ.get("PORTA", "8787"))
    host = os.environ.get("HOST", "127.0.0.1")
    print(f"Serviço de contato em {host}:{porta}", flush=True)
    ThreadingHTTPServer((host, porta), Handler).serve_forever()
