<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api'
import { pode } from '../auth'
import AnimalForm from '../components/AnimalForm.vue'
import { classeStatus, dataBR } from '../formato'

const lista = ref([])
const especies = ref([])
const abrigos = ref([])
const erro = ref('')
const formAberto = ref(false)
const editando = ref(null)
const filtros = reactive({ q: '', status: '', especie: '' })

async function carregar() {
  const params = new URLSearchParams()
  if (filtros.q) params.set('q', filtros.q)
  if (filtros.status) params.set('status', filtros.status)
  if (filtros.especie) params.set('especie', filtros.especie)
  const query = params.toString()
  lista.value = await api('/api/animais' + (query ? `?${query}` : ''))
}

onMounted(async () => {
  try {
    await carregar()
    if (pode('voluntario', 'gestor')) {
      especies.value = await api('/api/especies')
      abrigos.value = await api('/api/abrigos')
    }
  } catch (e) {
    erro.value = e.message
  }
})

function novo() {
  editando.value = null
  formAberto.value = true
}

function editar(animal) {
  editando.value = animal
  formAberto.value = true
}

async function salvar(dados) {
  erro.value = ''
  try {
    if (editando.value) {
      await api(`/api/animais/${editando.value.id}`, { method: 'PUT', body: dados })
    } else {
      await api('/api/animais', { method: 'POST', body: dados })
    }
    formAberto.value = false
    await carregar()
  } catch (e) {
    erro.value = e.message
  }
}
</script>

<template>
  <div class="d-flex justify-content-between align-items-center mb-3">
    <h1 class="h3 mb-0">Animais</h1>
    <button v-if="pode('voluntario', 'gestor')" class="btn btn-success" type="button" @click="novo">Novo animal</button>
  </div>
  <div v-if="erro" class="alert alert-danger">{{ erro }}</div>
  <AnimalForm
    v-if="formAberto"
    :animal="editando"
    :especies="especies"
    :abrigos="abrigos"
    @salvar="salvar"
    @cancelar="formAberto = false"
  />
  <form class="row g-2 mb-3" @submit.prevent="carregar">
    <div class="col-md-4">
      <input v-model="filtros.q" class="form-control" placeholder="Buscar por nome">
    </div>
    <div v-if="pode('voluntario', 'gestor')" class="col-md-3">
      <select v-model="filtros.status" class="form-select">
        <option value="">Todos os status</option>
        <option value="disponivel">Disponível</option>
        <option value="em_tratamento">Em tratamento</option>
        <option value="adotado">Adotado</option>
      </select>
    </div>
    <div v-if="pode('voluntario', 'gestor')" class="col-md-3">
      <select v-model="filtros.especie" class="form-select">
        <option value="">Todas as espécies</option>
        <option v-for="item in especies" :key="item.id" :value="String(item.id)">{{ item.nome }}</option>
      </select>
    </div>
    <div class="col-md-2">
      <button class="btn btn-outline-success w-100" type="submit">Filtrar</button>
    </div>
  </form>
  <div class="table-responsive">
    <table class="table table-hover align-middle">
      <thead>
        <tr>
          <th>Nome</th>
          <th>Espécie</th>
          <th>Abrigo</th>
          <th>Porte</th>
          <th>Status</th>
          <th>Entrada</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="lista.length === 0">
          <td colspan="7" class="text-secondary">Nenhum animal encontrado.</td>
        </tr>
        <tr v-for="animal in lista" :key="animal.id">
          <td>{{ animal.nome }}</td>
          <td>{{ animal.especie }}</td>
          <td>{{ animal.abrigo }}</td>
          <td>{{ animal.porte_label }}</td>
          <td><span class="badge" :class="classeStatus(animal.status)">{{ animal.status_label }}</span></td>
          <td>{{ dataBR(animal.data_entrada) }}</td>
          <td class="text-end">
            <router-link class="btn btn-sm btn-outline-success" :to="`/animais/${animal.id}`">Ver</router-link>
            <button v-if="pode('voluntario', 'gestor')" class="btn btn-sm btn-outline-secondary ms-1" type="button" @click="editar(animal)">Editar</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
