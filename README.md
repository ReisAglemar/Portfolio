# 💼 Portfólio Pessoal – v2.0

Site desenvolvido com **HTML semântico, CSS modular e JavaScript puro**, com abordagem **mobile-first**, hospedado em servidor próprio e com um **serviço de contato próprio** que envia e-mails pela API do **Resend**.

O projeto demonstra fundamentos sólidos de frontend, organização estrutural e a passagem para full stack: além do site estático, inclui um pequeno backend em Python, o deploy em Apache com Docker e a configuração do servidor.

🌐 **Online:** https://arreis.com.br

---

## 🚀 Objetivo do Projeto

Este portfólio foi desenvolvido para:

- Demonstrar domínio de **HTML semântico**
- Aplicar **CSS moderno (Grid e Flexbox)** de forma modular
- Estruturar layout com abordagem **mobile-first**
- Usar **JavaScript puro** para interações sem depender de frameworks
- Construir e operar o próprio **backend de contato**, sem serviço de formulário de terceiros
- Publicar e manter tudo em **infraestrutura própria**

---

## 📂 Estrutura do Projeto

```
.
├── index.html            # Página principal (capa, conhecimentos, projetos, contato)
├── agora.html            # Página "Agora": homelab e servidor real
├── notas.html            # Índice das Notas de Campo
├── nota-01.html          # Artigo: O abismo entre o teste e a produção
├── nota-02.html          # Artigo: A cabeça de quem constrói e a de quem mantém
├── style/                # CSS modular
├── js/main.js            # Interações da interface
├── img/                  # Imagens otimizadas (WebP)
├── contato/              # Serviço de contato (Python + Resend)
└── .htaccess             # Regras de segurança do Apache
```

---

## 🧱 Estrutura Técnica

### ✔ HTML

- Tags semânticas: `header`, `main`, `section`, `nav`, `figure`, `footer`
- Hierarquia correta de títulos (`h1` único por página)
- Imagens com `alt`, `width`, `height` e `loading="lazy"`
- Separação lógica entre capa, conhecimentos, projetos e contato

### 🎨 CSS

Organizado de forma modular. O `main.css` importa os demais, e cada página específica tem o seu arquivo:

```
style/
├── reset.css
├── variaveis.css          # paleta, tipografia e breakpoints (:root)
├── layout.css
├── componentes.css
├── animacoes.css
├── main.css               # importa os demais
├── responsivo768px.css
├── responsivo1024px.css
├── agora.css              # página Agora
└── notas.css              # páginas de Notas
```

Aplicações técnicas:

- Arquitetura **mobile-first**
- CSS Grid para estrutura global e Flexbox para alinhamentos internos
- Variáveis CSS para paleta de cores, tipografia e breakpoints
- Componentes reutilizáveis (cards, botões, formulário)
- Animações e transições suaves

### ⚙️ JavaScript

Tudo em `js/main.js`, sem bibliotecas:

- **Scroll reveal** com `IntersectionObserver`
- **Header** com efeito de vidro ao rolar a página
- **ScrollSpy**: destaca no menu a seção visível
- Botão flutuante de **voltar ao topo**
- **Formulário de contato** via `fetch`, com estado de envio, mensagem de sucesso ou erro e sem recarregar a página

### 🖼️ Imagens

As imagens são servidas em **WebP**, redimensionadas para o tamanho de exibição (com margem para telas 2x). Isso reduziu o peso de ~27 MB para menos de 1 MB.

Os originais ficam fora do versionamento (`img-src/`, ignorado pelo git) e podem ser recuperados do histórico do repositório. Para gerar uma imagem nova:

```bash
cwebp -q 80 -m 6 -resize 900 900 original.png -o img/nome.webp
```

---

## 📱 Responsividade

- Base estruturada para mobile, com ajustes em `768px` e `1024px`
- Elementos com classe `.desktop` ocultos em telas menores
- Imagens com dimensões declaradas, evitando deslocamento de layout

---

## 📄 Páginas

### 🎖️ Conhecimentos

Apresentação técnica das habilidades em HTML, CSS, JavaScript, Java, Git e Linux.

### 📚 Projetos

- **Super Trunfo (Java – Console)**
- **Garage Database (Spring + JPA + IA generativa)**
- **Portfólio Pessoal** (este projeto)
- **Script de Automação Linux**

Cada projeto apresenta contexto, problema resolvido, decisões técnicas, arquitetura aplicada e link para o repositório.

### 📍 Agora (/now & Homelab)

Página dedicada a registrar a implementação real de infraestrutura e servidor doméstico (**Homelab**), baseada no documento `/srv/documentation/decisoes.md`:

- **Hardware & SO**: Lenovo ThinkPad L14 Gen 2 (Intel Core i7-1185G7), Ubuntu Server 26.04 LTS (governor *performance*, suspensão/tampa desabilitadas).
- **Acesso & VPN**: **WireGuard** (`wg0` na rede privada `10.0.0.0/24`) como método mandatório de acesso remoto externo.
- **Hardening & Firewall (UFW)**: política padrão *DROP Incoming*, `51820/udp` (WireGuard) e web (80/443) restrita à Cloudflare, SSH exclusivo por chave pública, Cockpit (9090 HTTPS) restrito a LAN/VPN.
- **Estrutura `/srv` & Docker**: containers com Docker Compose, Portainer (9443 HTTPS), Apache (self-hosting do site) e Samba (445 exclusivo LAN para backup de fotos da família).
- **Armazenamento**: HDA (produção), HDB (backup), RAID no SO e isolamento de permissões (root vs sysadmin).

### ✍️ Notas de Campo

Artigos curtos sobre a prática de construir e manter sistemas, com índice em `notas.html`.

### 📤 Contato

Formulário que envia mensagens por e-mail através de um serviço próprio. Detalhes na seção a seguir.

---

## 📬 Serviço de Contato

O formulário não usa serviço de terceiros para formulários. Ele envia para um pequeno backend em **Python** (somente biblioteca padrão, sem dependências) que dispara o e-mail pela API do **Resend**.

```
formulário ──fetch──▶ Cloudflare ──▶ Apache (Docker) ──ProxyPass /api/contato──▶ serviço Python ──▶ Resend ──▶ e-mail
```

A chave da API não pode ficar no front-end, por isso ela vive só no servidor, em um arquivo `.env` que não é versionado.

### Proteções

- Validação de nome, e-mail e mensagem, com limites de tamanho
- **Honeypot**: campo oculto que só bots preenchem
- **Rate limit** por IP (3 envios a cada 10 minutos), lendo o IP real do visitante em `CF-Connecting-IP`
- Conteúdo da mensagem escapado antes de entrar no HTML do e-mail
- E-mail enviado com `reply-to` do visitante, para responder direto
- Serviço escutando apenas na interface interna do Docker, fora da internet
- Executado por um **usuário de sistema dedicado** (`contato`), sem login, sob `systemd` com `NoNewPrivileges`, `ProtectSystem=strict` e `ProtectHome`

### Arquivos (`contato/`)

| Arquivo | Função |
|---|---|
| `servidor.py` | Serviço HTTP: valida, limita e envia o e-mail |
| `contato.service` | Unidade do systemd |
| `apache.conf` | Trecho do `ProxyPass` para o vhost |
| `.env.example` | Modelo das variáveis de ambiente |

### Variáveis de ambiente

Copie `.env.example` para `.env` (o `.env` real nunca vai para o git):

| Variável | Descrição |
|---|---|
| `API_KEY_RESEND` | Chave da API do Resend |
| `EMAIL_REMETENTE` | Endereço do domínio verificado no Resend |
| `EMAIL_DESTINATARIO` | Caixa que recebe as mensagens |
| `PORTA` | Porta do serviço (padrão `8787`) |
| `HOST` | Interface de escuta (`127.0.0.1` local; gateway da rede Docker no servidor) |

---

## 🧪 Rodando Localmente

Para ver apenas o site, abra o `index.html` no navegador. O formulário não envia sem o serviço de contato.

Para testar o site com o envio de e-mail:

```bash
cd contato
cp .env.example .env        # preencha API_KEY_RESEND e os e-mails; use HOST=127.0.0.1
SERVIR_SITE=1 python3 servidor.py
```

Acesse **http://127.0.0.1:8787/**. Com `SERVIR_SITE=1` o serviço também entrega os arquivos do site (exceto a pasta `contato/`), o que dispensa o Apache. Em produção essa variável não deve ser usada.

---

## 🚢 Deploy

O site é servido pelo **Apache em Docker** (vários sites por *virtual host*), atrás da **Cloudflare**, e o serviço de contato roda no host via **systemd**.

1. Copiar os arquivos do site para a pasta do vhost, sem `contato/`, `.git` e `img-src/`
2. Instalar o serviço em `/opt/contato/` com o `.env` (permissão `600`) e habilitar o `contato.service`
3. Adicionar o `ProxyPass` de `contato/apache.conf` ao vhost, com `mod_proxy` e `mod_proxy_http` ativos
4. Liberar no firewall a origem da rede Docker para a porta do serviço
5. Validar (`httpd -t`) e recarregar o Apache

O `.htaccess` bloqueia listagem de diretórios, arquivos ocultos, extensões sensíveis (`.env`, `.py`, `.service`, `.conf`, `.sql`, `.log`, `.sh`), o `.git` e a pasta `contato/`. Ele exige `AllowOverride` liberado no vhost.

---

## 🧠 Decisões Técnicas Importantes

- Separação clara entre conteúdo, estilo e comportamento
- Sistema visual baseado em variáveis CSS
- Backend de contato mínimo, sem dependências, para reduzir a superfície de ataque e a manutenção
- Segredos fora do repositório; o `.env.example` traz só valores fictícios
- Imagens otimizadas para reduzir o tempo de carregamento
- Infraestrutura própria, documentada na página Agora

---

## 🔮 Próximas Versões (Roadmap)

- Integração com PostgreSQL
- Backend em Java (Spring Boot) ou Node.js para o conteúdo dinâmico
- Sistema de artigos dinâmicos, hoje escritos em HTML
- Autenticação para área administrativa
- Conteúdo persistido em banco de dados
- Transformação para aplicação Full Stack

---

## 🛠 Tecnologias Utilizadas

- HTML5, CSS3 e JavaScript (ES6+)
- Python 3 (biblioteca padrão)
- Resend (envio de e-mail)
- Apache HTTP Server, Docker e Docker Compose
- Cloudflare (DNS e proxy)
- systemd e UFW
- Git e GitHub

---

## 📌 Versão

**v2.0 – Site estático com serviço de contato próprio, imagens otimizadas e deploy em infraestrutura própria**

---

## 👤 Autor

**Aglemar Reis**  
Estudante de Engenharia de Software  
Foco em Backend Java e Administração de Sistemas  

GitHub: https://github.com/ReisAglemar  
LinkedIn: https://www.linkedin.com/in/aglemarreis/
