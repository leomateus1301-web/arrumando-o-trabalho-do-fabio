# Importa o módulo "models" do Django, que contém as classes e os tipos de campo
# usados para descrever as tabelas do banco de dados (ORM).
from django.db import models


# Cada classe que herda de models.Model vira uma TABELA no banco (clinica_servico).
# Esta tabela guarda os procedimentos de estética oferecidos pela clínica.
class Servico(models.Model):
    # Texto curto (até 100 caracteres). unique=True impede dois serviços com o mesmo nome.
    nome = models.CharField(max_length=100, unique=True)

    # Texto longo, sem limite fixo. blank=True deixa o campo opcional no formulário/admin.
    descricao = models.TextField(blank=True)

    # Número decimal exato (usado para dinheiro): até 8 dígitos no total, 2 depois da vírgula.
    preco = models.DecimalField(max_digits=8, decimal_places=2)

    # Número inteiro positivo com a duração em minutos. help_text é a dica exibida no admin.
    duracao_minutos = models.PositiveIntegerField(help_text="Duração do procedimento em minutos")

    # Configurações do modelo que não criam colunas.
    class Meta:
        # Nome legível (singular) mostrado no painel admin.
        verbose_name = "Serviço"
        # Nome legível (plural) mostrado no painel admin.
        verbose_name_plural = "Serviços"
        # Ordem padrão das consultas: alfabética pelo nome.
        ordering = ["nome"]

    # Define como o objeto aparece como texto (no admin, no print, no shell).
    def __str__(self):
        # Retorna o nome do serviço, em vez de "Servico object (1)".
        return self.nome


# Tabela com as perguntas e respostas padrão que o chatbot vai consultar.
class DuvidasFrequente(models.Model):
    # Pergunta curta (até 255 caracteres), por isso CharField.
    pergunta = models.CharField(max_length=255)

    # Resposta que pode ser longa, por isso TextField (sem limite de tamanho).
    # Atenção aos parênteses: é uma chamada que CRIA o campo.
    resposta = models.TextField()

    # Configurações do modelo.
    class Meta:
        # Nomes legíveis no admin (com acento e plural correto).
        verbose_name = "Dúvida Frequente"
        verbose_name_plural = "Dúvidas Frequentes"

    # No admin, cada dúvida aparece pelo texto da pergunta.
    # Fica FORA da Meta, no mesmo nível dela, pois é um método da classe do modelo.
    def __str__(self):
        # "self." acessa o campo "pergunta" deste objeto.
        return self.pergunta


# Tabela que registra as pessoas que conversaram com o chatbot.
class Contato(models.Model):
    # Nome da pessoa (texto curto).
    nome = models.CharField(max_length=100)

    # Telefone guardado como TEXTO, e não número, para manter "+", parênteses,
    # traços e zeros à esquerda. Não fazemos cálculo com telefone.
    telefone = models.CharField(max_length=20)

    # Data e hora preenchidas AUTOMATICAMENTE no momento em que o registro é criado.
    # Depois disso o campo não é mais editável.
    data_hora = models.DateTimeField(auto_now_add=True)

    # Configurações do modelo.
    class Meta:
        verbose_name = "Contato"
        verbose_name_plural = "Contatos"
        # O sinal "-" inverte a ordem: os contatos mais recentes aparecem primeiro.
        ordering = ["-data_hora"]

    # No admin, cada contato aparece como "Nome (telefone)".
    def __str__(self):
        return f"{self.nome} ({self.telefone})"

# Tabela com os horários de funcionamento da clínica (uma linha por dia da semana).
class HorarioFuncionamento(models.Model):
    dias_semana = [
        (0, "Segunda-feira"),
        (1, "Terça-feira"),
        (2, "Quarta-feira"),
        (3, "Quinta-feira"),
        (4, "Sexta-feira"),
        (5, "Sábado"),
        (6, "Domingo"),
    ]

    # Dia da semana: o banco guarda o número, mas o admin mostra o nome do dia.
    dia_semana = models.IntegerField(choices=dias_semana, unique=True)
    # Horário de abertura. null=True e blank=True deixam o campo vazio quando a clínica não abre.
    abre = models.TimeField(null=True, blank=True)

    # Horário de fechamento. null=True e blank=True deixam o campo vazio quando a clínica não abre.
    fecha = models.TimeField(null=True, blank=True)

    # Caixinha para marcar quando a clínica NÃO atende naquele dia.
    fechado = models.BooleanField(default=False)

        # Configurações do modelo que não criam colunas.
    class Meta:
        # Nomes legíveis no admin.
        verbose_name = "Horário de Funcionamento"
        verbose_name_plural = "Horários de Funcionamento"
        # Ordem da lista: de segunda a domingo.
        ordering = ["dia_semana"]

    # Texto que aparece para cada registro no admin e no shell.
    def __str__(self):
        # get_dia_semana_display() devolve o NOME do dia (ex.: "Sábado") em vez do número.
        dia = self.get_dia_semana_display()
        if self.fechado:
            return f"{dia}: fechado"
        if self.abre and self.fecha:
            # :%H:%M mostra a hora no formato 09:00
            return f"{dia}: {self.abre:%H:%M} às {self.fecha:%H:%M}"
        return f"{dia}: horário não definido"