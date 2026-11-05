import { ref } from 'vue'

export const tema = ref(localStorage.getItem('acolhe-tema') || 'light')

export function aplicarTema() {
  document.documentElement.setAttribute('data-bs-theme', tema.value)
}

export function alternarTema() {
  tema.value = tema.value === 'dark' ? 'light' : 'dark'
  localStorage.setItem('acolhe-tema', tema.value)
  aplicarTema()
}
