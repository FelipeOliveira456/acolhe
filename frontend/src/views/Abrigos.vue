<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api'

const lista = ref([])
const erro = ref('')
const editando = ref(null)
const form = reactive({ nome: '', cidade: '', endereco: '', capacidade: '' })

function limpar() {
  editando.value = null
  form.nome = ''
  form.cidade = ''
  form.endereco = ''
  form.capacidade = ''
}

async function carregar() {
  lista.value = await api('/api/abrigos')
}

onMounted(async () => {
  try {
    await carregar()
  } catch (e) {
    erro.value = e.message
  }
})

function editar(item) {
  editando.value = item
  form.nome = item.nome
  form.cidade = item.cidade
  form.endereco = item.endereco
  form.capacidade = item.capacidade
}

async function salvar() {
  erro.value = ''
  const body = { ...form, capacidade: Number(form.capacidade) }
  try {
    if (editando.value) {
      await api(`/api/abrigos/${editando.value.id}`, { method: 'PUT', body })
    } else {
      await api('/api/abrigos', { method: 'POST', body })
    }
    limpar()
    await carregar()
  } catch (e) {
    erro.value = e.message
  }
}

async function excluir(item) {
  if (!confirm('Excluir este abrigo?')) return
  erro.value = ''
  try {
    await api(`/api/abrigos/${item.id}`, { method: 'DELETE' })
    await carregar()
  } catch (e) {
    erro.value = e.message
  }
}
</script>

<template>
  <h1 class="h3 mb-3">Abrigos</h1>
  <div v-if="erro" class="alert alert-danger">{{ erro }}</div>
  <form class="card mb-4" @submit.prevent="salvar">
    <div class="card-body">
      <h2 class="h5">{{ editando ? 'Editar abrigo' : 'Novo abrigo' }}</h2>
      <div class="row g-2">
        <div class="col-md-4"><input v-model="form.nome" class="form-control" placeholder="Nome" required></div>
        <div class="col-md-3"><input v-model="form.cidade" class="form-control" placeholder="Cidade" required></div>
        <div class="col-md-3"><input v-model="form.endereco" class="form-control" placeholder="Endereço" required></div>
        <div class="col-md-2"><input v-model="form.capacidade" type="number" min="1" class="form-control" placeholder="Vagas" required></div>
      </div>
      <button class="btn btn-success mt-3" type="submit">Salvar</button>
      <button v-if="editando" class="btn btn-outline-secondary mt-3 ms-2" type="button" @click="limpar">Cancelar</button>
    </div>
  </form>
  <div class="table-responsive">
    <table class="table align-middle">
      <thead>
        <tr>
          <th>Nome</th>
          <th>Cidade</th>
          <th>Endereço</th>
          <th>Ocupação</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in lista" :key="item.id">
          <td>{{ item.nome }}</td>
          <td>{{ item.cidade }}</td>
          <td>{{ item.endereco }}</td>
          <td>{{ item.ocupacao }} / {{ item.capacidade }}</td>
          <td class="text-end">
            <button class="btn btn-sm btn-outline-secondary" type="button" @click="editar(item)">Editar</button>
            <button class="btn btn-sm btn-outline-danger ms-1" type="button" @click="excluir(item)">Excluir</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
