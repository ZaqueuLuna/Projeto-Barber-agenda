# BarberAgenda

Sistema web de agendamento para barbearias. A recepção marca, remarca, conclui e cancela
atendimentos; o sistema impede dois clientes no mesmo horário com o mesmo profissional.
O administrador também cadastra serviços, profissionais e usuários e acompanha o painel
de faturamento.

Projeto Integrador Transdisciplinar em Sistemas de Informação II (PIT II) - Cruzeiro do Sul.

## Tecnologias

Python 3.10+, Flask (padrão MVC), SQLAlchemy, Flask-Login, MySQL (produção) ou SQLite
(desenvolvimento), Bootstrap 5 e Pytest.

## Estrutura (MVC)

```
app/
  models/        Model: classes persistentes e regras de negócio (RN01 a RN06)
  controllers/   Controller: rotas Flask, uma por área do sistema
  templates/     View: páginas Jinja
  static/        CSS e JavaScript
database/        schema.sql (projeto físico) e seed.sql (dados de exemplo)
tests/           testes automatizados com Pytest
```

## Rodar no seu computador

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
flask --app run popular      # cria o banco SQLite com dados de exemplo
flask --app run run          # abre em http://127.0.0.1:5000
```

Usuários criados pelo comando `popular`:

| Perfil | E-mail | Senha |
| --- | --- | --- |
| Administrador | admin | admin |
| Recepcionista | recepcao@barberagenda.com | recepcao123 |

Troque essas senhas antes de divulgar o link do sistema: entre com cada usuário e use
**Alterar senha**, na barra lateral.

## Rodar os testes

```bash
python -m pytest -v
```

São 30 testes: as regras de negócio (CT01 a CT08 do plano de testes), controle de acesso
(CT09 e CT10), abertura de todas as telas, um fluxo completo pela interface, a troca de senha e a proteção
contra redirecionamento para outros sites após o login.

## Publicar no PythonAnywhere (plano gratuito)

1. Crie uma conta *Beginner* em pythonanywhere.com. O nome de usuário vira o endereço:
   `SEUUSUARIO.pythonanywhere.com`.
2. Envie o código. Pelo GitHub, abra um **Bash console** e rode
   `git clone https://github.com/SEUUSUARIO/barberagenda.git`. Sem GitHub, envie o `.zip`
   na aba **Files** e rode `unzip barberagenda.zip`.
3. No mesmo console, crie o ambiente e instale as dependências:
   ```bash
   cd barberagenda
   mkvirtualenv barber --python=python3.10
   pip install -r requirements.txt
   ```
4. Na aba **Databases**, defina uma senha do MySQL e crie o banco `barberagenda`.
   O nome completo fica `SEUUSUARIO$barberagenda`.
5. Crie o arquivo `.env` dentro da pasta do projeto (aba **Files**) com:
   ```
   SECRET_KEY=uma-frase-longa-e-aleatoria
   DATABASE_URL=mysql+pymysql://SEUUSUARIO:SENHA_DO_MYSQL@SEUUSUARIO.mysql.pythonanywhere-services.com/SEUUSUARIO$barberagenda
   ```
6. No console, com o ambiente ativo (`workon barber`), crie as tabelas e os dados:
   `flask --app run popular`
7. Na aba **Web**, clique em **Add a new web app** → **Manual configuration** → Python 3.10.
   Depois, na mesma página:
   - **Virtualenv**: `/home/SEUUSUARIO/.virtualenvs/barber`
   - **Static files**: URL `/static/` e diretório `/home/SEUUSUARIO/barberagenda/app/static`
   - Abra o **WSGI configuration file**, apague o conteúdo e deixe só:
     ```python
     import sys
     caminho = "/home/SEUUSUARIO/barberagenda"
     if caminho not in sys.path:
         sys.path.insert(0, caminho)
     from run import app as application
     ```
8. Clique em **Reload** e acesse `https://SEUUSUARIO.pythonanywhere.com`.

No plano gratuito, o site precisa ser renovado a cada 3 meses pelo botão
**Run until 3 months from today**, na aba Web. Se algo der errado, o motivo aparece no
**Error log**, na mesma aba.

## Regras de negócio

| ID | Regra |
| --- | --- |
| RN01 | Dois agendamentos em aberto do mesmo profissional não podem se sobrepor |
| RN02 | Não é possível agendar em data ou hora que já passou |
| RN03 | O atendimento precisa caber no horário do profissional |
| RN04 | Cancelar libera o horário e exige um motivo |
| RN05 | Só atendimentos concluídos entram no faturamento, pelo preço do dia do agendamento |
| RN06 | Clientes, serviços, profissionais e usuários são inativados, nunca excluídos |
