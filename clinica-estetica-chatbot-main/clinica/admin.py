# Importa o sistema de administração que já vem pronto no Django.
from django.contrib import admin

# Importa os três modelos criados no models.py ("." significa "da mesma pasta/app").
from .models import Servico, DuvidasFrequente, Contato, HorarioFuncionamento

# O decorador @admin.register registra o modelo Servico no painel admin
# e liga esse modelo à classe de configuração logo abaixo.
@admin.register(Servico)
class ServicoAdmin (admin.ModelAdmin):
    #Colunas exibidas na listagem de serviços (em vez de só o resultado do __str__).
    list_display = ("nome", "preco", "duracao_minutos")
    #Cria um barra de busca que procura nestes campos.
    search_fields = ("nome", "descricao")

#Registra o modelo Duvida frequente no painel Admin.
@admin.register(Contato)
class ContatoADmin(admin.ModelAdmin):
    list_display = ("nome", "telefone", "data_hora")
    #Cria um barra de busca que procura nestes campos.
    search_fields = ("nome", "telefone")
    # Mostra data_hora na tela de detalhe, mas sem permitir edição.
    # Necessário porque campos com auto_now_add não aparecem no formulário por padrão.
    readonly_fields = ("data_hora",)

# Registra o modelo DuvidaFrequente no painel admin.
@admin.register(DuvidasFrequente)
class DuvidaFrequenteAdmin(admin.ModelAdmin):
    # Mostra a pergunta na listagem. A vírgula final é obrigatória em tupla de 1 item.
    list_display = ("pergunta",)

    # Permite buscar tanto pela pergunta quanto pelo texto da resposta.
    search_fields = ("pergunta", "resposta")

# Registra o modelo HorarioFuncionamento no painel admin.
@admin.register(HorarioFuncionamento)
class HorarioFuncionamentoAdmin(admin.ModelAdmin):
    # Colunas da lista: o dia (com o nome, e não o número), os horários e a caixinha "fechado".
    list_display = ("dia_semana", "abre", "fecha", "fechado")

    # Campos que podem ser editados DIRETO NA LISTA, sem abrir cada dia.
    # O primeiro campo (dia_semana) não entra aqui, pois ele é o link para abrir o registro.
    list_editable = ("abre", "fecha", "fechado")