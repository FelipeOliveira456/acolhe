<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api'
import { dataBR, dinheiro } from '../formato'

const lista = ref([])
const erro = ref('')
const form = reactive({
  doador_nome: '',
  tipo: 'dinheiro',
  valor: '',
  descricao: '',
  data: '',
})

async function carregar() {
  lista.value = await api('/api/doacoes')
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
    await api('/api/doacoes', { method: 'POST', body: { ...form } })
    form.doador_nome = ''
    form.valor = ''
    form.descricao = ''
    form.data = ''
    await carregar()
  } catch (e) {
    erro.value = e.message
  }
}
</script>

<template>
  <h1 class="h3 mb-3">Doações</h1>
  <div v-if="erro" class="alert alert-danger">{{ erro }}</div>
  <form class="card mb-4" @submit.prevent="salvar">
    <div class="card-body">
      <h2 class="h5">Registrar doação</h2>
      <div class="row g-2">
        <div class="col-md-4">
          <input v-model="form.doador_nome" class="form-control" placeholder="Nome do doador" required>
        </div>
        <div class="col-md-2">
          <select v-model="form.tipo" class="form-select">
            <option value="dinheiro">Dinheiro</option>
            <option value="racao">Ração</option>
            <option value="medicamento">Medicamento</option>
            <option value="outro">Outro</option>
          </select>
        </div>
        <div class="col-md-2">
          <input v-model="form.valor" class="form-control" placeholder="Valor">
        </div>
        <div class="col-md-2">
          <input v-model="form.data" type="date" class="form-control" required>
        </div>
        <div class="col-md-6">
          <input v-model="form.descricao" class="form-control" placeholder="Descrição">
        </div>
      </div>
      <button class="btn btn-success mt-3" type="submit">Registrar</button>
    </div>
  </form>
  <div class="table-responsive">
    <table class="table align-middle">
      <thead>
        <tr>
          <th>Data</th>
          <th>Doador</th>
          <th>Tipo</th>
          <th>Valor</th>
          <th>Descrição</th>
          <th>Registrado por</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="lista.length === 0">
          <td colspan="6" class="text-secondary">Nenhuma doação registrada.</td>
        </tr>
        <tr v-for="item in lista" :key="item.id">
          <td>{{ dataBR(item.data) }}</td>
          <td>{{ item.doador_nome }}</td>
          <td>{{ item.tipo_label }}</td>
          <td>{{ dinheiro(item.valor) }}</td>
          <td>{{ item.descricao }}</td>
          <td>{{ item.registrado_por }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
