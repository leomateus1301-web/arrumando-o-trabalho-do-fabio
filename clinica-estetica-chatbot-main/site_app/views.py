from urllib.parse import quote

from django.shortcuts import render
from clinica.models import Servico

WHATSAPP_NUMERO = "5511994786180"
WHATSAPP_MENSAGEM = "Olá, gostaria de agendar uma consulta."
WHATSAPP_URL = f"https://wa.me/{WHATSAPP_NUMERO}?text={quote(WHATSAPP_MENSAGEM)}"

CONTATO = {
    "endereco": "Rua Exemplo, 123 — Jardins, São Paulo/SP",
    "telefone": "(11) 99999-9999",
    "email": "contato@silviaribeiro.com.br",
    "horarios": [
        ("Segunda a sexta", "09h às 19h"),
        ("Sábado", "09h às 14h"),
    ],
    "instagram": "https://instagram.com/",
    "whatsapp": WHATSAPP_URL,
}

# --- Mapa -------------------------------------------------------------
# Troque pelas coordenadas reais do consultório (clique com o botão direito
# no Google Maps e copie latitude/longitude).
LOCAL = {"lat": -23.5617, "lon": -46.6693}
_d = 0.005  # "zoom" do mapa: menor = mais aproximado
CONTATO["mapa_src"] = (
    "https://www.openstreetmap.org/export/embed.html"
    f"?bbox={LOCAL['lon'] - _d:.5f}%2C{LOCAL['lat'] - _d:.5f}%2C{LOCAL['lon'] + _d:.5f}%2C{LOCAL['lat'] + _d:.5f}"
    f"&layer=mapnik&marker={LOCAL['lat']}%2C{LOCAL['lon']}"
)
CONTATO["mapa_link"] = "https://www.google.com/maps/search/?api=1&query=" + quote(CONTATO["endereco"])

# --- Agenda -----------------------------------------------------------
# Dias da semana: 0 = domingo, 1 = segunda ... 6 = sábado.
# Cada dia é [hora de abertura, hora de fechamento]. Dia ausente = fechado.
AGENDA = {
    "dias_a_frente": 60,   # até quantos dias à frente o calendário permite agendar
    "duracao_min": 30,     # duração de cada atendimento, em minutos
    "fuso": "Horário Padrão de Brasília (BRT)",
    "horarios": {
        "1": [9, 19],   # segunda: abre 9h, fecha 19h
        "2": [9, 19],
        "3": [9, 19],
        "4": [9, 19],
        "5": [9, 19],
        "6": [9, 14],   # sábado
    },
}

TRATAMENTOS = [
    {
        "categoria": "facial",
        "rotulo": "Facial",
        "itens": [
            {"nome": "Limpeza de pele", "icone": "✨", "preco": "120,00", "descricao": "Higienização profunda, esfoliação e cuidados para uma pele mais saudável."},
            {"nome": "Hidratação facial", "icone": "🌸", "preco": "90,00", "descricao": "Reposição de água e nutrientes para uma pele macia, luminosa e iluminada."},
            {"nome": "Design de sobrancelhas", "icone": "💎", "preco": "60,00", "descricao": "Modelagem personalizada para valorizar o formato do seu rosto."},
            {"nome": "Peeling renovador", "icone": "🍃", "preco": "", "descricao": "Renova as camadas superficiais e suaviza manchas e marcas."},
        ],
    },
    {
        "categoria": "corporal",
        "rotulo": "Corporal",
        "itens": [
            {"nome": "Massagem relaxante", "icone": "💆", "preco": "100,00", "descricao": "Técnicas de massagem para aliviar a tensão e proporcionar relaxamento."},
            {"nome": "Drenagem linfática", "icone": "💧", "preco": "", "descricao": "Reduz o inchaço e a retenção de líquidos, com sensação de leveza."},
            {"nome": "Massagem modeladora", "icone": "🌿", "preco": "", "descricao": "Trabalha contornos e firmeza com técnicas personalizadas."},
            {"nome": "Tratamento para celulite", "icone": "🫧", "preco": "", "descricao": "Protocolo combinado para melhorar a textura e a aparência da pele."},
        ],
    },
    {
        "categoria": "rejuvenescimento",
        "rotulo": "Rejuvenescimento",
        "itens": [
            {"nome": "Bioestimuladores de colágeno", "icone": "🧬", "preco": "", "descricao": "Estimulam a produção natural de colágeno para sustentar a pele."},
            {"nome": "Microagulhamento", "icone": "🔬", "preco": "", "descricao": "Melhora a textura, cicatrizes e a qualidade geral da pele."},
            {"nome": "Protocolos antienvelhecimento", "icone": "⏳", "preco": "", "descricao": "Planos que unem técnicas para resultados naturais e graduais."},
        ],
    },
]

DEPOIMENTOS = [
    {"nome": "Mariana S.", "texto": "Fui ouvida desde a primeira conversa. O plano foi pensado para a minha pele, e não para um protocolo pronto.", "estrelas": 5},
    {"nome": "Camila R.", "texto": "Ambiente acolhedor e muita clareza em cada etapa. Saí do consultório sabendo exatamente o que esperar.", "estrelas": 5},
    {"nome": "Juliana A.", "texto": "Resultado natural, do jeito que eu queria. Recomendo para quem busca cuidado de verdade.", "estrelas": 5},
]


def _contexto(extra=None):
    ctx = {"contato": CONTATO, "whatsapp_numero": WHATSAPP_NUMERO}
    if extra:
        ctx.update(extra)
    return ctx


def _destaques(qtd=4):
    """Serviços com preço vêm primeiro; completa com os demais até `qtd`."""
    todos = [item for cat in TRATAMENTOS for item in cat["itens"]
             for item in [dict(item, rotulo=cat["rotulo"], categoria=cat["categoria"])]]
    todos.sort(key=lambda i: not i["preco"])  # sort estável: com preço primeiro
    return todos[:qtd]


def home(request):
    return render(request, "site_app/home.html", _contexto({
        "tratamentos": TRATAMENTOS,
        "destaques": _destaques(),
        "depoimentos": DEPOIMENTOS,
        "agenda": AGENDA,
        "pagina": "home",
    }))


def servicos(request):
    # 1. Busca os serviços cadastrados no SQLite
    lista_servicos = Servico.objects.all()
    
    # 2. Renderiza a página mantendo a estrutura do _contexto e enviando o banco
    return render(request, "site_app/servicos.html", _contexto({
        "servicos": lista_servicos,
        "tratamentos": TRATAMENTOS, # Mantido para não quebrar outras partes da tela
        "agenda": AGENDA,
        "pagina": "servicos",
    }))


def contato(request):
    return render(request, "site_app/contato.html", _contexto({
        "tratamentos": TRATAMENTOS,
        "pagina": "contato",
    }))


def privacidade(request):
    return render(request, "site_app/privacidade.html", _contexto({"pagina": "privacidade"}))


def sobre(request):
    return render(request, "site_app/sobre.html", _contexto({"pagina": "sobre"}))