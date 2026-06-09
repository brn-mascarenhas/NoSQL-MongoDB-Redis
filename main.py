"""
Atividade: Conexão Python com NoSQL - MongoDB e Redis

Este script:
1. Conecta no MongoDB Atlas.
2. Cria/usa o banco desafio_nosql e a coleção produtos.
3. Realiza operações CRUD no MongoDB.
4. Conecta no Redis Cloud/Upstash.
5. Realiza operações básicas no Redis.
6. Demonstra cache de produtos com TTL de 60 segundos.
"""

import certifi
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import redis
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import (
    ConfigurationError,
    ConnectionFailure,
    OperationFailure,
    ServerSelectionTimeoutError,
)
from redis.exceptions import (
    AuthenticationError as RedisAuthenticationError,
    ConnectionError as RedisConnectionError,
    TimeoutError as RedisTimeoutError,
)

DB_NAME = "desafio_nosql"
COLLECTION_NAME = "produtos"
CACHE_TTL_SECONDS = 60


def carregar_variaveis_ambiente() -> tuple[str, str]:
    """Carrega e valida as variáveis de ambiente necessárias."""
    load_dotenv()

    mongo_uri = os.getenv("MONGO_URI")
    redis_url = os.getenv("REDIS_URL")

    if not mongo_uri:
        raise ValueError("Variável MONGO_URI não configurada no arquivo .env.")

    if not redis_url:
        raise ValueError("Variável REDIS_URL não configurada no arquivo .env.")

    return mongo_uri.strip(), redis_url.strip()


def conectar_mongo(mongo_uri: str) -> MongoClient:
    """Cria conexão com MongoDB Atlas e testa a conexão com ping."""
    try:
        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000,
            tlsCAFile=certifi.where(),
        )
        client.admin.command("ping")
        print("✅ Conexão com MongoDB realizada com sucesso.")
        return client

    except ConfigurationError as erro:
        raise RuntimeError(f"Erro de configuração da URI do MongoDB: {erro}") from erro

    except OperationFailure as erro:
        raise RuntimeError(f"Erro de autenticação/autorização no MongoDB: {erro}") from erro

    except (ServerSelectionTimeoutError, ConnectionFailure) as erro:
        raise RuntimeError(f"Erro de conexão com MongoDB: {erro}") from erro


def conectar_redis(redis_url: str) -> redis.Redis:
    """Cria conexão com Redis Cloud/Upstash e testa a conexão com ping."""
    try:
        redis_client = redis.Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        redis_client.ping()
        print("✅ Conexão com Redis realizada com sucesso.")
        return redis_client

    except RedisAuthenticationError as erro:
        raise RuntimeError(f"Erro de autenticação no Redis: {erro}") from erro

    except (RedisConnectionError, RedisTimeoutError) as erro:
        raise RuntimeError(f"Erro de conexão com Redis: {erro}") from erro


def obter_colecao_produtos(mongo_client: MongoClient) -> Collection:
    """Retorna a coleção produtos do banco desafio_nosql."""
    database = mongo_client[DB_NAME]
    return database[COLLECTION_NAME]


def documento_produto_para_dict(produto: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Converte documento do MongoDB para dict serializável em JSON."""
    if not produto:
        return None

    produto_formatado = dict(produto)
    produto_formatado["_id"] = str(produto_formatado["_id"])
    return produto_formatado


def inserir_produtos(collection: Collection) -> None:
    """Insere produtos de exemplo na coleção."""
    produtos = [
        {"nome": "Mouse Gamer", "preco": 89.90, "categoria": "perifericos"},
        {"nome": "Teclado Mecânico", "preco": 199.90, "categoria": "perifericos"},
        {"nome": "Caderno", "preco": 8.50, "categoria": "papelaria"},
        {"nome": "Monitor LED", "preco": 799.90, "categoria": "monitores"},
    ]

    # Limpa a coleção apenas para evitar duplicação em testes repetidos.
    collection.delete_many({})

    resultado = collection.insert_many(produtos)
    print(f"✅ {len(resultado.inserted_ids)} produtos inseridos no MongoDB.")


def consultar_produtos_preco_maior_que(collection: Collection, preco_minimo: float) -> List[Dict[str, Any]]:
    """Consulta produtos com preço maior que o valor informado."""
    produtos = list(collection.find({"preco": {"$gt": preco_minimo}}))
    return [documento_produto_para_dict(produto) for produto in produtos]


def atualizar_preco_produto(collection: Collection, nome: str, novo_preco: float) -> None:
    """Atualiza o preço de um produto específico pelo nome."""
    resultado = collection.update_one(
        {"nome": nome},
        {"$set": {"preco": novo_preco}},
    )

    if resultado.matched_count == 0:
        print(f"⚠️ Produto '{nome}' não encontrado para atualização.")
        return

    print(f"✅ Produto '{nome}' atualizado para R$ {novo_preco:.2f}.")


def remover_produto_por_categoria(collection: Collection, categoria: str) -> None:
    """Remove um produto pela categoria informada."""
    resultado = collection.delete_one({"categoria": categoria})

    if resultado.deleted_count == 0:
        print(f"⚠️ Nenhum produto encontrado na categoria '{categoria}'.")
        return

    print(f"✅ Um produto da categoria '{categoria}' foi removido.")


def executar_operacoes_mongo(collection: Collection) -> None:
    """Executa as operações obrigatórias de CRUD no MongoDB."""
    print("\n===== OPERAÇÕES NO MONGODB =====")

    inserir_produtos(collection)

    produtos_caros = consultar_produtos_preco_maior_que(collection, 10)
    print("\nProdutos com preço > 10:")
    for produto in produtos_caros:
        print(produto)

    atualizar_preco_produto(collection, "Mouse Gamer", 99.90)

    remover_produto_por_categoria(collection, "papelaria")


def armazenar_mensagem_inicio(redis_client: redis.Redis) -> None:
    """Armazena uma string simples no Redis."""
    redis_client.set("mensagem:inicio", "Bem-vindo ao desafio NoSQL com MongoDB e Redis!")
    print("✅ String mensagem:inicio armazenada no Redis.")


def armazenar_usuario_hash(redis_client: redis.Redis) -> None:
    """Armazena dados de usuário usando hash no Redis."""
    redis_client.hset(
        "usuario:1",
        mapping={
            "nome": "Jonathan Rodrigues",
            "email": "jonathan@example.com",
        },
    )
    print("✅ Hash usuario:1 armazenado no Redis.")


def adicionar_log_acesso(redis_client: redis.Redis, acao: str) -> None:
    """Adiciona um log de acesso em uma lista Redis."""
    timestamp = datetime.now(timezone.utc).isoformat()
    log = f"{timestamp} - {acao}"
    redis_client.rpush("logs:acesso", log)


def recuperar_logs_acesso(redis_client: redis.Redis) -> List[str]:
    """Recupera todos os elementos da lista de logs."""
    return redis_client.lrange("logs:acesso", 0, -1)


def executar_operacoes_redis(redis_client: redis.Redis) -> None:
    """Executa as operações obrigatórias no Redis."""
    print("\n===== OPERAÇÕES NO REDIS =====")

    redis_client.delete("logs:acesso")

    armazenar_mensagem_inicio(redis_client)
    armazenar_usuario_hash(redis_client)

    adicionar_log_acesso(redis_client, "Usuário acessou a página inicial")
    adicionar_log_acesso(redis_client, "Usuário consultou produtos")
    adicionar_log_acesso(redis_client, "Usuário finalizou a demonstração")

    mensagem = redis_client.get("mensagem:inicio")
    usuario = redis_client.hgetall("usuario:1")
    logs = recuperar_logs_acesso(redis_client)

    print("\nMensagem recuperada:")
    print(mensagem)

    print("\nUsuário recuperado do hash:")
    print(usuario)

    print("\nLogs de acesso:")
    for log in logs:
        print(log)


def buscar_produto_com_cache(
    collection: Collection,
    redis_client: redis.Redis,
    nome_produto: str,
) -> Optional[Dict[str, Any]]:
    """
    Busca produto pelo nome usando Redis como cache.

    Fluxo:
    1. Verifica a chave produto:{nome} no Redis.
    2. Se existir, retorna os dados do cache.
    3. Se não existir, busca no MongoDB.
    4. Se encontrar no MongoDB, salva no Redis com TTL de 60 segundos.
    """
    chave_cache = f"produto:{nome_produto}"

    produto_cache = redis_client.get(chave_cache)
    if produto_cache:
        print(f"⚡ Produto '{nome_produto}' encontrado no cache Redis.")
        return json.loads(produto_cache)

    print(f"🔎 Produto '{nome_produto}' não encontrado no cache. Buscando no MongoDB...")

    produto_mongo = collection.find_one({"nome": nome_produto})
    produto_formatado = documento_produto_para_dict(produto_mongo)

    if not produto_formatado:
        print(f"⚠️ Produto '{nome_produto}' não encontrado no MongoDB.")
        return None

    redis_client.setex(
        chave_cache,
        CACHE_TTL_SECONDS,
        json.dumps(produto_formatado, ensure_ascii=False),
    )

    print(f"✅ Produto '{nome_produto}' salvo no cache Redis por {CACHE_TTL_SECONDS} segundos.")
    return produto_formatado


def executar_caso_integrado_cache(collection: Collection, redis_client: redis.Redis) -> None:
    """Demonstra o caso integrado de cache entre MongoDB e Redis."""
    print("\n===== CASO INTEGRADO: CACHE COM REDIS =====")

    redis_client.delete("produto:Mouse Gamer")

    produto_1 = buscar_produto_com_cache(collection, redis_client, "Mouse Gamer")
    print("\nPrimeira busca:")
    print(produto_1)

    produto_2 = buscar_produto_com_cache(collection, redis_client, "Mouse Gamer")
    print("\nSegunda busca:")
    print(produto_2)


def main() -> None:
    """Função principal da aplicação."""
    mongo_client = None

    try:
        mongo_uri, redis_url = carregar_variaveis_ambiente()

        mongo_client = conectar_mongo(mongo_uri)
        redis_client = conectar_redis(redis_url)

        collection = obter_colecao_produtos(mongo_client)

        executar_operacoes_mongo(collection)
        executar_operacoes_redis(redis_client)
        executar_caso_integrado_cache(collection, redis_client)

        print("\n✅ Demonstração finalizada com sucesso.")

    except Exception as erro:
        print(f"\n❌ Erro durante a execução: {erro}")

    finally:
        if mongo_client:
            mongo_client.close()
            print("🔒 Conexão com MongoDB encerrada.")


if __name__ == "__main__":
    main()
