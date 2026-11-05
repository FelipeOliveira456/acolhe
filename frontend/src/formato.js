export function dataBR(valor) {
  if (!valor) return ''
  const [ano, mes, dia] = valor.split('-')
  return `${dia}/${mes}/${ano}`
}

export function dinheiro(valor) {
  if (valor === null || valor === undefined || valor === '') return ''
  return Number(valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export function classeStatus(status) {
  if (status === 'disponivel' || status === 'aprovada') return 'text-bg-success'
  if (status === 'em_tratamento' || status === 'analise') return 'text-bg-warning'
  if (status === 'recusada') return 'text-bg-danger'
  return 'text-bg-secondary'
}
