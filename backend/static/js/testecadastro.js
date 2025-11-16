const API_BASE = "http://127.0.0.1:5000/api";
document.addEventListener("DOMContentLoaded", () => {
  const formBtn = document.querySelector(".btn-cadastro");
  const listaBody = document.getElementById("lista-caminhoes-body");
  const listaVazia = document.getElementById("lista-vazia-msg");

  // Função para carregar caminhões
  async function carregarCaminhoes() {
    try {
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
            </td>
          `;
          listaBody.appendChild(linha);
        });
      }

      // Conectar os botões de exclusão
      document.querySelectorAll(".excluir").forEach(btn => {
        btn.addEventListener("click", async (e) => {
          const id = e.target.getAttribute("data-id");
          if (confirm("Deseja realmente excluir este caminhão?")) {
            await excluirCaminhao(id);
            carregarCaminhoes();
          }
        });
      });

    } catch (erro) {
      console.error("Erro ao carregar caminhões:", erro);
    }
  }

  // Função para cadastrar caminhão
  formBtn.addEventListener("click", async () => {
    const placa = document.querySelector("input[name='plate']").value.trim();
    const modelo = document.querySelector("input[name='model']").value.trim();
    const fabricante = document.querySelector("input[name='manufacturer']").value.trim();
    const ano = document.querySelector("input[name='year']").value.trim();

    if (!placa || !modelo || !fabricante || !ano) {
      alert("Preencha todos os campos!");
      return;
    }

    try {
      const resposta = await fetch("/api/caminhoes", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({placa, modelo, fabricante, ano})
      });

      const dados = await resposta.json();

      if (resposta.ok) {
        mostrarToast("Caminhão cadastrado com sucesso!", "success");
        limparCampos();
        carregarCaminhoes();
      } else {
        mostrarToast("Erro ao cadastrar caminhão", "error");
      }
    } catch (erro) {
      console.error("Erro ao cadastrar:", erro);
      alert("Erro na comunicação com o servidor.");
    }
  });

  //Função q limpa dados após cadastro
  function limparCampos() {
    document.getElementById("truckForm").reset();
  }
  


  // Função para excluir caminhão
  async function excluirCaminhao(id) {
    try {
      const resposta = await fetch(`/api/caminhoes/${id}`, {
        method: "DELETE"
      });
      const resultado = await resposta.json();
      if (resposta.ok) {
        alert("🗑️ Caminhão excluído com sucesso!");
      } else {
        alert(`Erro: ${resultado.erro}`);
      }
    } catch (erro) {
      console.error("Erro ao excluir caminhão:", erro);
    }
  }

  // Função para limpar os campos após cadastro
  function limparCampos() {
    document.querySelectorAll(".input").forEach(input => input.value = "");
  }

  // Inicializa a listagem ao carregar a página
  carregarCaminhoes();

  function mostrarToast(mensagem, tipo = "success") {
  const toast = document.createElement("div");
  toast.className = `toast ${tipo}`;
  toast.textContent = mensagem;
  document.body.appendChild(toast);

  setTimeout(() => toast.classList.add("show"), 100);

  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 500);
  }, 3000);
}
});