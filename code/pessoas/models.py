from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models

from animais.models import Animal


class Perfil(models.Model):
    PAPEL = [
        ('adotante', 'Adotante'),
        ('voluntario', 'Voluntário'),
        ('gestor', 'Gestor'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
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

    animal = models.ForeignKey(Animal, on_delete=models.PROTECT, related_name='adocoes')
    solicitante = models.ForeignKey(User, on_delete=models.PROTECT, related_name='adocoes')
    data_pedido = models.DateField('data do pedido')
    status = models.CharField(max_length=20, choices=STATUS, default='analise')
    observacao = models.TextField('observação', blank=True)

    class Meta:
        verbose_name = 'Adoção'
        verbose_name_plural = 'Adoções'
        ordering = ['-data_pedido']

    def __str__(self):
        return f"{self.animal.nome} - {self.solicitante.username}"

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

    def como_dict(self):
        return {
            'id': self.id,
            'animal_id': self.animal_id,
            'animal': self.animal.nome,
            'especie': self.animal.especie.nome,
            'solicitante_id': self.solicitante_id,
            'solicitante': self.solicitante.first_name or self.solicitante.username,
            'data_pedido': self.data_pedido.isoformat(),
            'status': self.status,
            'status_label': self.get_status_display(),
            'observacao': self.observacao,
        }


class Doacao(models.Model):
    TIPO = [
        ('dinheiro', 'Dinheiro'),
        ('racao', 'Ração'),
        ('medicamento', 'Medicamento'),
        ('outro', 'Outro'),
    ]

    doador_nome = models.CharField('nome do doador', max_length=120)
    tipo = models.CharField(max_length=20, choices=TIPO)
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    descricao = models.CharField('descrição', max_length=255, blank=True)
    data = models.DateField()
    registrado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='doacoes')

    class Meta:
        verbose_name = 'Doação'
        verbose_name_plural = 'Doações'
        ordering = ['-data']

    def __str__(self):
        return f"{self.doador_nome} - {self.get_tipo_display()}"

    def como_dict(self):
        return {
            'id': self.id,
            'doador_nome': self.doador_nome,
            'tipo': self.tipo,
            'tipo_label': self.get_tipo_display(),
            'valor': str(self.valor) if self.valor is not None else None,
            'descricao': self.descricao,
            'data': self.data.isoformat(),
            'registrado_por': self.registrado_por.first_name or self.registrado_por.username,
        }
