import os
import sys
import django
from datetime import date

# Caminho base do projeto (um nível acima da pasta scripts-bd)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gestao_ong.settings")
django.setup()

from django.contrib.auth.models import User
from animais.models import Abrigo
from animais.models import Animal
from animais.models import Especie
from animais.models import Prontuario
from pessoas.models import Adocao
from pessoas.models import Doacao
from pessoas.models import Perfil

if Especie.objects.exists():
    print("O banco já possui dados. Execute o script deleta_dados.py antes.")
    sys.exit()

cachorro = Especie.objects.create(nome="Cachorro")
gato = Especie.objects.create(nome="Gato")

central = Abrigo.objects.create(nome="Abrigo Central", cidade="Lavras", endereco="Rua das Flores, 120", capacidade=40)
felinos = Abrigo.objects.create(nome="Lar dos Felinos", cidade="Lavras", endereco="Avenida Central, 55", capacidade=20)

def criar_usuario(username, senha, nome, email, papel, telefone, staff=False, superuser=False):
    user = User.objects.create_user(
        username=username,
        password=senha,
        email=email,
        first_name=nome,
        is_staff=staff,
        is_superuser=superuser,
    )
    Perfil.objects.create(usuario=user, papel=papel, telefone=telefone)
    return user

criar_usuario("admin", "admin123", "Administrador", "admin@acolhe.local", "gestor", "35999990000", True, True)
gestor = criar_usuario("gestor", "gestor123", "Ana Gestora", "ana@acolhe.local", "gestor", "35988880000", True, True)
voluntario = criar_usuario("voluntario", "voluntario123", "João Voluntário", "joao@acolhe.local", "voluntario", "35977770000")
adotante = criar_usuario("adotante", "adotante123", "Maria Adotante", "maria@acolhe.local", "adotante", "35966660000")

luna = Animal.objects.create(nome="Luna", especie=cachorro, abrigo=central, sexo="F", porte="M", status="disponivel", data_entrada=date(2026, 2, 10), castrado=True, descricao="Dócil e já vacinada.")
Animal.objects.create(nome="Thor", especie=cachorro, abrigo=central, sexo="M", porte="G", status="disponivel", data_entrada=date(2026, 3, 2), castrado=False, descricao="Energético, precisa de espaço.")
mia = Animal.objects.create(nome="Mia", especie=gato, abrigo=felinos, sexo="F", porte="P", status="em_tratamento", data_entrada=date(2026, 4, 18), castrado=True, descricao="Em recuperação de uma pata.")
bidu = Animal.objects.create(nome="Bidu", especie=cachorro, abrigo=central, sexo="M", porte="P", status="adotado", data_entrada=date(2026, 1, 8), castrado=True, descricao="Calmo e companheiro.")
nina = Animal.objects.create(nome="Nina", especie=gato, abrigo=felinos, sexo="F", porte="M", status="disponivel", data_entrada=date(2026, 5, 3), castrado=True, descricao="Gosta de colo.")
Animal.objects.create(nome="Bob", especie=cachorro, abrigo=central, sexo="M", porte="M", status="disponivel", data_entrada=date(2026, 6, 21), castrado=False, descricao="Resgatado na rodovia.")

Prontuario.objects.create(animal=luna, data=date(2026, 2, 12), veterinario="Dra. Clara", descricao="Vacinação em dia.")
Prontuario.objects.create(animal=mia, data=date(2026, 4, 20), veterinario="Dr. Paulo", descricao="Curativo na pata dianteira.")
Prontuario.objects.create(animal=bidu, data=date(2026, 1, 15), veterinario="Dra. Clara", descricao="Castração realizada.")

Adocao.objects.create(animal=bidu, solicitante=adotante, data_pedido=date(2026, 7, 1), status="aprovada", observacao="Casa com quintal.")
Adocao.objects.create(animal=nina, solicitante=adotante, data_pedido=date(2026, 8, 12), status="analise", observacao="Tem outro gato em casa.")

Doacao.objects.create(doador_nome="Padaria São José", tipo="racao", valor=None, descricao="20 kg de ração", data=date(2026, 6, 5), registrado_por=voluntario)
Doacao.objects.create(doador_nome="Carlos Mendes", tipo="dinheiro", valor="150.00", descricao="Doação mensal", data=date(2026, 7, 10), registrado_por=gestor)

print("Dados de exemplo adicionados com sucesso!")
