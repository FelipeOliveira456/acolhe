from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

EQUIPE = ('voluntario', 'gestor')


def papel_de(user):
    if not user.is_authenticated:
        return ''
    perfil = getattr(user, 'perfil', None)
    if perfil:
        return perfil.papel
    if user.is_superuser:
        return 'gestor'
    return 'adotante'


def sem_permissao(request):
    messages.error(request, 'Você não tem permissão para acessar esta página.')
    return redirect('painel')


class PapelMixin(LoginRequiredMixin):
    papeis = ()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and self.papeis and papel_de(request.user) not in self.papeis:
            return sem_permissao(request)
        return super().dispatch(request, *args, **kwargs)


def papel_required(*papeis):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(request, *args, **kwargs):
            if papel_de(request.user) not in papeis:
                return sem_permissao(request)
            return view(request, *args, **kwargs)
        return wrapper
    return decorator
