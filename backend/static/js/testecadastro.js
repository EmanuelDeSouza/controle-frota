const API_BASE = "http://127.0.0.1:5000/api";
document.addEventListener("DOMContentLoaded", () => {
    const formBtn = document.querySelector(".btn-cadastro");
    const listaBody = document.getElementById("lista-caminhoes-body");
    const listaVazia = document.getElementById("lista-vazia-msg");

    // === Carregar caminhões ===
    async function carregarCaminhoes() {
      const resposta = await fetch("/api/caminhoes");
      const caminhoes = await resposta.json();

      listaBody.innerHTML = "";

      if (caminhoes.length === 0) {
        listaVazia.style.display = "block";
      } else {
        listaVazia.style.display = "none";
        caminhoes.forEach(c => {
          const linha = document.createElement("tr");
          linha.innerHTML = `
            <td>${c.placa}</td>
            <td>${c.fabricante}</td>
            <td>${c.modelo}</td>
            <td>${c.ano}</td>
            <td>
              <button class="excluir" data-id="${c.id}">🗑️ Excluir</button>
              <button class="add-expense" data-id="${c.id}">💰 Gasto</button>
              <button class="ver-gastos" data-id="${c.id}">📋 Ver Gastos</button>
            </td>
          `;
          listaBody.appendChild(linha);
        });
      }
    }

    //Função q limpa dados após cadastro
    function limparCampos() {
    document.getElementById("truckForm").reset();
    }

    // === Cadastrar caminhão ===
    formBtn.addEventListener("click", async () => {
      const placa = document.querySelector("input[name='plate']").value.trim();
      const modelo = document.querySelector("input[name='model']").value.trim();
      const fabricante = document.querySelector("input[name='manufacturer']").value.trim();
      const ano = document.querySelector("input[name='year']").value.trim();

      if (!placa || !modelo || !fabricante || !ano) {
        alert("Preencha todos os campos!");
        return;
      }

      const resposta = await fetch("/api/caminhoes", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({placa, modelo, fabricante, ano})
      });

      if (resposta.ok) {
        alert("Caminhão cadastrado com sucesso!");
        limparCampos();
        carregarCaminhoes();
      } else {
        const erro = await resposta.json();
        alert(erro.erro || "Erro ao cadastrar caminhão");
      }
    });

    // === Ações na lista ===
    listaBody.addEventListener("click", async (event) => {
      const id = event.target.dataset.id;

      // Excluir caminhão
      if (event.target.classList.contains("excluir")) {
        const confirmar = confirm("Tem certeza que deseja excluir este caminhão?");
        if (!confirmar) return;

        const resposta = await fetch(`/api/caminhoes/${id}`, { method: "DELETE" });
        const dados = await resposta.json();

        if (resposta.ok) {
          alert(dados.mensagem);
          carregarCaminhoes();
        } else {
          alert(dados.erro || "Erro ao excluir caminhão");
        }
      }

      // Adicionar gasto
      if (event.target.classList.contains("add-expense")) {
        abrirModalGasto(id);
      }

      // Ver gastos
      if (event.target.classList.contains("ver-gastos")) {
        listarGastos(id);
      }
    });

    carregarCaminhoes();
  });

  // === MODAL DE GASTO ===
  function abrirModalGasto(caminhaoId) {
    document.getElementById("caminhaoIdGasto").value = caminhaoId;
    document.getElementById("modalGasto").style.display = "flex";
  }

  function fecharModalGasto() {
    document.getElementById("modalGasto").style.display = "none";
  }

  async function salvarGasto() {
    const caminhaoId = document.getElementById("caminhaoIdGasto").value;
    const descricao = document.getElementById("descricaoGasto").value;
    const valor = document.getElementById("valorGasto").value;
    const data = document.getElementById("dataGasto").value;

    if (!descricao || !valor || !data) {
      alert("Preencha todos os campos do gasto!");
      return;
    }
  
    try {
      const resposta = await fetch(`/api/caminhoes/${caminhaoId}/gastos`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ descricao, valor, data })
      });

      const result = await resposta.json();

      if (resposta.ok) {
        alert(result.message || "Gasto adicionado com sucesso!");
        fecharModalGasto();
      } else {
        alert(result.error || "Erro ao adicionar gasto!");
      }

    } catch (error) {
      console.error("Erro na requisição:", error);
      alert("Falha ao comunicar com o servidor.");
    }
  }

  // === MODAL DE LISTA DE GASTOS ===
  async function listarGastos(caminhaoId) {
    try {
      const resposta = await fetch(`/api/caminhoes/${caminhaoId}/gastos`);
      const gastos = await resposta.json();

      const modal = document.getElementById("modalListaGastos");
      const tbody = modal.querySelector("tbody");
      const totalEl = modal.querySelector(".totalGastos");

      tbody.innerHTML = "";
      let total = 0;

      gastos.forEach(g => {
        const linha = document.createElement("tr");
        linha.innerHTML = `
          <td>${g.descricao}</td>
          <td>R$ ${parseFloat(g.valor).toFixed(2)}</td>
          <td>${g.data.split('-').reverse().join('/')}</td>
        `;
        total += parseFloat(g.valor);
        tbody.appendChild(linha);
      });

      totalEl.textContent = `Total: R$ ${total.toFixed(2)}`;
      modal.style.display = "flex";

    } catch (error) {
      console.error("Erro ao listar gastos:", error);
      alert("Não foi possível carregar os gastos.");
    }
  }

  function fecharModalListaGastos() {
    document.getElementById("modalListaGastos").style.display = "none";
  }
  
  //RELATÓRIO DE GASTOS
  document.getElementById("btnGerarRelatorio").addEventListener("click", async () => {
    const inicio = document.getElementById("dataInicial").value;
    const fim = document.getElementById("dataFinal").value;

    if (!inicio || !fim) {
        alert("Selecione as datas.");
        return;
    }

    try {
        const resposta = await fetch(`/api/relatorio/gastos_detalhado?data_inicial=${inicio}&data_final=${fim}`);

        if (!resposta.ok) {
            throw new Error("Erro ao carregar relatório");
        }

        const dados = await resposta.json();

        if (dados.length === 0) {
            alert("Nenhum gasto encontrado no período.");
            return;
        }

        let total = 0;

        let tabela = `
            <table border="1" class="tabela-relatorio" style="width:100%; border-collapse:collapse">
                <thead>
                    <tr>
                        <th>Placa</th>
                        <th>Descrição</th>
                        <th>Data</th>
                        <th>Valor (R$)</th>
                    </tr>
                </thead>
                <tbody>
        `;

        dados.forEach(gasto => {
            const dataFormatada = gasto.data.split("-").reverse().join("/");
            total += gasto.valor;

            tabela += `
                <tr>
                    <td>${gasto.placa}</td>
                    <td>${gasto.descricao}</td>
                    <td>${dataFormatada}</td>
                    <td>R$ ${gasto.valor.toFixed(2)}</td>
                </tr>
            `;
        });

        tabela += `
                </tbody>
            </table>
            <h3 style="margin-top:15px;">Total no período: <strong>R$ ${total.toFixed(2)}</strong></h3>
        `;

        document.getElementById("conteudoRelatorio").innerHTML = tabela;

        // abre o popup
        document.getElementById("popupRelatorio").style.display = "flex";

    } catch (err) {
        console.error("Erro no relatório:", err);
        alert("Erro ao gerar relatório.");
    }
});

// fechar popup
document.getElementById("fecharPopup").onclick = () => {
    document.getElementById("popupRelatorio").style.display = "none";
};