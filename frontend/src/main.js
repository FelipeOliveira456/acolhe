import { createApp } from 'vue'
import App from './App.vue'
import { carregarSessao } from './auth'
import router from './router'
import { aplicarTema } from './tema'
import './style.css'

aplicarTema()

carregarSessao().finally(() => {
  createApp(App).use(router).mount('#app')
})
