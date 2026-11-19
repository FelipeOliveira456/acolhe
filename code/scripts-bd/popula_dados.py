import os
import sys
import django
from datetime import date
from datetime import timedelta

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

if Especie.objects.exists() or User.objects.exists():
    print("O banco já possui dados. Execute o script deleta_dados.py antes.")
    sys.exit()

hoje = date.today()

cachorro = Especie.objects.create(nome="Cachorro")
gato = Especie.objects.create(nome="Gato")
coelho = Especie.objects.create(nome="Coelho")

central = Abrigo.objects.create(nome="Abrigo Central", cidade="Lavras", endereco="Rua das Flores, 120", capacidade=40)
felinos = Abrigo.objects.create(nome="Lar dos Felinos", cidade="Lavras", endereco="Avenida Central, 55", capacidade=20)
recanto = Abrigo.objects.create(nome="Recanto Rural", cidade="Ijaci", endereco="Estrada do Funil, km 3", capacidade=8)

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
carla = criar_usuario("carla", "carla123", "Carla Souza", "carla@acolhe.local", "voluntario", "35977771111")
adotante = criar_usuario("adotante", "adotante123", "Maria Adotante", "maria@acolhe.local", "adotante", "35966660000")
pedro = criar_usuario("pedro", "pedro123", "Pedro Lima", "pedro@acolhe.local", "adotante", "35966661111")
julia = criar_usuario("julia", "julia123", "Júlia Rocha", "julia@acolhe.local", "adotante", "35966662222")

animais = [
    {"nome": "Luna", "especie": cachorro, "abrigo": central, "sexo": "F", "porte": "M", "status": "disponivel", "data_entrada": date(2026, 2, 10), "castrado": True, "descricao": "Dócil e já vacinada. Se dá bem com crianças."},
    {"nome": "Thor", "especie": cachorro, "abrigo": central, "sexo": "M", "porte": "G", "status": "disponivel", "data_entrada": date(2026, 3, 2), "castrado": False, "descricao": "Energético, precisa de espaço para correr."},
    {"nome": "Mia", "especie": gato, "abrigo": felinos, "sexo": "F", "porte": "P", "status": "em_tratamento", "data_entrada": date(2026, 4, 18), "castrado": True, "descricao": "Em recuperação de uma pata."},
    {"nome": "Bidu", "especie": cachorro, "abrigo": central, "sexo": "M", "porte": "P", "status": "disponivel", "data_entrada": date(2026, 1, 8), "castrado": True, "descricao": "Calmo e companheiro."},
    {"nome": "Nina", "especie": gato, "abrigo": felinos, "sexo": "F", "porte": "M", "status": "disponivel", "data_entrada": date(2026, 5, 3), "castrado": True, "descricao": "Gosta de colo e de dormir no sol."},
    {"nome": "Bob", "especie": cachorro, "abrigo": central, "sexo": "M", "porte": "M", "status": "disponivel", "data_entrada": date(2026, 6, 21), "castrado": False, "descricao": "Resgatado na rodovia. Muito brincalhão."},
    {"nome": "Mel", "especie": cachorro, "abrigo": recanto, "sexo": "F", "porte": "G", "status": "disponivel", "data_entrada": date(2026, 7, 14), "castrado": True, "descricao": "Ótima guardiã, ideal para casa com quintal."},
    {"nome": "Tom", "especie": gato, "abrigo": felinos, "sexo": "M", "porte": "M", "status": "disponivel", "data_entrada": date(2026, 8, 1), "castrado": True, "descricao": "Curioso e independente."},
    {"nome": "Pipoca", "especie": coelho, "abrigo": recanto, "sexo": "F", "porte": "P", "status": "disponivel", "data_entrada": date(2026, 8, 20), "castrado": False, "descricao": "Coelha mansa, come verduras na mão."},
    {"nome": "Paçoca", "especie": cachorro, "abrigo": central, "sexo": "M", "porte": "P", "status": "em_tratamento", "data_entrada": date(2026, 9, 5), "castrado": False, "descricao": "Chegou com sarna, em tratamento com banhos."},
    {"nome": "Frida", "especie": gato, "abrigo": felinos, "sexo": "F", "porte": "P", "status": "disponivel", "data_entrada": date(2026, 9, 18), "castrado": True, "descricao": "Filhote tricolor muito carinhosa."},
    {"nome": "Rex", "especie": cachorro, "abrigo": recanto, "sexo": "M", "porte": "G", "status": "disponivel", "data_entrada": date(2026, 10, 2), "castrado": True, "descricao": "Idoso tranquilo, procura um lar para descansar."},
    {"nome": "Amora", "especie": cachorro, "abrigo": central, "sexo": "F", "porte": "M", "status": "disponivel", "data_entrada": date(2026, 10, 15), "castrado": True, "descricao": "Adora passear de coleira."},
    {"nome": "Floquinho", "especie": coelho, "abrigo": recanto, "sexo": "M", "porte": "P", "status": "disponivel", "data_entrada": date(2026, 10, 28), "castrado": False, "descricao": "Coelho branco, ainda um pouco tímido."},
    {"nome": "Salem", "especie": gato, "abrigo": felinos, "sexo": "M", "porte": "M", "status": "disponivel", "data_entrada": date(2026, 11, 4), "castrado": False, "descricao": "Gato preto brincalhão, resgatado no centro."},
    {"nome": "Kiara", "especie": cachorro, "abrigo": central, "sexo": "F", "porte": "P", "status": "disponivel", "data_entrada": date(2026, 11, 10), "castrado": False, "descricao": "Filhote resgatada com os irmãos."},
]

criados = {}
for dados in animais:
    animal = Animal(**dados)
    animal.save()
    criados[animal.nome] = animal

prontuarios = [
    {"animal": "Luna", "data": date(2026, 2, 12), "veterinario": "Dra. Clara", "descricao": "Vacinação V10 e antirrábica em dia."},
    {"animal": "Mia", "data": date(2026, 4, 20), "veterinario": "Dr. Paulo", "descricao": "Curativo na pata dianteira."},
    {"animal": "Mia", "data": date(2026, 5, 2), "veterinario": "Dr. Paulo", "descricao": "Retorno: cicatrização boa, manter repouso."},
    {"animal": "Bidu", "data": date(2026, 1, 15), "veterinario": "Dra. Clara", "descricao": "Castração realizada."},
    {"animal": "Paçoca", "data": date(2026, 9, 6), "veterinario": "Dra. Clara", "descricao": "Diagnóstico de sarna. Banhos semanais com shampoo medicamentoso."},
    {"animal": "Rex", "data": date(2026, 10, 3), "veterinario": "Dr. Paulo", "descricao": "Check-up geriátrico. Exames de sangue normais."},
    {"animal": "Frida", "data": date(2026, 9, 20), "veterinario": "Dra. Clara", "descricao": "Vermifugação e primeira dose da vacina."},
]

for dados in prontuarios:
    Prontuario.objects.create(animal=criados[dados["animal"]], data=dados["data"], veterinario=dados["veterinario"], descricao=dados["descricao"])

adocoes = [
    {"animal": "Bidu", "solicitante": adotante, "data_pedido": date(2026, 7, 1), "status": "aprovada", "observacao": "Casa com quintal."},
    {"animal": "Mel", "solicitante": julia, "data_pedido": date(2026, 8, 3), "status": "recusada", "observacao": "Moro em apartamento pequeno."},
    {"animal": "Pipoca", "solicitante": pedro, "data_pedido": date(2026, 9, 10), "status": "aprovada", "observacao": "Já tive coelhos antes."},
    {"animal": "Tom", "solicitante": julia, "data_pedido": date(2026, 10, 12), "status": "aprovada", "observacao": "Tenho tela em todas as janelas."},
    {"animal": "Nina", "solicitante": adotante, "data_pedido": hoje - timedelta(days=6), "status": "analise", "observacao": "Tenho outro gato em casa."},
    {"animal": "Thor", "solicitante": pedro, "data_pedido": hoje - timedelta(days=3), "status": "analise", "observacao": "Moro em sítio, ele vai ter bastante espaço."},
    {"animal": "Luna", "solicitante": julia, "data_pedido": hoje - timedelta(days=1), "status": "analise", "observacao": "Trabalho em casa e tenho tempo para passear."},
]

for dados in adocoes:
    Adocao.objects.create(animal=criados[dados["animal"]], solicitante=dados["solicitante"], data_pedido=dados["data_pedido"], status=dados["status"], observacao=dados["observacao"])

doacoes = [
    {"doador_nome": "Padaria São José", "tipo": "racao", "valor": None, "descricao": "20 kg de ração", "data": date(2026, 6, 5), "registrado_por": voluntario},
    {"doador_nome": "Carlos Mendes", "tipo": "dinheiro", "valor": "150.00", "descricao": "Doação mensal", "data": date(2026, 7, 10), "registrado_por": gestor},
    {"doador_nome": "Clínica Vida Animal", "tipo": "medicamento", "valor": None, "descricao": "Vermífugos e antipulgas", "data": date(2026, 8, 22), "registrado_por": carla},
    {"doador_nome": "Carlos Mendes", "tipo": "dinheiro", "valor": "150.00", "descricao": "Doação mensal", "data": date(2026, 8, 10), "registrado_por": gestor},
    {"doador_nome": "Bazar Solidário UFLA", "tipo": "dinheiro", "valor": "820.50", "descricao": "Renda do bazar de setembro", "data": date(2026, 9, 28), "registrado_por": voluntario},
    {"doador_nome": "Mercado Bom Preço", "tipo": "racao", "valor": None, "descricao": "50 kg de ração para gatos", "data": date(2026, 10, 4), "registrado_por": carla},
    {"doador_nome": "Fernanda Alves", "tipo": "outro", "valor": None, "descricao": "Cobertores e caminhas", "data": date(2026, 10, 19), "registrado_por": voluntario},
    {"doador_nome": "Carlos Mendes", "tipo": "dinheiro", "valor": "150.00", "descricao": "Doação mensal", "data": hoje - timedelta(days=8), "registrado_por": gestor},
    {"doador_nome": "Rafael Costa", "tipo": "dinheiro", "valor": "60.00", "descricao": "Doação pelo Pix", "data": hoje - timedelta(days=4), "registrado_por": carla},
    {"doador_nome": "Pet Shop Amigo Fiel", "tipo": "racao", "valor": None, "descricao": "30 kg de ração para filhotes", "data": hoje - timedelta(days=2), "registrado_por": voluntario},
]

for dados in doacoes:
    Doacao.objects.create(**dados)

print("Dados de exemplo adicionados com sucesso!")
