from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from animais.models import Animal


class Perfil(models.Model):
    PAPEL = [
        ('adotante', 'Adotante'),
        ('voluntario', 'Voluntário'),
        ('gestor', 'Gestor'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil', verbose_name='usuário')
    papel = models.CharField(max_length=20, choices=PAPEL)
    telefone = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f"{self.usuario.username} - {self.get_papel_display()}"


class Adocao(models.Model):
    STATUS = [
        ('analise', 'Em análise'),
        ('aprovada', 'Aprovada'),
        ('recusada', 'Recusada'),
    ]
    CORES = {
        'analise': 'warning',
        'aprovada': 'success',
        'recusada': 'secondary',
    }

    animal = models.ForeignKey(Animal, on_delete=models.PROTECT, related_name='adocoes')
    solicitante = models.ForeignKey(User, on_delete=models.PROTECT, related_name='adocoes')
    data_pedido = models.DateField('data do pedido')
    status = models.CharField(max_length=20, choices=STATUS, default='analise')
    observacao = models.TextField('observação', blank=True)

    class Meta:
        verbose_name = 'Adoção'
        verbose_name_plural = 'Adoções'
        ordering = ['-data_pedido', '-id']

    def __str__(self):
        return f"{self.animal.nome} - {self.solicitante.username}"

    def cor_status(self):
        return self.CORES[self.status]

    def clean(self):
        if self.status != 'aprovada' or not self.animal_id:
            return
        anterior = Adocao.objects.filter(pk=self.pk).values_list('status', flat=True).first()
        if anterior != 'aprovada' and self.animal.status != 'disponivel':
            raise ValidationError('Este animal não está disponível para adoção.')

    def save(self, *args, **kwargs):
        anterior = Adocao.objects.filter(pk=self.pk).values_list('status', flat=True).first()
        super().save(*args, **kwargs)

        animal = self.animal
        if self.status == 'aprovada':
            animal.status = 'adotado'
            animal.save()
            Adocao.objects.filter(animal=animal, status='analise').exclude(pk=self.pk).update(status='recusada')
        elif anterior == 'aprovada':
            if not Adocao.objects.filter(animal=animal, status='aprovada').exists():
                animal.status = 'disponivel'
                animal.save()


class Doacao(models.Model):
    TIPO = [
        ('dinheiro', 'Dinheiro'),
        ('racao', 'Ração'),
        ('medicamento', 'Medicamento'),
        ('outro', 'Outro'),
    ]
    ICONES = {
        'dinheiro': 'fa-money-bill-wave',
        'racao': 'fa-bone',
        'medicamento': 'fa-pills',
        'outro': 'fa-box-open',
    }

    doador_nome = models.CharField('nome do doador', max_length=120)
    tipo = models.CharField(max_length=20, choices=TIPO)
    valor = models.DecimalField('valor (R$)', max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    descricao = models.CharField('descrição', max_length=255, blank=True)
    data = models.DateField()
    registrado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='doacoes', verbose_name='registrado por')

    class Meta:
        verbose_name = 'Doação'
        verbose_name_plural = 'Doações'
        ordering = ['-data', '-id']

    def __str__(self):
        return f"{self.doador_nome} - {self.get_tipo_display()}"

    def icone(self):
        return self.ICONES[self.tipo]

    def clean(self):
        if self.tipo == 'dinheiro' and self.valor is None:
            raise ValidationError({'valor': 'Informe o valor da doação em dinheiro.'})
