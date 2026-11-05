from functools import wraps

from django.http import JsonResponse

from gestao_ong.util import papel_de


def login_json(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'erro': 'Faça login para continuar.'}, status=401)
        return view(request, *args, **kwargs)
    return wrapper


def papel_json(*papeis):
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'erro': 'Faça login para continuar.'}, status=401)
            if papel_de(request.user) not in papeis:
                return JsonResponse({'erro': 'Você não tem permissão para esta ação.'}, status=403)
            return view(request, *args, **kwargs)
        return wrapper
    return decorator
