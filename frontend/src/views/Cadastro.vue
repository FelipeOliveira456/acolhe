<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { sessao } from '../auth'
import { alternarTema, tema } from '../tema'

const router = useRouter()
const erro = ref('')
const form = reactive({
  nome: '',
  usuario: '',
  email: '',
  telefone: '',
  senha: '',
})

async function cadastrar() {
  erro.value = ''
  try {
    sessao.usuario = await api('/api/cadastro', { method: 'POST', body: { ...form } })
    router.push('/')
  } catch (e) {
    erro.value = e.message
  }
}
</script>

<template>
  <div class="card shadow-sm cartao-acesso">
    <div class="card-body p-4">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h1 class="h3 mb-0">Cadastre-se</h1>
        <button class="btn btn-outline-secondary btn-sm" type="button" @click="alternarTema">
          {{ tema === 'dark' ? 'Tema claro' : 'Tema escuro' }}
        </button>
      </div>
      <p class="text-secondary">O cadastro cria uma conta de adotante.</p>
      <div v-if="erro" class="alert alert-danger">{{ erro }}</div>
      <form @submit.prevent="cadastrar">
        <div class="mb-3">
          <label class="form-label">Nome</label>
          <input v-model="form.nome" class="form-control" required>
        </div>
        <div class="mb-3">
          <label class="form-label">Usuário</label>
          <input v-model="form.usuario" class="form-control" required>
        </div>
        <div class="mb-3">
          <label class="form-label">E-mail</label>
          <input v-model="form.email" type="email" class="form-control" required>
        </div>
        <div class="mb-3">
          <label class="form-label">Telefone</label>
          <input v-model="form.telefone" class="form-control">
        </div>
        <div class="mb-3">
          <label class="form-label">Senha</label>
          <input v-model="form.senha" type="password" class="form-control" minlength="8" required>
        </div>
        <button class="btn btn-success w-100" type="submit">Cadastrar</button>
      </form>
      <p class="mt-3 mb-0 text-center">
        Já tem conta?
        <router-link to="/login">Entrar</router-link>
      </p>
    </div>
  </div>
</template>
