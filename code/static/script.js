function aplicarTema(tema) {
    document.documentElement.setAttribute('data-bs-theme', tema);
    const icone = document.querySelector('#botaoTema i');
    if (icone) {
        icone.className = tema === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
    if (typeof Chart !== 'undefined') {
        Chart.defaults.color = tema === 'dark' ? '#dee2e6' : '#495057';
        Object.values(Chart.instances).forEach((grafico) => grafico.update());
    }
}

function alternarTema() {
    const atual = document.documentElement.getAttribute('data-bs-theme');
    const novo = atual === 'dark' ? 'light' : 'dark';
    localStorage.setItem('acolhe-tema', novo);
    aplicarTema(novo);
}

function alterarVisibilidadeSenha(fieldId) {
    const field = document.getElementById(fieldId);
    if (field.type === "password") {
        field.type = "text";
    } else {
        field.type = "password";
    }
}

function validaSenha() {
    const password = document.getElementById("senha").value;
    const confirmPassword = document.getElementById("confirma_senha").value;
    const errorDiv = document.getElementById("erroSenha");

    if (password !== confirmPassword) {
        errorDiv.style.display = "block";
        return false;
    } else {
        errorDiv.style.display = "none";
        return true;
    }
}

function lerDados(id) {
    const elemento = document.getElementById(id);
    return elemento ? JSON.parse(elemento.textContent) : null;
}

function graficoStatus() {
    const dados = lerDados('dados-status');
    if (!dados) return;

    new Chart(document.getElementById('graficoStatus'), {
        type: 'doughnut',
        data: {
            labels: dados.labels,
            datasets: [{
                label: 'Animais',
                data: dados.dados,
                backgroundColor: [
                    'rgb(25, 135, 84)',
                    'rgb(255, 193, 7)',
                    'rgb(108, 117, 125)'
                ],
                hoverOffset: 8
            }]
        },
        options: {
            maintainAspectRatio: false
        }
    });
}

function graficoEspecies() {
    const dados = lerDados('dados-especies');
    if (!dados) return;

    new Chart(document.getElementById('graficoEspecies'), {
        type: 'bar',
        data: {
            labels: dados.labels,
            datasets: [{
                label: 'Animais acolhidos',
                data: dados.dados,
                backgroundColor: 'rgba(25, 135, 84, 0.7)',
                borderColor: 'rgb(25, 135, 84)',
                borderWidth: 1
            }]
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

aplicarTema(localStorage.getItem('acolhe-tema') || 'light');

if (typeof Chart !== 'undefined') {
    graficoStatus();
    graficoEspecies();
}
