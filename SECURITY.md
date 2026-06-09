# Observação de Segurança

Este projeto usa variáveis de ambiente para armazenar credenciais.

Não coloque as senhas diretamente no `main.py`.

Não envie o arquivo `.env` para o GitHub.

O arquivo `.gitignore` já está configurado para ignorar `.env`.

Caso alguma senha seja exposta publicamente, troque a senha imediatamente no MongoDB Atlas ou Redis Cloud.
