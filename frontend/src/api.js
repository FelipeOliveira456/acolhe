function csrf() {
  const encontrado = document.cookie.match(/csrftoken=([^;]+)/)
  return encontrado ? decodeURIComponent(encontrado[1]) : ''
}

export async function api(url, { method = 'GET', body } = {}) {
  const headers = {}
  const opcoes = { method, credentials: 'include', headers }

  if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
    opcoes.body = JSON.stringify(body)
  }
  if (method !== 'GET') {
    headers['X-CSRFToken'] = csrf()
  }

  const resposta = await fetch(url, opcoes)
  const dados = await resposta.json().catch(() => ({}))
  if (!resposta.ok) {
    throw new Error(dados.erro || 'Não foi possível concluir a operação.')
  }
  return dados
}
