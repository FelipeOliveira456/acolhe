<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api'
import { pode, sessao } from '../auth'

const dados = ref(null)
const erro = ref('')

onMounted(async () => {
  try {
    dados.value = await api('/api/painel')
  } catch (e) {
    erro.value = e.message
  }
})
</script>

<template>
  <h1 class="h3 mb-3">Olá, {{ sessao.usuario.nome }}</h1>
  <p class="text-secondary">Você está como {{ sessao.usuario.papel_label.toLowerCase() }}.</p>
  <div v-if="erro" class="alert alert-danger">{{ erro }}</div>
  <div v-if="dados" class="row g-3">
    <div class="col-md-4">
      <div class="card h-100">
        <div class="card-body">
          <div class="text-secondary">Disponíveis</div>
          <div class="display-6">{{ dados.disponiveis }}</div>
        </div>
      </div>
    </div>
    <div v-if="pode('voluntario', 'gestor')" class="col-md-4">
      <div class="card h-100">
        <div class="card-body">
          <div class="text-secondary">Em tratamento</div>
          <div class="display-6">{{ dados.em_tratamento }}</div>
        </div>
      </div>
    </div>
    <div v-if="pode('voluntario', 'gestor')" class="col-md-4">
      <div class="card h-100">
        <div class="card-body">
          <div class="text-secondary">Adotados</div>
          <div class="display-6">{{ dados.adotados }}</div>
        </div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card h-100">
        <div class="card-body">
          <div class="text-secondary">{{ pode('adotante') ? 'Minhas adoções em análise' : 'Adoções em análise' }}</div>
          <div class="display-6">{{ dados.em_analise }}</div>
        </div>
      </div>
    </div>
    <div v-if="pode('adotante')" class="col-md-4">
      <div class="card h-100">
        <div class="card-body">
          <div class="text-secondary">Minhas adoções</div>
          <div class="display-6">{{ dados.minhas_adocoes }}</div>
        </div>
      </div>
    </div>
    <div v-if="pode('voluntario', 'gestor')" class="col-md-4">
      <div class="card h-100">
        <div class="card-body">
          <div class="text-secondary">Doações registradas</div>
          <div class="display-6">{{ dados.doacoes }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
