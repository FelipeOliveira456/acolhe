import os
import sys
import django

# Caminho base do projeto (um nível acima da pasta scripts-bd)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gestao_ong.settings")
django.setup()

from django.contrib.auth.models import User
from animais.models import Abrigo
from animais.models import Animal
from animais.models import Especie
from pessoas.models import Adocao
from pessoas.models import Doacao

# A ordem importa: adoções e doações protegem animais e usuários.
total = 0
for modelo in (Adocao, Doacao, Animal, Abrigo, Especie, User):
    quantidade, _ = modelo.objects.all().delete()
    total += quantidade

print(f"Todos os dados foram deletados! Total de registros deletados: {total}")
