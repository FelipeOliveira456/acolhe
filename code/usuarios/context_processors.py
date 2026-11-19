from .permissoes import EQUIPE
from .permissoes import papel_de


def papel(request):
    atual = papel_de(request.user)
    return {
        'papel': atual,
        'equipe': atual in EQUIPE,
    }
