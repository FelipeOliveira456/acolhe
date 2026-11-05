<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api'

const lista = ref([])
const erro = ref('')
const form = reactive({ nome: '', usuario: '', email: '', telefone: '', senha: '' })

async function carregar() {
  lista.value = await api('/api/voluntarios')
}

onMounted(async () => {
  try {
    await carregar()
  } catch (e) {
    erro.value = e.message
  }
})

async function salvar() {
  erro.value = ''
  try {
    await api('/api/voluntarios', { method: 'POST', body: { ...form } })
    form.nome = ''
    form.usuario = ''
    form.email = ''
    form.telefone = ''
    form.senha = ''
    await carregar()
  } catch (e) {
    erro.value = e.message
  }
}
</script>

<template>
  <h1 class="h3 mb-3">Voluntários</h1>
  <div v-if="erro" class="alert alert-danger">{{ erro }}</div>
  <form class="card mb-4" @submit.prevent="salvar">
    <div class="card-body">
      <h2 class="h5">Novo voluntário</h2>
      <p class="text-secondary">A conta já entra com permissão de voluntário.</p>
      <div class="row g-2">
        <div class="col-md-4"><input v-model="form.nome" class="form-control" placeholder="Nome" required></div>
        <div class="col-md-4"><input v-model="form.usuario" class="form-control" placeholder="Usuário" required></div>
        <div class="col-md-4"><input v-model="form.email" type="email" class="form-control" placeholder="E-mail" required></div>
        <div class="col-md-4"><input v-model="form.telefone" class="form-control" placeholder="Telefone"></div>
        <div class="col-md-4"><input v-model="form.senha" type="password" minlength="8" class="form-control" placeholder="Senha" required></div>
      </div>
      <button class="btn btn-success mt-3" type="submit">Cadastrar</button>
    </div>
  </form>
  <div class="table-responsive">
    <table class="table align-middle">
      <thead>
        <tr>
          <th>Nome</th>
          <th>Usuário</th>
          <th>E-mail</th>
          <th>Telefone</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="lista.length === 0">
          <td colspan="4" class="text-secondary">Nenhum voluntário cadastrado.</td>
        </tr>
        <tr v-for="item in lista" :key="item.id">
          <td>{{ item.nome }}</td>
          <td>{{ item.usuario }}</td>
          <td>{{ item.email }}</td>
          <td>{{ item.telefone }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
