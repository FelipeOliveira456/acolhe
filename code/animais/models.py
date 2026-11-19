from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


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

    def ocupacao(self):
        return self.animais.exclude(status='adotado').count()

    def clean(self):
        if not self.pk or self.capacidade is None:
            return
        ocupados = self.ocupacao()
        if self.capacidade < ocupados:
            raise ValidationError({'capacidade': f'O abrigo já tem {ocupados} animais. A capacidade não pode ser menor que isso.'})


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
    CORES = {
        'disponivel': 'success',
        'em_tratamento': 'warning',
        'adotado': 'secondary',
    }

    nome = models.CharField(max_length=80)
    especie = models.ForeignKey(Especie, on_delete=models.PROTECT, related_name='animais', verbose_name='espécie')
    abrigo = models.ForeignKey(Abrigo, on_delete=models.PROTECT, related_name='animais')
    sexo = models.CharField(max_length=1, choices=SEXO)
    porte = models.CharField(max_length=1, choices=PORTE)
    status = models.CharField(max_length=20, choices=STATUS, default='disponivel')
    data_entrada = models.DateField('data de entrada')
    castrado = models.BooleanField(default=False)
    descricao = models.TextField('descrição', blank=True)
    foto = models.ImageField(upload_to='animais/', blank=True)

    class Meta:
        verbose_name = 'Animal'
        verbose_name_plural = 'Animais'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} - {self.especie}"

    def get_absolute_url(self):
        return reverse('animal_detalhe', args=[self.pk])

    def cor_status(self):
        return self.CORES[self.status]

    def clean(self):
        if not self.abrigo_id or self.status == 'adotado':
            return
        ocupados = Animal.objects.filter(abrigo_id=self.abrigo_id).exclude(status='adotado').exclude(pk=self.pk)
        if ocupados.count() >= self.abrigo.capacidade:
            raise ValidationError({'abrigo': 'O abrigo escolhido está lotado.'})


class Prontuario(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='prontuarios')
    data = models.DateField()
    veterinario = models.CharField('veterinário', max_length=120)
    descricao = models.TextField('descrição')

    class Meta:
        verbose_name = 'Prontuário'
        verbose_name_plural = 'Prontuários'
        ordering = ['-data']

    def __str__(self):
        return f"{self.animal.nome} - {self.data}"
