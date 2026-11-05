import { reactive } from 'vue'
import { api } from './api'

export const sessao = reactive({
  usuario: null,
  pronto: false,
})

export async function carregarSessao() {
  try {
    await api('/api/csrf')
  } catch {
    sessao.usuario = null
    sessao.pronto = true
    return
  }
  try {
    sessao.usuario = await api('/api/me')
  } catch {
    sessao.usuario = null
  }
  sessao.pronto = true
}

export function pode(...papeis) {
  return Boolean(sessao.usuario && papeis.includes(sessao.usuario.papel))
}
