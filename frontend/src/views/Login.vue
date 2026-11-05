<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { sessao } from '../auth'
import { alternarTema, tema } from '../tema'

const router = useRouter()
const erro = ref('')
const form = reactive({ usuario: '', senha: '' })

async function entrar() {
  erro.value = ''
  try {
    sessao.usuario = await api('/api/login', { method: 'POST', body: { ...form } })
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
        <h1 class="h3 mb-0">Acolhe</h1>
        <button class="btn btn-outline-secondary btn-sm" type="button" @click="alternarTema">
          {{ tema === 'dark' ? 'Tema claro' : 'Tema escuro' }}
        </button>
      </div>
      <p class="text-secondary">Gestão de ONG animal. Entre com seu usuário e senha.</p>
      <div v-if="erro" class="alert alert-danger">{{ erro }}</div>
      <form @submit.prevent="entrar">
        <div class="mb-3">
          <label class="form-label">Usuário</label>
          <input v-model="form.usuario" class="form-control" required>
        </div>
        <div class="mb-3">
          <label class="form-label">Senha</label>
          <input v-model="form.senha" type="password" class="form-control" required>
        </div>
        <button class="btn btn-success w-100" type="submit">Entrar</button>
      </form>
      <p class="mt-3 mb-0 text-center">
        Não tem conta?
        <router-link to="/cadastro">Cadastre-se</router-link>
      </p>
    </div>
  </div>
</template>
