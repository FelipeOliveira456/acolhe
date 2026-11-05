import { createRouter, createWebHistory } from 'vue-router'
import { sessao } from './auth'
import Abrigos from './views/Abrigos.vue'
import Adocoes from './views/Adocoes.vue'
import AnimalDetalhe from './views/AnimalDetalhe.vue'
import Animais from './views/Animais.vue'
import Cadastro from './views/Cadastro.vue'
import Doacoes from './views/Doacoes.vue'
import Inicio from './views/Inicio.vue'
import Login from './views/Login.vue'
import Voluntarios from './views/Voluntarios.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: Login, meta: { guest: true } },
    { path: '/cadastro', component: Cadastro, meta: { guest: true } },
    { path: '/', component: Inicio, meta: { auth: true } },
    { path: '/animais', component: Animais, meta: { auth: true } },
    { path: '/animais/:id', component: AnimalDetalhe, meta: { auth: true } },
    { path: '/adocoes', component: Adocoes, meta: { auth: true } },
    { path: '/doacoes', component: Doacoes, meta: { auth: true, papeis: ['voluntario', 'gestor'] } },
    { path: '/abrigos', component: Abrigos, meta: { auth: true, papeis: ['gestor'] } },
    { path: '/voluntarios', component: Voluntarios, meta: { auth: true, papeis: ['gestor'] } },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach((to) => {
  if (!sessao.pronto) return true
  if (to.meta.auth && !sessao.usuario) return '/login'
  if (to.meta.guest && sessao.usuario) return '/'
  if (to.meta.papeis && !to.meta.papeis.includes(sessao.usuario?.papel)) return '/'
  return true
})

export default router
