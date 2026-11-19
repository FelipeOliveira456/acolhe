from django.shortcuts import render

from animais.models import Abrigo
from animais.models import Animal
from pessoas.models import Adocao


def principal(request):
    context = {
        'disponiveis': Animal.objects.filter(status='disponivel').count(),
        'adotados': Adocao.objects.filter(status='aprovada').count(),
        'abrigos': Abrigo.objects.count(),
        'animais': Animal.objects.filter(status='disponivel').select_related('especie').order_by('-data_entrada')[:4],
    }
    return render(request, 'principal.html', context)
