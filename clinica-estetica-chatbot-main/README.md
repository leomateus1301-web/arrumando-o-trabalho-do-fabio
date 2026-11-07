# Chatbot SR Estética Avançada

Site institucional com chatbot de atendimento para a clínica **SR Estética Avançada**, desenvolvido em Python e Django como atividade extensionista da disciplina **Aplicação de Cloud, IoT e Indústria 4.0 em Python** (Estácio, Unidade Liberdade, curso de Análise e Desenvolvimento de Sistemas).

O chatbot apresenta serviços e preços, informa horários e contatos, responde dúvidas frequentes e direciona solicitações de agendamento para o WhatsApp da clínica.

## Integrantes

- Vinícius L. Garcia
- Caio V. A. dos Santos
- William L. Rodrigues
- Leonardo M. Machado
- João V. I. dos Santos

Orientador: Fabio da Roza Oliveira

## Tecnologias

- Python 3.12+
- Django
- SQLite
- HTML, CSS e JavaScript

## Estrutura do projeto

```
core/        configurações e rotas principais do projeto
clinica/     modelos de dados (serviços, horários, contatos, dúvidas) e lógica do chatbot
site_app/    páginas e funcionalidades do site
dados_iniciais.json dados iniciais do banco (serviços, horários e dúvidas frequentes)
duvidas.json dúvidas frequentes (mesmo formato do dados_iniciais.json)
manage.py    comandos administrativos do Django
```

## Como executar

Pré-requisito: Python 3.12 ou superior instalado (o Django 6 exige essa versão). Confira com `python --version`.

1. Clone o repositório (ou extraia o ZIP) e entre na pasta do projeto, onde está o `manage.py`.

2. Crie e ative o ambiente virtual:

   Windows:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

   Linux ou macOS:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

4. Crie o banco de dados:
   ```
   python manage.py migrate
   ```

5. Carregue os dados iniciais (serviços, horários e dúvidas frequentes):
   ```
   python manage.py loaddata dados_iniciais.json
   ```

6. Crie um usuário administrador para cadastrar e editar serviços, horários e dúvidas:
   ```
   python manage.py createsuperuser
   ```

7. Inicie o servidor:
   ```
   python manage.py runserver
   ```

8. Acesse no navegador:
   - Site com chatbot: http://127.0.0.1:8000/
   - Painel administrativo: http://127.0.0.1:8000/admin/

## Dados da aplicação

O arquivo `db.sqlite3` não é versionado, pois é gerado a cada instalação pelo comando `migrate`. Os dados iniciais da clínica (serviços, preços, horários de funcionamento e dúvidas frequentes) estão no arquivo `dados_iniciais.json` e são carregados com o comando `loaddata`. Qualquer dado pode ser alterado depois pelo painel administrativo (`/admin/`).

Para atualizar o arquivo de dados iniciais depois de alterar serviços, horários ou dúvidas no banco local (sem exportar os registros de `Contato`, que são pessoas que usaram o chat):

```
python -X utf8 manage.py dumpdata clinica --exclude clinica.contato --indent 2 --output dados_iniciais.json
```

## Como usar o chatbot

O chatbot recebe mensagens pela rota `/chatbot/mensagem/` (método POST, corpo em JSON). Na interface do site, basta abrir o chat e digitar:

- `oi` ou `menu`: exibe o menu principal
- `1`: serviços e preços
- `2`: horários de funcionamento
- `3`: contatos
- `quero agendar`: devolve o link do WhatsApp da clínica com a mensagem de agendamento
- perguntas como "quais cuidados após os tratamentos?": respostas das dúvidas frequentes

Mensagens não reconhecidas recebem uma orientação com o menu e o link do WhatsApp. Requisições inválidas retornam erro HTTP 400.

## Testes

Os testes são manuais e estão descritos na seção 7 (Testes e Validação) do Relatório Extensionista, com as evidências no Anexo B.