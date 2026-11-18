"""Camada Model: acesso ao banco e regras de negócio.

Cada função recebe a conexão (`db`) como primeiro argumento. Assim as regras
podem ser testadas com pytest sem passar pelas rotas.
"""


class RegraNegocioError(Exception):
    """Violação de regra de negócio. A mensagem é exibida ao usuário."""
