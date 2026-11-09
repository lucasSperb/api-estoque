# API do Controle de Estoque e Vendas

Backend em FastAPI + PostgreSQL para o front `estoque-vendas-app`. Guarda produtos, clientes, vendas e movimentações de estoque.

Cada registro vira uma linha na tabela `documentos` (coleção, id e o JSON do registro em JSONB). A tabela é criada sozinha na primeira inicialização.

## Rotas

| Método | Rota | Efeito |
| --- | --- | --- |
| GET | `/{colecao}` | lista os registros da coleção |
| PUT | `/{colecao}/{id}` | cria ou substitui um registro (corpo JSON) |
| DELETE | `/{colecao}/{id}` | remove (responde 204) |
| GET | `/health` | testa a conexão com o banco |
| GET | `/docs` | documentação interativa (Swagger) |

Coleções aceitas: `produtos`, `clientes`, `vendas`, `movs`. Qualquer outra responde 404.

## Rodar localmente

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Sem `DATABASE_URL`, usa um arquivo SQLite (`local.db`) só para testes. Abra http://localhost:8000/docs.

Para apontar o front local para esta API, crie `.env.local` no projeto do front com `VITE_API_URL=http://localhost:8000`.

## Colocar no Railway, passo a passo

### 1. Subir o código para o GitHub
Crie um repositório só para esta pasta (`estoque-vendas-api`) e envie os arquivos:

```bash
git init
git add .
git commit -m "API de estoque e vendas"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/estoque-vendas-api.git
git push -u origin main
```

### 2. Criar o projeto e o serviço da API
1. Em railway.com, clique em **New Project**.
2. Escolha **Deploy from GitHub repo** e selecione `estoque-vendas-api` (autorize o GitHub se pedir).
3. O Railway detecta Python, instala o `requirements.txt` e usa o `railway.json` (comando de início e teste de saúde em `/health`). O primeiro deploy vai falhar com "DATABASE_URL não definida". Isso é esperado: falta o banco.

### 3. Criar o banco PostgreSQL
1. No canvas do projeto, clique em **+ Create** (ou **New**) e escolha **Database → Add PostgreSQL**.
2. Aguarde o serviço `Postgres` ficar verde.

### 4. Ligar a API ao banco
1. Clique no serviço da API, aba **Variables**, **New Variable**.
2. Nome: `DATABASE_URL`. Valor: `${{Postgres.DATABASE_URL}}` (referência ao banco; se você renomeou o serviço do banco, troque `Postgres` pelo nome dele).
3. Salve. O Railway faz um novo deploy sozinho.

### 5. Gerar o endereço público
1. Serviço da API, **Settings → Networking → Generate Domain**.
2. Copie o endereço (algo como `https://estoque-api-production.up.railway.app`).

### 6. Testar
- Abra `SEU-ENDERECO/health`: deve mostrar `{"status":"ok","banco":"ok"}`.
- Abra `SEU-ENDERECO/docs` e teste um `PUT /produtos/teste` com `{"nome":"Teste"}`; depois `GET /produtos` deve listar. Apague com `DELETE /produtos/teste`.

### 7. Ligar o front (Vercel)
1. No projeto da Vercel, **Settings → Environment Variables**: `VITE_API_URL` = o endereço do passo 5, com `https://` e sem barra no final.
2. Faça **Redeploy**. O Vite grava essa variável no momento do build, então sem novo deploy ela não vale.

### 8. Travar o CORS
Na API (Railway), em **Variables**, crie `ALLOWED_ORIGINS` com o domínio do front na Vercel, por exemplo `https://seu-app.vercel.app` (vários domínios separados por vírgula, sem barra no final). Sem essa variável, qualquer site consegue chamar a API pelo navegador.

## Limites desta versão

- **Sem login.** Quem souber o endereço da API consegue ler e alterar os dados. O CORS só impede outros sites no navegador, não impede chamadas diretas. Antes de usar com dados reais de clientes e vendas, adicione autenticação.
- **Venda não é atômica.** O front grava venda, estoque e movimentação em chamadas separadas. Se a rede cair no meio, o estoque pode ficar diferente das vendas. O correto é uma rota `POST /vendas` que faça tudo numa transação.
- **Sem migrações.** A tabela é criada com `create_all`. Para mudar o esquema depois, use Alembic.
- **Backup.** Confira as opções de backup do serviço Postgres no Railway antes de guardar dados reais.
