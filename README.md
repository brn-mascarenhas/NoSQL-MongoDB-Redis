# Desafio NoSQL com Python, MongoDB e Redis

Este projeto demonstra uma conexão Python com dois bancos NoSQL:

- **MongoDB Atlas**, usado como banco principal de produtos.
- **Redis Cloud**, usado para operações simples e cache.

O script realiza operações básicas de CRUD no MongoDB, operações com estruturas do Redis e um caso integrado de cache usando TTL de 60 segundos.

## Tecnologias utilizadas

- Python 3.10+
- pymongo
- redis-py
- python-dotenv
- MongoDB Atlas
- Redis Cloud

## Estrutura do projeto

```text
desafio_nosql_python/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Configuração das strings de conexão

As credenciais reais devem ficar apenas no arquivo `.env`.

Este projeto já contém um `.env.example` com a estrutura correta, mas com as senhas ocultas. Substitua pela sua string de conexão.

### MongoDB

A string informada no Atlas deve ser usada sem os caracteres `<` e `>` ao redor da senha.

Formato correto:

```env
MONGO_URI=mongodb+srv://usuario_db_user:SUA_SENHA_DO_MONGODB@cluster0.qyzghmt.mongodb.net/desafio_nosql?retryWrites=true&w=majority
```

Exemplo do que não deve ser feito:

```env
MONGO_URI=mongodb+srv://usuario_db_user:<SUA_SENHA>@cluster0.qyzghmt.mongodb.net/
```

Os sinais `<` e `>` aparecem no modelo do MongoDB Atlas apenas para indicar substituição. Eles não devem entrar na URI real.

### Redis

O comando informado pelo Redis vem assim:

```bash
redis-cli -u redis://default:SUA_SENHA_REDIS@home-oaken-wing-77993.db.redis.io:14540
```

No arquivo `.env`, use apenas a URL após `-u`:

```env
REDIS_URL=redis://default:SUA_SENHA_REDIS@home-oaken-wing-77993.db.redis.io:14540
```

Não coloque `redis-cli -u` dentro do `.env`.

## Instalação

Crie um ambiente virtual:

```bash
python -m venv venv
```

Ative o ambiente virtual:

### Windows

```bash
venv\Scripts\activate
```

### Linux/macOS

```bash
source venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Copie o arquivo de exemplo:

### Windows

```bash
copy .env.example .env
```

### Linux/macOS

```bash
cp .env.example .env
```

Depois, edite o arquivo `.env` e substitua por suas respectivas strings de conexões.

## Execução

Execute:

```bash
python main.py
```

## O que o script faz

### MongoDB

O script:

1. Conecta ao MongoDB Atlas.
2. Usa o banco `desafio_nosql`.
3. Usa a coleção `produtos`.
4. Insere produtos com os campos:
   - `nome`
   - `preco`
   - `categoria`
5. Consulta produtos com preço maior que 10.
6. Atualiza o preço do produto `Mouse Gamer`.
7. Remove um produto da categoria `papelaria`.

### Redis

O script:

1. Conecta ao Redis Cloud.
2. Armazena uma string na chave `mensagem:inicio`.
3. Armazena dados de usuário em uma hash chamada `usuario:1`.
4. Armazena logs de acesso em uma lista chamada `logs:acesso`.
5. Recupera e exibe todos os logs da lista.

### Cache integrado

A função `buscar_produto_com_cache()` busca um produto pelo nome seguindo este fluxo:

1. Verifica se existe uma chave Redis no formato `produto:{nome}`.
2. Se existir, retorna o produto a partir do cache.
3. Se não existir, busca o produto no MongoDB.
4. Se encontrar no MongoDB, salva no Redis com TTL de 60 segundos.
5. Retorna os dados do produto.

Exemplo de chave usada:

```text
produto:Mouse Gamer
```

## Tratamento de exceções

O projeto trata erros como:

- URI incorreta do MongoDB.
- Falha de autenticação no MongoDB.
- Falha de conexão com MongoDB.
- Falha de autenticação no Redis.
- Falha de conexão com Redis.
- Variáveis de ambiente ausentes.

## Observação sobre segurança

Não suba o arquivo `.env` para o GitHub.

O arquivo `.gitignore` já ignora `.env`, `venv/` e arquivos temporários do Python.

Se uma senha for publicada em algum repositório, o ideal é trocá-la imediatamente no painel do MongoDB Atlas ou Redis Cloud.
