from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Especie(models.Model):
    nome = models.CharField(max_length=80, unique=True)

    class Meta:
        verbose_name = 'Espécie'
        verbose_name_plural = 'Espécies'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Abrigo(models.Model):
    nome = models.CharField(max_length=120)
    cidade = models.CharField(max_length=80)
    endereco = models.CharField('endereço', max_length=255)
    capacidade = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Abrigo'
        verbose_name_plural = 'Abrigos'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} - {self.cidade}"

    def como_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'cidade': self.cidade,
            'endereco': self.endereco,
            'capacidade': self.capacidade,
            'ocupacao': self.animais.exclude(status='adotado').count(),
        }


class Animal(models.Model):
    SEXO = [
        ('M', 'Macho'),
        ('F', 'Fêmea'),
    ]
    PORTE = [
        ('P', 'Pequeno'),
        ('M', 'Médio'),
        ('G', 'Grande'),
    ]
    STATUS = [
        ('disponivel', 'Disponível'),
        ('em_tratamento', 'Em tratamento'),
        ('adotado', 'Adotado'),
    ]

    nome = models.CharField(max_length=80)
    especie = models.ForeignKey(Especie, on_delete=models.PROTECT, related_name='animais')
    abrigo = models.ForeignKey(Abrigo, on_delete=models.PROTECT, related_name='animais')
    sexo = models.CharField(max_length=1, choices=SEXO)
    porte = models.CharField(max_length=1, choices=PORTE)
    status = models.CharField(max_length=20, choices=STATUS, default='disponivel')
    data_entrada = models.DateField('data de entrada')
    castrado = models.BooleanField(default=False)
    descricao = models.TextField('descrição', blank=True)

    class Meta:
        verbose_name = 'Animal'
        verbose_name_plural = 'Animais'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} - {self.especie}"

    def clean(self):
        if not self.abrigo_id or self.status == 'adotado':
            return
        ocupados = Animal.objects.filter(abrigo_id=self.abrigo_id).exclude(status='adotado').exclude(pk=self.pk)
        if ocupados.count() >= self.abrigo.capacidade:
            raise ValidationError('O abrigo escolhido está lotado.')

    def como_dict(self, com_prontuario=False):
        dados = {
            'id': self.id,
            'nome': self.nome,
            'especie_id': self.especie_id,
            'especie': self.especie.nome,
            'abrigo_id': self.abrigo_id,
            'abrigo': self.abrigo.nome,
            'sexo': self.sexo,
            'sexo_label': self.get_sexo_display(),
            'porte': self.porte,
            'porte_label': self.get_porte_display(),
            'status': self.status,
            'status_label': self.get_status_display(),
            'data_entrada': self.data_entrada.isoformat(),
            'castrado': self.castrado,
            'descricao': self.descricao,
        }
        if com_prontuario:
            dados['prontuarios'] = [item.como_dict() for item in self.prontuarios.all()]
        return dados


class Prontuario(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='prontuarios')
    data = models.DateField()
    veterinario = models.CharField(max_length=120)
    descricao = models.TextField('descrição')

    class Meta:
        verbose_name = 'Prontuário'
        verbose_name_plural = 'Prontuários'
        ordering = ['-data']

    def __str__(self):
        return f"{self.animal.nome} - {self.data}"

    def como_dict(self):
        return {
            'id': self.id,
            'animal_id': self.animal_id,
            'data': self.data.isoformat(),
            'veterinario': self.veterinario,
            'descricao': self.descricao,
        }
