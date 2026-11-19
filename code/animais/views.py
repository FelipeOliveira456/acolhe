from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.db.models import ProtectedError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from usuarios.permissoes import EQUIPE
from usuarios.permissoes import PapelMixin
from usuarios.permissoes import papel_de
from usuarios.permissoes import papel_required
from .forms import AbrigoForm
from .forms import AnimalForm
from .forms import EspecieForm
from .forms import ProntuarioForm
from .models import Abrigo
from .models import Animal
from .models import Especie
from .models import Prontuario


class ExclusaoMixin(PapelMixin, SuccessMessageMixin):
    papeis = ('gestor',)
    template_name = 'confirmar_exclusao.html'
    mensagem_protegido = 'Não é possível excluir este registro.'

    def get_voltar(self):
        return self.get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['voltar'] = self.get_voltar()
        return context

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, self.mensagem_protegido)
            return redirect(self.get_voltar())


class AnimalListView(LoginRequiredMixin, ListView):
    model = Animal
    template_name = 'animais.html'
    context_object_name = 'animais'
    paginate_by = 12

    def get_queryset(self):
        consulta = Animal.objects.select_related('especie', 'abrigo')
        filtros = self.request.GET
        if papel_de(self.request.user) in EQUIPE:
            if filtros.get('status'):
                consulta = consulta.filter(status=filtros['status'])
            if filtros.get('abrigo', '').isdigit():
                consulta = consulta.filter(abrigo_id=filtros['abrigo'])
        else:
            consulta = consulta.filter(status='disponivel')
        if filtros.get('especie', '').isdigit():
            consulta = consulta.filter(especie_id=filtros['especie'])
        if filtros.get('porte'):
            consulta = consulta.filter(porte=filtros['porte'])
        if filtros.get('sexo'):
            consulta = consulta.filter(sexo=filtros['sexo'])
        if filtros.get('q'):
            consulta = consulta.filter(Q(nome__icontains=filtros['q']) | Q(descricao__icontains=filtros['q']))
        return consulta

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parametros = self.request.GET.copy()
        parametros.pop('page', None)
        context.update({
            'busca': self.request.GET,
            'filtros': parametros.urlencode() + '&' if parametros else '',
            'especies': Especie.objects.all(),
            'abrigos': Abrigo.objects.all(),
            'sexos': Animal.SEXO,
            'portes': Animal.PORTE,
            'situacoes': Animal.STATUS,
        })
        return context


class AnimalDetailView(LoginRequiredMixin, DetailView):
    model = Animal
    template_name = 'animal_detalhe.html'
    context_object_name = 'animal'

    def get_queryset(self):
        consulta = Animal.objects.select_related('especie', 'abrigo')
        if papel_de(self.request.user) not in EQUIPE:
            consulta = consulta.filter(Q(status='disponivel') | Q(adocoes__solicitante=self.request.user)).distinct()
        return consulta

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        animal = self.object
        if papel_de(self.request.user) in EQUIPE:
            context['prontuarios'] = animal.prontuarios.all()
            context['form_prontuario'] = ProntuarioForm(initial={'data': timezone.localdate()})
            context['adocoes'] = animal.adocoes.select_related('solicitante')
        else:
            context['meu_pedido'] = animal.adocoes.filter(solicitante=self.request.user).order_by('-data_pedido', '-id').first()
        return context


class AnimalCreateView(PapelMixin, SuccessMessageMixin, CreateView):
    papeis = EQUIPE
    model = Animal
    form_class = AnimalForm
    template_name = 'formulario.html'
    success_message = 'Animal cadastrado com sucesso!'
    extra_context = {
        'titulo': 'Novo animal',
        'icone': 'fa-dog',
        'voltar': reverse_lazy('animais'),
    }


class AnimalUpdateView(PapelMixin, SuccessMessageMixin, UpdateView):
    papeis = EQUIPE
    model = Animal
    form_class = AnimalForm
    template_name = 'formulario.html'
    success_message = 'Dados do animal atualizados com sucesso!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': f'Editar {self.object.nome}',
            'icone': 'fa-dog',
            'voltar': self.object.get_absolute_url(),
        })
        return context


class AnimalDeleteView(ExclusaoMixin, DeleteView):
    model = Animal
    success_url = reverse_lazy('animais')
    success_message = 'Animal excluído com sucesso!'
    mensagem_protegido = 'Não é possível excluir: este animal possui pedidos de adoção.'

    def get_voltar(self):
        return self.object.get_absolute_url()


@papel_required(*EQUIPE)
def prontuario_novo(request, pk):
    animal = get_object_or_404(Animal, pk=pk)
    if request.method == 'POST':
        form = ProntuarioForm(request.POST)
        if form.is_valid():
            prontuario = form.save(commit=False)
            prontuario.animal = animal
            prontuario.save()
            messages.success(request, 'Registro adicionado ao prontuário.')
        else:
            messages.error(request, 'Preencha a data, o veterinário e a descrição do atendimento.')
    return redirect(animal)


class ProntuarioDeleteView(ExclusaoMixin, DeleteView):
    model = Prontuario
    success_message = 'Registro do prontuário excluído.'

    def get_success_url(self):
        return self.object.animal.get_absolute_url()


class AbrigoListView(PapelMixin, ListView):
    papeis = EQUIPE
    template_name = 'abrigos.html'
    context_object_name = 'abrigos'

    def get_queryset(self):
        return Abrigo.objects.annotate(
            ocupados=Count('animais', filter=~Q(animais__status='adotado')),
            total=Count('animais'),
        )


class AbrigoCreateView(PapelMixin, SuccessMessageMixin, CreateView):
    papeis = ('gestor',)
    model = Abrigo
    form_class = AbrigoForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('abrigos')
    success_message = 'Abrigo cadastrado com sucesso!'
    extra_context = {
        'titulo': 'Novo abrigo',
        'icone': 'fa-home',
        'voltar': reverse_lazy('abrigos'),
    }


class AbrigoUpdateView(PapelMixin, SuccessMessageMixin, UpdateView):
    papeis = ('gestor',)
    model = Abrigo
    form_class = AbrigoForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('abrigos')
    success_message = 'Abrigo atualizado com sucesso!'
    extra_context = {
        'titulo': 'Editar abrigo',
        'icone': 'fa-home',
        'voltar': reverse_lazy('abrigos'),
    }


class AbrigoDeleteView(ExclusaoMixin, DeleteView):
    model = Abrigo
    success_url = reverse_lazy('abrigos')
    success_message = 'Abrigo excluído com sucesso!'
    mensagem_protegido = 'Não é possível excluir: existem animais cadastrados neste abrigo.'


class EspecieListView(PapelMixin, ListView):
    papeis = ('gestor',)
    template_name = 'especies.html'
    context_object_name = 'especies'

    def get_queryset(self):
        return Especie.objects.annotate(total=Count('animais'))


class EspecieCreateView(PapelMixin, SuccessMessageMixin, CreateView):
    papeis = ('gestor',)
    model = Especie
    form_class = EspecieForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('especies')
    success_message = 'Espécie cadastrada com sucesso!'
    extra_context = {
        'titulo': 'Nova espécie',
        'icone': 'fa-tags',
        'voltar': reverse_lazy('especies'),
    }


class EspecieUpdateView(PapelMixin, SuccessMessageMixin, UpdateView):
    papeis = ('gestor',)
    model = Especie
    form_class = EspecieForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('especies')
    success_message = 'Espécie atualizada com sucesso!'
    extra_context = {
        'titulo': 'Editar espécie',
        'icone': 'fa-tags',
        'voltar': reverse_lazy('especies'),
    }


class EspecieDeleteView(ExclusaoMixin, DeleteView):
    model = Especie
    success_url = reverse_lazy('especies')
    success_message = 'Espécie excluída com sucesso!'
    mensagem_protegido = 'Não é possível excluir: existem animais cadastrados com esta espécie.'
