<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { pode } from '../auth'
import { classeStatus, dataBR } from '../formato'

const route = useRoute()
const router = useRouter()
const animal = ref(null)
const erro = ref('')
const aviso = ref('')
const observacao = ref('')
const form = reactive({ data: '', veterinario: '', descricao: '' })

async function carregar() {
  animal.value = await api(`/api/animais/${route.params.id}`)
}

onMounted(async () => {
  try {
    await carregar()
  } catch (e) {
    erro.value = e.message
  }
})

async function pedirAdocao() {
  erro.value = ''
  aviso.value = ''
  try {
    await api('/api/adocoes', {
      method: 'POST',
      body: { animal_id: animal.value.id, observacao: observacao.value },
    })
    aviso.value = 'Pedido de adoção enviado.'
    observacao.value = ''
  } catch (e) {
    erro.value = e.message
  }
}

async function registrarProntuario() {
  erro.value = ''
  try {
    await api('/api/prontuarios', {
      method: 'POST',
      body: { animal_id: animal.value.id, ...form },
    })
    form.data = ''
    form.veterinario = ''
    form.descricao = ''
    await carregar()
  } catch (e) {
    erro.value = e.message
  }
}

async function excluir() {
  if (!confirm('Excluir este animal?')) return
  try {
    await api(`/api/animais/${animal.value.id}`, { method: 'DELETE' })
    router.push('/animais')
  } catch (e) {
    erro.value = e.message
  }
}
</script>

<template>
  <router-link to="/animais">Voltar</router-link>
  <div v-if="erro" class="alert alert-danger mt-3">{{ erro }}</div>
  <div v-if="aviso" class="alert alert-success mt-3">{{ aviso }}</div>
  <div v-if="animal" class="mt-3">
    <div class="d-flex justify-content-between align-items-start">
      <div>
        <h1 class="h3">{{ animal.nome }}</h1>
        <p class="mb-1">{{ animal.especie }} · {{ animal.sexo_label }} · porte {{ animal.porte_label.toLowerCase() }}</p>
        <p class="mb-1">Abrigo: {{ animal.abrigo }}</p>
        <p class="mb-1">Entrada: {{ dataBR(animal.data_entrada) }}</p>
        <p class="mb-1">{{ animal.castrado ? 'Castrado' : 'Não castrado' }}</p>
        <span class="badge" :class="classeStatus(animal.status)">{{ animal.status_label }}</span>
        <p v-if="animal.descricao" class="mt-3">{{ animal.descricao }}</p>
      </div>
      <button v-if="pode('gestor')" class="btn btn-outline-danger btn-sm" type="button" @click="excluir">Excluir</button>
    </div>

    <div v-if="pode('adotante') && animal.status === 'disponivel'" class="card mt-4">
      <div class="card-body">
        <h2 class="h5">Pedir adoção</h2>
        <textarea v-model="observacao" class="form-control mb-2" rows="2" placeholder="Observação (opcional)"></textarea>
        <button class="btn btn-success" type="button" @click="pedirAdocao">Enviar pedido</button>
      </div>
    </div>

    <template v-if="pode('voluntario', 'gestor')">
      <h2 class="h5 mt-4">Prontuário</h2>
      <p v-if="animal.prontuarios.length === 0" class="text-secondary">Nenhum registro ainda.</p>
      <ul v-else class="list-group mb-3">
        <li v-for="item in animal.prontuarios" :key="item.id" class="list-group-item">
          <strong>{{ dataBR(item.data) }}</strong> — {{ item.veterinario }}
          <div>{{ item.descricao }}</div>
        </li>
      </ul>
      <form class="card" @submit.prevent="registrarProntuario">
        <div class="card-body">
          <h2 class="h6">Novo registro</h2>
          <div class="row g-2">
            <div class="col-md-3">
              <input v-model="form.data" type="date" class="form-control" required>
            </div>
            <div class="col-md-4">
              <input v-model="form.veterinario" class="form-control" placeholder="Veterinário" required>
            </div>
            <div class="col-md-5">
              <input v-model="form.descricao" class="form-control" placeholder="Descrição" required>
            </div>
          </div>
          <button class="btn btn-success mt-3" type="submit">Registrar</button>
        </div>
      </form>
    </template>
  </div>
</template>
