<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api'
import { pode } from '../auth'
import { classeStatus, dataBR } from '../formato'

const lista = ref([])
const erro = ref('')

async function carregar() {
  lista.value = await api('/api/adocoes')
}

onMounted(async () => {
  try {
    await carregar()
  } catch (e) {
    erro.value = e.message
  }
})

async function atualizar(item, status) {
  erro.value = ''
  try {
    await api(`/api/adocoes/${item.id}`, { method: 'PUT', body: { status } })
    await carregar()
  } catch (e) {
    erro.value = e.message
    await carregar()
  }
}
</script>

<template>
  <h1 class="h3 mb-3">Adoções</h1>
  <div v-if="erro" class="alert alert-danger">{{ erro }}</div>
  <div class="table-responsive">
    <table class="table align-middle">
      <thead>
        <tr>
          <th>Animal</th>
          <th>Espécie</th>
          <th v-if="!pode('adotante')">Solicitante</th>
          <th>Data</th>
          <th>Status</th>
          <th>Observação</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="lista.length === 0">
          <td colspan="6" class="text-secondary">Nenhuma adoção encontrada.</td>
        </tr>
        <tr v-for="item in lista" :key="item.id">
          <td>
            <router-link :to="`/animais/${item.animal_id}`">{{ item.animal }}</router-link>
          </td>
          <td>{{ item.especie }}</td>
          <td v-if="!pode('adotante')">{{ item.solicitante }}</td>
          <td>{{ dataBR(item.data_pedido) }}</td>
          <td>
            <select
              v-if="pode('gestor')"
              class="form-select form-select-sm"
              :value="item.status"
              @change="atualizar(item, $event.target.value)"
            >
              <option value="analise">Em análise</option>
              <option value="aprovada">Aprovada</option>
              <option value="recusada">Recusada</option>
            </select>
            <span v-else class="badge" :class="classeStatus(item.status)">{{ item.status_label }}</span>
          </td>
          <td>{{ item.observacao }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
