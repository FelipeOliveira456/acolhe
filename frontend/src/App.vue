<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from './api'
import { pode, sessao } from './auth'
import { alternarTema, tema } from './tema'

const route = useRoute()
const router = useRouter()
const convidado = computed(() => route.meta.guest)

async function sair() {
  await api('/api/logout', { method: 'POST' })
  sessao.usuario = null
  router.push('/login')
}
</script>

<template>
  <div v-if="!sessao.pronto" class="text-center py-5">Carregando...</div>
  <template v-else>
    <nav v-if="!convidado && sessao.usuario" class="navbar navbar-expand-lg navbar-dark bg-success">
      <div class="container">
        <router-link class="navbar-brand" to="/">Acolhe</router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#menu">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div id="menu" class="collapse navbar-collapse">
          <ul class="navbar-nav me-auto">
            <li class="nav-item"><router-link class="nav-link" to="/">Início</router-link></li>
            <li class="nav-item"><router-link class="nav-link" to="/animais">Animais</router-link></li>
            <li class="nav-item"><router-link class="nav-link" to="/adocoes">Adoções</router-link></li>
            <li v-if="pode('voluntario', 'gestor')" class="nav-item">
              <router-link class="nav-link" to="/doacoes">Doações</router-link>
            </li>
            <li v-if="pode('gestor')" class="nav-item">
              <router-link class="nav-link" to="/abrigos">Abrigos</router-link>
            </li>
            <li v-if="pode('gestor')" class="nav-item">
              <router-link class="nav-link" to="/voluntarios">Voluntários</router-link>
            </li>
          </ul>
          <div class="d-flex align-items-center gap-2">
            <button class="btn btn-outline-light btn-sm" type="button" @click="alternarTema">
              {{ tema === 'dark' ? 'Tema claro' : 'Tema escuro' }}
            </button>
            <a v-if="sessao.usuario.is_staff" class="btn btn-outline-light btn-sm" href="/admin/" target="_blank">Admin</a>
            <span class="text-white small">{{ sessao.usuario.nome }} ({{ sessao.usuario.papel_label }})</span>
            <button class="btn btn-light btn-sm" type="button" @click="sair">Sair</button>
          </div>
        </div>
      </div>
    </nav>
    <main class="container py-4">
      <router-view />
    </main>
  </template>
</template>
