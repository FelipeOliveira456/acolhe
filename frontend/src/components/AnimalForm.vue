<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  animal: { type: Object, default: null },
  especies: { type: Array, default: () => [] },
  abrigos: { type: Array, default: () => [] },
})
const emit = defineEmits(['salvar', 'cancelar'])

function vazio() {
  return {
    nome: '',
    especie_id: '',
    abrigo_id: '',
    sexo: 'F',
    porte: 'M',
    status: 'disponivel',
    data_entrada: '',
    castrado: false,
    descricao: '',
  }
}

const form = reactive(vazio())

watch(() => props.animal, (animal) => {
  Object.assign(form, vazio())
  if (animal) {
    Object.assign(form, {
      nome: animal.nome,
      especie_id: String(animal.especie_id),
      abrigo_id: String(animal.abrigo_id),
      sexo: animal.sexo,
      porte: animal.porte,
      status: animal.status,
      data_entrada: animal.data_entrada,
      castrado: animal.castrado,
      descricao: animal.descricao,
    })
  }
}, { immediate: true })

function enviar() {
  emit('salvar', {
    ...form,
    especie_id: Number(form.especie_id),
    abrigo_id: Number(form.abrigo_id),
  })
}
</script>

<template>
  <form class="card mb-4" @submit.prevent="enviar">
    <div class="card-body">
      <h2 class="h5">{{ animal ? 'Editar animal' : 'Novo animal' }}</h2>
      <div class="row g-3">
        <div class="col-md-4">
          <label class="form-label">Nome</label>
          <input v-model="form.nome" class="form-control" required>
        </div>
        <div class="col-md-4">
          <label class="form-label">Espécie</label>
          <select v-model="form.especie_id" class="form-select" required>
            <option value="">Selecione</option>
            <option v-for="item in especies" :key="item.id" :value="String(item.id)">{{ item.nome }}</option>
          </select>
        </div>
        <div class="col-md-4">
          <label class="form-label">Abrigo</label>
          <select v-model="form.abrigo_id" class="form-select" required>
            <option value="">Selecione</option>
            <option v-for="item in abrigos" :key="item.id" :value="String(item.id)">{{ item.nome }}</option>
          </select>
        </div>
        <div class="col-md-3">
          <label class="form-label">Sexo</label>
          <select v-model="form.sexo" class="form-select">
            <option value="F">Fêmea</option>
            <option value="M">Macho</option>
          </select>
        </div>
        <div class="col-md-3">
          <label class="form-label">Porte</label>
          <select v-model="form.porte" class="form-select">
            <option value="P">Pequeno</option>
            <option value="M">Médio</option>
            <option value="G">Grande</option>
          </select>
        </div>
        <div class="col-md-3">
          <label class="form-label">Status</label>
          <select v-model="form.status" class="form-select">
            <option value="disponivel">Disponível</option>
            <option value="em_tratamento">Em tratamento</option>
            <option value="adotado">Adotado</option>
          </select>
        </div>
        <div class="col-md-3">
          <label class="form-label">Entrada</label>
          <input v-model="form.data_entrada" type="date" class="form-control" required>
        </div>
        <div class="col-12">
          <label class="form-label">Descrição</label>
          <textarea v-model="form.descricao" class="form-control" rows="2"></textarea>
        </div>
        <div class="col-12">
          <div class="form-check">
            <input id="castrado" v-model="form.castrado" class="form-check-input" type="checkbox">
            <label class="form-check-label" for="castrado">Castrado</label>
          </div>
        </div>
      </div>
      <div class="mt-3">
        <button class="btn btn-success" type="submit">Salvar</button>
        <button class="btn btn-outline-secondary ms-2" type="button" @click="emit('cancelar')">Cancelar</button>
      </div>
    </div>
  </form>
</template>
