# Este arquivo substitui o conteúdo de clinica/views.py.
# Agora o chatbot consulta o banco (serviços, horários e dúvidas) em vez de usar texto fixo.

import json                              # lê o corpo da requisição (a mensagem vem em JSON)
import re                                # expressões regulares: separam o texto em palavras
import unicodedata                       # remove acentos para comparar textos ("hidratação" = "hidratacao")

from django.http import JsonResponse     # devolve a resposta do chatbot em formato JSON
from django.views.decorators.http import require_POST   # só aceita envio de mensagem (POST)

# Reaproveita os dados de contato e o link do WhatsApp que o site já usa
from site_app.views import CONTATO, WHATSAPP_URL

# Tabelas do banco que o chatbot consulta
from .models import Servico, HorarioFuncionamento, DuvidasFrequente


# ---------------------------------------------------------------------------
# Textos fixos do chatbot
# ---------------------------------------------------------------------------

# Menu de boas-vindas (o mesmo texto que o chat já mostrava)
MENU = "Olá! Como posso ajudar? Digite 1 (Serviços), 2 (Horários) ou 3 (Contatos)."

# Resposta quando o chatbot não entende a mensagem: mostra o menu e o WhatsApp
FALLBACK = (
    "Desculpe, não entendi a sua mensagem. "
    "Digite 1 (Serviços), 2 (Horários) ou 3 (Contatos), "
    f"ou fale com a gente pelo WhatsApp: {WHATSAPP_URL}"
)

# Palavras que o chatbot reconhece (já sem acento e em minúsculas)
SAUDACOES = {"oi", "ola", "menu", "ajuda", "inicio", "bom", "boa", "hey", "opa"}
PALAVRAS_AGENDAR = {"agendar", "agendamento", "marcar", "marcacao", "reservar", "consulta"}
PALAVRAS_HORARIO = {"horario", "horarios", "funcionamento", "abre", "fecha", "aberto", "atendimento"}
PALAVRAS_CONTATO = {"contato", "contatos", "telefone", "endereco", "whatsapp", "email"}
PALAVRAS_PRECO = {"preco", "precos", "quanto", "custa", "valor", "valores", "servicos", "servico"}

# Palavras comuns que não ajudam a achar uma dúvida (artigos, preposições etc.)
STOPWORDS = {
    "que", "quais", "qual", "como", "para", "por", "com", "uma", "uns", "dos", "das", "nos",
    "nas", "aos", "sao", "tem", "ter", "ser", "mais", "mas", "foi", "pra", "isso", "esse",
    "essa", "meu", "minha", "voce", "seu", "sua", "ele", "ela", "onde", "quando", "quero",
    "gostaria", "saber", "favor", "pode", "posso", "podem", "depois", "sobre", "ate", "tambem",
}


# ---------------------------------------------------------------------------
# Funções de apoio (cada uma faz uma coisa pequena)
# ---------------------------------------------------------------------------

def normalizar(texto):
    """Põe o texto em minúsculas e tira os acentos, para comparar sem erro."""
    # NFD separa a letra do acento ("ç" vira "c" + cedilha)
    decomposto = unicodedata.normalize("NFD", texto.lower())
    # Mantém só os caracteres que não são acentos
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def palavras_de(texto_normalizado):
    """Separa o texto em um conjunto de palavras (sem repetir)."""
    return set(re.findall(r"[a-z0-9]+", texto_normalizado))


def palavras_chave(texto_normalizado):
    """Palavras importantes do texto: tira as comuns e as muito curtas, e tira o 's' do plural."""
    chaves = set()
    for palavra in re.findall(r"[a-z0-9]+", texto_normalizado):
        if len(palavra) < 3 or palavra in STOPWORDS:
            continue                                   # ignora palavra comum ou curta
        if palavra.endswith("s") and len(palavra) > 3:
            palavra = palavra[:-1]                     # "tratamentos" vira "tratamento"
        chaves.add(palavra)
    return chaves


def formatar_preco(valor):
    """Transforma 120 em 'R$ 120,00'."""
    return "R$ " + f"{valor:.2f}".replace(".", ",")


def descrever_servico(servico):
    """Texto de um serviço: nome, preço e duração."""
    return f"{servico.nome}: {formatar_preco(servico.preco)} ({servico.duracao_minutos} min)"


# ---------------------------------------------------------------------------
# Respostas que consultam o banco
# ---------------------------------------------------------------------------

def resposta_servicos():
    """Lista todos os serviços cadastrados no banco (tabela Servico)."""
    servicos = Servico.objects.all()
    if not servicos:
        return f"Ainda não temos serviços cadastrados. Fale com a gente pelo WhatsApp: {WHATSAPP_URL}"
    linhas = [descrever_servico(s) for s in servicos]
    return "Nossos serviços:\n" + "\n".join(linhas)


def buscar_servicos(palavras):
    """Procura serviços cujo nome tenha alguma palavra da mensagem."""
    achados = []
    for servico in Servico.objects.all():
        nome = normalizar(servico.nome)
        # Acha se o nome inteiro está na mensagem ou se alguma palavra da mensagem está no nome
        if any(len(p) >= 4 and p not in STOPWORDS and p in nome for p in palavras):
            achados.append(servico)
    return achados


def resposta_servico_encontrado(achados):
    """Monta a resposta quando a mensagem citou um ou mais serviços."""
    if len(achados) == 1:
        s = achados[0]
        # Se o serviço tem descrição, mostra junto
        descricao = f" {s.descricao}" if s.descricao else ""
        return f"{descrever_servico(s)}.{descricao}"
    linhas = [descrever_servico(s) for s in achados]
    return "Encontrei estes serviços:\n" + "\n".join(linhas)


def resposta_horarios():
    """Mostra os horários cadastrados (tabela HorarioFuncionamento), agrupando dias iguais."""
    horarios = list(HorarioFuncionamento.objects.all())   # já vem em ordem de segunda a domingo
    if not horarios:
        return f"Os horários ainda não foram cadastrados. Fale com a gente pelo WhatsApp: {WHATSAPP_URL}"

    def nome_curto(h):
        # "Segunda-feira" vira "Segunda"
        return h.get_dia_semana_display().replace("-feira", "")

    def texto_do_dia(h):
        if h.fechado:
            return "fechado"
        if h.abre and h.fecha:
            return f"{h.abre:%H:%M} às {h.fecha:%H:%M}"
        return "horário não definido"

    # Junta dias seguidos que têm o mesmo horário (ex.: segunda a sexta)
    grupos = []                                            # cada grupo: [primeiro, ultimo, texto]
    for h in horarios:
        texto = texto_do_dia(h)
        if grupos and grupos[-1][2] == texto and grupos[-1][3] == h.dia_semana - 1:
            grupos[-1][1] = nome_curto(h)                  # estende o grupo até este dia
            grupos[-1][3] = h.dia_semana
        else:
            grupos.append([nome_curto(h), nome_curto(h), texto, h.dia_semana])

    partes = []
    for primeiro, ultimo, texto, _ in grupos:
        dias = primeiro if primeiro == ultimo else f"{primeiro} a {ultimo}"
        partes.append(f"{dias}: {texto}")
    return "Horários de atendimento:\n" + "\n".join(partes)


def resposta_contatos():
    """Mostra os dados de contato da clínica (os mesmos do site)."""
    return (
        f"Contatos: telefone {CONTATO['telefone']}, e-mail {CONTATO['email']}, "
        f"endereço {CONTATO['endereco']}. WhatsApp: {WHATSAPP_URL}"
    )


def resposta_agendar():
    """Devolve o link do WhatsApp com a mensagem de agendamento já preenchida."""
    return f"Para agendar, é só chamar a clínica pelo WhatsApp: {WHATSAPP_URL}"


def buscar_duvida(chaves_usuario):
    """Acha a dúvida frequente (tabela DuvidasFrequente) mais parecida com a mensagem."""
    if not chaves_usuario:
        return None
    melhor, melhor_pontos = None, 0
    for duvida in DuvidasFrequente.objects.all():
        chaves_pergunta = palavras_chave(normalizar(duvida.pergunta))
        pontos = len(chaves_usuario & chaves_pergunta)     # quantas palavras importantes coincidem
        if pontos > melhor_pontos:
            melhor, melhor_pontos = duvida, pontos
    # Exige 2 palavras em comum (ou 1, se a mensagem tiver só uma palavra importante)
    if melhor and melhor_pontos >= min(2, len(chaves_usuario)):
        return melhor
    return None


# ---------------------------------------------------------------------------
# Decide o que responder
# ---------------------------------------------------------------------------

def gerar_resposta(texto):
    """Recebe o texto da pessoa e devolve a resposta do chatbot."""
    if texto == "":
        return MENU                                        # mensagem vazia ou só espaços

    normal = normalizar(texto)
    palavras = palavras_de(normal)

    # 1) Opções do menu
    if normal == "1":
        return resposta_servicos()
    if normal == "2":
        return resposta_horarios()
    if normal == "3":
        return resposta_contatos()

    # 2) Saudações: mostram o menu
    if palavras & SAUDACOES and len(palavras) <= 3:
        return MENU

    # 3) Pedido de agendamento: devolve o link do WhatsApp
    if palavras & PALAVRAS_AGENDAR:
        return resposta_agendar()

    # 4) Horário e contato
    if palavras & PALAVRAS_HORARIO:
        return resposta_horarios()
    if palavras & PALAVRAS_CONTATO:
        return resposta_contatos()

    # 5) Cita um serviço do banco (ex.: "limpeza de pele", "massagem")
    achados = buscar_servicos(palavras)
    if achados:
        return resposta_servico_encontrado(achados)

    # 6) Pergunta sobre preços em geral: lista todos
    if palavras & PALAVRAS_PRECO:
        return resposta_servicos()

    # 7) Dúvida frequente parecida
    duvida = buscar_duvida(palavras_chave(normal))
    if duvida:
        return duvida.resposta

    # 8) Não entendeu
    return FALLBACK


# ---------------------------------------------------------------------------
# View: é a função que recebe a mensagem enviada pelo chat do site
# ---------------------------------------------------------------------------

@require_POST                                              # GET devolve erro 405
def processar_mensagem(request):
    # Tenta ler o JSON enviado. Se estiver quebrado, devolve erro 400 (e não 500).
    try:
        dados = json.loads(request.body)
    except ValueError:
        return JsonResponse({"resposta": "Não consegui ler a sua mensagem. Tente de novo."}, status=400)

    # O JSON precisa ser um objeto com "mensagem" em texto (ex.: {"mensagem": "oi"})
    if not isinstance(dados, dict) or not isinstance(dados.get("mensagem", ""), str):
        return JsonResponse({"resposta": "Mensagem em formato inválido."}, status=400)

    # Tira espaços das pontas e limita o tamanho para o chat não travar com textos enormes
    texto = dados.get("mensagem", "").strip()[:500]

    return JsonResponse({"resposta": gerar_resposta(texto)})