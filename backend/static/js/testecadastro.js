document.addEventListener("DOMContentLoaded", () => {
    // === SELETORES DO DOM ===
    const listaBody = document.getElementById("lista-caminhoes-body");
    const listaVazia = document.getElementById("lista-vazia-msg");
    const corpoTabelaItens = document.getElementById('lista-itens-body');
    

    // ==========================================
    // 🚚 CONTEXTO: CAMINHÕES
    // ==========================================

    // Listar Caminhões
    // === Carregar caminhões ===
    async function carregarCaminhoes() {
      // Se NÃO encontrar a tabela de caminhões na página atual, sai da função sem quebrar o código
      if (!listaBody) return; 

      try {
        const resposta = await fetch("/api/caminhoes");
        const caminhoes = await resposta.json();

        listaBody.innerHTML = "";

        if (caminhoes.length === 0) {
          if (listaVazia) listaVazia.style.display = "block";
        } else {
          if (listaVazia) listaVazia.style.display = "none";
          caminhoes.forEach(c => {
            const linha = document.createElement("tr");
            linha.innerHTML = `
              <td>${c.placa}</td>
              <td>${c.fabricante}</td>
              <td>${c.modelo}</td>
              <td>${c.ano}</td>
              <td>${c.prefixo || '---'}</td>
              <td>${c.chassi || '---'}</td>
              <td>
                <div class="dropdown">
                    <button class="btn-acoes">Ações ▾</button>
                    <div class="dropdown-menu">
                    <button class="add-expense" data-id="${c.id}">💰 Adicionar Gasto</button>
                    <button class="abastecer" data-id="${c.id}">⛽ Registrar Abastecimento</button>
                    <button class="dropdown-item" onclick="abrirModalReceita(${c.id})">💵 Registrar Receita</button>
                    <button class="ver-gastos" data-id="${c.id}">📋 Ver Gastos</button>
                    <button class="dropdown-item" onclick="listarReceitas(${c.id})">📈 Ver Receitas</button>
                    <button class="excluir" data-id="${c.id}">🗑️ Excluir Caminhão</button>
                    
                    
                    </div>
                </div>
                </td>
            `;
            listaBody.appendChild(linha);
          });
        }
      } catch (erro) {
         console.error("Erro ao carregar caminhões:", erro);
      }
    }

    // Cadastro de Caminhões

    // Cadastro de Caminhões
    // CORREÇÃO: Buscando pelo ID correto 'btnSalvarCaminhao' que colocamos no HTML
    const btnSalvarCaminhao = document.getElementById("btnSalvarCaminhao");
if (btnSalvarCaminhao) {
    btnSalvarCaminhao.addEventListener("click", async (e) => {
        e.preventDefault();
        
        

        const dadosCaminhao = {
            placa: document.getElementById("placa").value.trim(),
            modelo: document.getElementById("modelo").value.trim(),
            fabricante: document.getElementById("fabricante").value.trim(),
            ano: parseInt(document.getElementById("ano").value),
            prefixo: document.getElementById("prefixo").value.trim(),
            chassi: document.getElementById("chassi").value.trim()
        };

       

        try {
            const resposta = await fetch("/api/caminhoes", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(dadosCaminhao)
            });

    

            const resultado = await resposta.json();
            if (resposta.ok) {
                document.getElementById("formCaminhao").reset(); 
                carregarCaminhoes(); 
            } else {
                alert("Erro no cadastro" + (resultado.erro || "Erro desconhecido"));
            }
        } catch (erro) {
            alert("Passo 4 FALHOU: O JavaScript não conseguiu falar com o servidor. Erro: " + erro);
        }
    });
} 

    // Ações da Lista de Caminhões (Excluir, Adicionar Gasto, Ver Gastos)
    if (listaBody) {
        listaBody.addEventListener("click", async (event) => {
            const id = event.target.dataset.id;
            if (!id) return;

            // Opção: Excluir
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

            
            if (event.target.classList.contains("add-expense")) {
                abrirModalGasto(id);
            }

            
            if (event.target.classList.contains("ver-gastos")) {
                listarGastos(id);
            }

            if (event.target.classList.contains("abastecer")) {
            abrirModalAbastecimento(id);

            if (event.target.classList.contains("add-receita")) {
            abrirModalReceita(id);
}
            if (event.target.classList.contains("ver-receitas")) {
            listarReceitas(id);
}
}
        });
    }

    // ==========================================
    // 🔧 CONTEXTO: ITENS DE MANUTENÇÃO
    // ==========================================

    // Listar Itens
    async function listarItens() {
    if (!corpoTabelaItens) return;

    try {
        const resposta = await fetch('/api/itens');
        const itens = await resposta.json();

        corpoTabelaItens.innerHTML = '';

        if (itens.length === 0) {
            if (listaVazia) listaVazia.style.display = 'block';
            return;
        }

        if (listaVazia) listaVazia.style.display = 'none';

        itens.forEach(item => {
            const linha = document.createElement("tr");
            linha.innerHTML = `
                <td>${item.nome}</td>
                <td>R$ ${parseFloat(item.valor_unitario).toFixed(2)}</td>
                <td>${item.categoria || '---'}</td>
            `;
            corpoTabelaItens.appendChild(linha);
        });

    } catch (err) {
        console.error("Erro ao listar itens:", err);
    }
}

async function carregarCaminhoesNoSelect() {
    const select = document.getElementById('placaSelect');
    if (!select) return;

    try {
        const resposta = await fetch('/api/caminhoes');
        const caminhoes = await resposta.json();

        caminhoes.forEach(c => {
            const option = document.createElement('option');
            option.value = c.placa;
            option.textContent = `${c.placa} — ${c.modelo}`;
            select.appendChild(option);
        });
    } catch (err) {
        console.error("Erro ao carregar caminhões no select:", err);
    }
}

async function carregarItensNoSelect() {
    const select = document.getElementById('itemSelect');
    if (!select) return;

    try {
        const response = await fetch('/api/itens');
        if (!response.ok) return;

        const itens = await response.json();
        select.innerHTML = '<option value="todos">Todos os Itens</option>';

        itens.forEach(item => {
            const option = document.createElement('option');
            option.value = item.nome;
            option.textContent = item.nome;
            select.appendChild(option);
        });
    } catch (error) {
        console.error("Erro ao carregar itens no select:", error);
    }
}

    // Cadastrar Item
    const btnSalvarItem = document.getElementById("btnSalvarItem") || document.getElementById("btn-cadastro");
    if (btnSalvarItem) {
        btnSalvarItem.addEventListener("click", async (e) => {
            e.preventDefault();

            // Mapeia os inputs tentando os dois padrões de ID que você usou no seu código
            const inputNome = document.getElementById("nomeItem") || document.querySelector('input[name="name"]');
            const inputValor = document.getElementById("valorUnitario") || document.querySelector('input[name="Value"]');
            const inputCategoria = document.getElementById("categoriaItem") || document.querySelector('input[name="Category"]');

            const dadosItem = {
                nome: inputNome ? inputNome.value.trim() : "",
                valor_unitario: inputValor ? parseFloat(inputValor.value) : NaN,
                categoria: inputCategoria ? inputCategoria.value.trim() : ""
            };

            if (!dadosItem.nome || isNaN(dadosItem.valor_unitario)) {
                alert("Por favor, insira um nome e um valor unitário válido.");
                return;
            }

            try {
                const resposta = await fetch("/api/itens/cadastrar", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(dadosItem)
                });

                const resultado = await resposta.json();

                if (resposta.ok) {
                    alert("Item cadastrado com sucesso!");
                    const form = document.getElementById("formItem") || document.getElementById("truckForm");
                    if (form) form.reset();
                    listarItens(); // Atualiza a tabela na hora
                    carregarItensNoSelect(); // Atualiza o select do relatório se ele existir na tela
                } else {
                    alert(`Erro: ${resultado.error || "Não foi possível cadastrar o item."}`);
                }
            } catch (erro) {
                console.error("Erro na requisição:", erro);
                alert("Erro interno ao conectar com o servidor.");
            }
        });
    }


    // ==========================================
    // 📈 CONTEXTO: RELATÓRIOS
    // ==========================================

    
   

    // Evento de gerar relatório
    const btnGerarRelatorio = document.getElementById("btnGerarRelatorio");
if (btnGerarRelatorio) {
    btnGerarRelatorio.addEventListener("click", async () => {
        const inicio = document.getElementById("dataInicial").value;
        const fim = document.getElementById("dataFinal").value;
        const placa = document.getElementById("placaSelect")?.value || "todos";
        const tipo = document.getElementById("tipoSelect")?.value || "todos";

        if (!inicio || !fim) {
            alert("Selecione as datas inicial e final.");
            return;
        }

        try {
            const url = `/api/relatorio/gastos_detalhado?data_inicial=${inicio}&data_final=${fim}&placa=${placa}&tipo=${tipo}`;
            const resposta = await fetch(url);
            if (!resposta.ok) throw new Error("Erro ao carregar relatório");

            const dados = await resposta.json();

            if (dados.length === 0) {
                alert("Nenhum gasto encontrado para os filtros selecionados.");
                return;
            }

            let total = 0;
            const corTipo = t => t === 'Abastecimento' ? '#1565C0' :
                                  t === 'Manutenção' ? '#F57C00' :
                                  t === 'Pedágio' ? '#6a1b9a' : '#888';

            let tabela = `
                <table border="1" class="tabela-relatorio" style="width:100%; border-collapse:collapse; margin-top:20px;">
                    <thead>
                        <tr>
                            <th>Placa</th>
                            <th>Descrição</th>
                            <th>Tipo</th>
                            <th>Data</th>
                            <th>Valor (R$)</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            dados.forEach(g => {
                const dataFormatada = g.data.split("-").reverse().join("/");
                total += parseFloat(g.valor);
                tabela += `
                    <tr>
                        <td>${g.placa}</td>
                        <td>${g.descricao}</td>
                        <td style="color:${corTipo(g.tipo)}; font-weight:600;">${g.tipo}</td>
                        <td>${dataFormatada}</td>
                        <td>R$ ${parseFloat(g.valor).toFixed(2)}</td>
                    </tr>
                `;
            });

            tabela += `
                    </tbody>
                </table>
                <h3 style="margin-top:15px; text-align:right;">
                    Total: <strong>R$ ${total.toFixed(2)}</strong>
                </h3>
            `;

            document.getElementById("resultadoRelatorio").innerHTML = tabela;

        } catch (err) {
            console.error("Erro no relatório:", err);
            alert("Erro ao gerar relatório. Verifique o console.");
        }
    });
}

    // Fechar Popup do Relatório
    const btnFecharRelatorio = document.getElementById("fecharPopup");
    if (btnFecharRelatorio) {
        btnFecharRelatorio.onclick = () => {
            document.getElementById("popupRelatorio").style.display = "none";
        };
    }

    // ==========================================
    // 🚀 INICIALIZAÇÃO DA PÁGINA
    // ==========================================
    carregarCaminhoes();
    listarItens();
    carregarItensNoSelect();
    carregarCaminhoesNoSelect();
});

async function carregarItensNoModalGasto() {
    const select = document.getElementById("itemSelecionado");
    if (!select) return;
    try {
        const resposta = await fetch('/api/itens');
        const itens = await resposta.json();
        select.innerHTML = '<option value="">-- Selecione --</option>';
        itens.forEach(item => {
            const opt = document.createElement("option");
            opt.value = item.id;
            opt.textContent = item.nome;
            opt.dataset.valor = item.valor_unitario;
            opt.dataset.nome = item.nome;
            select.appendChild(opt);
        });
    } catch (err) {
        console.error("Erro ao carregar itens:", err);
    }
}

function alternarTipoGasto() {
    const tipo = document.getElementById("categoriaGasto").value;
    document.getElementById("campoSelectItem").style.display =
        tipo === "item" ? "block" : "none";

    if (tipo !== "item") {
        document.getElementById("descricaoGasto").value = "";
        document.getElementById("valorGasto").value = "";
    }
}

function preencherValorItem() {
    const select = document.getElementById("itemSelecionado");
    const opcao = select.options[select.selectedIndex];
    if (!opcao.value) return;
    document.getElementById("descricaoGasto").value = opcao.dataset.nome;
    document.getElementById("valorGasto").value = parseFloat(opcao.dataset.valor).toFixed(2);
}


// ==========================================
// 🧮 FUNÇÕES GLOBAIS (CHAMADAS VIA ONCLICK NO HTML)
// ==========================================
async function excluirGasto(gastoId, caminhaoId) {
    if (!confirm("Excluir este gasto?")) return;

    const resposta = await fetch(`/api/gastos/${gastoId}`, { method: "DELETE" });
    const result = await resposta.json();

    if (resposta.ok) {
        alert(result.message || "Gasto excluído!");
        listarGastos(caminhaoId); // atualiza a lista
    } else {
        alert(result.error || "Erro ao excluir.");
    }
}

function abrirModalGasto(caminhaoId) {
    document.getElementById("caminhaoIdGasto").value = caminhaoId;
    document.getElementById("categoriaGasto").value = "Manutenção";
    document.getElementById("campoSelectItem").style.display = "none";
    document.getElementById("descricaoGasto").value = "";
    document.getElementById("valorGasto").value = "";
    document.getElementById("modalGasto").style.display = "flex";
    carregarItensNoModalGasto();
}

function fecharModalGasto() {
    document.getElementById("modalGasto").style.display = "none";
}

async function salvarGasto() {
    const caminhaoId = document.getElementById("caminhaoIdGasto").value;
    const descricao = document.getElementById("descricaoGasto").value;
    const valor = document.getElementById("valorGasto").value;
    const data = document.getElementById("dataGasto").value;
    const tipo = document.getElementById("categoriaGasto").value; // ← novo

    if (!descricao || !valor || !data) {
        alert("Preencha todos os campos do gasto!");
        return;
    }

    try {
        const resposta = await fetch(`/api/caminhoes/${caminhaoId}/gastos`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ descricao, valor, data, tipo }) // ← tipo incluído
        });

        const result = await resposta.json();
        if (resposta.ok) {
            alert(result.message || "Gasto adicionado com sucesso!");
            fecharModalGasto();
        } else {
            alert(result.error || "Erro ao adicionar gasto!");
        }
    } catch (error) {
        console.error("Erro:", error);
        alert("Falha ao comunicar com o servidor.");
    }
}

async function listarGastos(caminhaoId) {
    try {
        const [resGastos, resAbast]  = await Promise.all([
            fetch(`/api/caminhoes/${caminhaoId}/gastos`),
            fetch(`/api/caminhoes/${caminhaoId}/abastecimentos`)
        ]);
        
        const gastos = await resGastos.json();
        const abastecimentos = await resAbast.json();

        const abastFormatados = abastecimentos.map(a => ({
            id: a.id,
            descricao: `Abastecimento — ${a.litros}L`,
            tipo: 'Abastecimento',
            valor: a.valor,
            data: a.data,
            is_abastecimento: true  // flag para não mostrar botão excluir por enquanto
        }));
        
        const tudo = [...gastos, ...abastFormatados].sort((a, b) =>
            new Date(b.data) - new Date(a.data)
        );

        const modal = document.getElementById("modalListaGastos");
        const tbody = modal.querySelector("tbody");
        const totalEl = modal.querySelector(".totalGastos");

        tbody.innerHTML = "";
        let total = 0;

        tudo.forEach(g => {
            const linha = document.createElement("tr");
            const corTipo = g.tipo === 'Abastecimento' ? '#1565C0' :
                            g.tipo === 'Manutenção' ? '#F57C00' :
                            g.tipo === 'Pedágio' ? '#6a1b9a' : '#888';

            linha.innerHTML = `
                <td>${g.descricao}</td>
                <td><span style="color:${corTipo}; font-weight:600;">${g.tipo || '---'}</span></td>
                <td>R$ ${parseFloat(g.valor).toFixed(2)}</td>
                <td>${g.data.split('-').reverse().join('/')}</td>
                <td>
                    ${!g.is_abastecimento
                        ? `<button type="button" onclick="excluirGasto(${g.id}, ${caminhaoId})">🗑️ Excluir</button>`
                        : '---'
                    }
                </td>
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

function abrirModalAbastecimento(caminhaoId) {
    document.getElementById("caminhaoIdAbastecimento").value = caminhaoId;
    document.getElementById("modalAbastecimento").style.display = "flex";
}

function fecharModalAbastecimento() {
    document.getElementById("modalAbastecimento").style.display = "none";
}

async function salvarAbastecimento() {
    const caminhaoId = document.getElementById("caminhaoIdAbastecimento").value;
    const litros = document.getElementById("litrosAbast").value;
    const valor = document.getElementById("valorAbast").value;
    const km = document.getElementById("kmAbast").value;
    const data = document.getElementById("dataAbast").value;

    if (!litros || !valor || !km || !data) {
        alert("Preencha todos os campos!");
        return;
    }

    try {
        const resposta = await fetch(`/api/caminhoes/${caminhaoId}/abastecimentos`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ litros, valor, km_atual: km, data })
        });

        const result = await resposta.json();
        if (resposta.ok) {
            alert(result.message || "Abastecimento registrado!");
            fecharModalAbastecimento();
            document.getElementById("litrosAbast").value = "";
            document.getElementById("valorAbast").value = "";
            document.getElementById("kmAbast").value = "";
            document.getElementById("dataAbast").value = "";
        } else {
            alert(result.error || "Erro ao registrar abastecimento!");
        }
    } catch (erro) {
        console.error("Erro:", erro);
        alert("Falha ao comunicar com o servidor.");
    }
}

function abrirModalReceita(caminhaoId) {
        console.log("abrirModalReceita chamado com o ID do caminhão:", caminhaoId);
        document.getElementById("caminhaoIdReceita").value = caminhaoId;
        document.getElementById("descricaoReceita").value = "";
        document.getElementById("valorReceita").value = "";
        document.getElementById("dataReceita").value = "";
        document.getElementById("modalReceita").style.display = "flex";
    }

    function fecharModalReceita() {
        document.getElementById("modalReceita").style.display = "none";
    }

    async function salvarReceita() {
        const caminhaoId = document.getElementById("caminhaoIdReceita").value;
        const descricao = document.getElementById("descricaoReceita").value;
        const valor = document.getElementById("valorReceita").value;
        const data = document.getElementById("dataReceita").value;

        if (!descricao || !valor || !data) {
            alert("Preencha todos os campos!");
            return;
        }

        try {
            const resposta = await fetch(`/api/caminhoes/${caminhaoId}/receitas`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ descricao, valor, data })
            });

            const result = await resposta.json();
            if (resposta.ok) {
                alert(result.message || "Receita registrada!");
                fecharModalReceita();
                location.reload(); // Recarrega para o dashboard computar as mudanças
            } else {
                alert(result.error || "Erro ao registrar receita!");
            }
        } catch (erro) {
            console.error("Erro:", erro);
            alert("Falha ao comunicar com o servidor.");
        }
    }

    async function listarReceitas(caminhaoId) {
        console.log("listarReceitas chamado com o ID do caminhão:", caminhaoId);
        try {
            const resposta = await fetch(`/api/caminhoes/${caminhaoId}/receitas`);
            const receitas = await resposta.json();

            const modal = document.getElementById("modalListaReceitas");
            const tbody = document.getElementById("tbodyReceitas");
            const totalEl = modal.querySelector(".totalReceitas");

            tbody.innerHTML = "";
            let total = 0;

            receitas.forEach(r => {
                const linha = document.createElement("tr");
                // Garante que a data do backend formate corretamente na inversão por hífens
                const dataFormatada = r.data.includes(' ') ? r.data.split(' ')[0] : r.data;
                const dataExibicao = dataFormatada.split('-').reverse().join('/');

                linha.innerHTML = `
                    <td>${r.descricao}</td>
                    <td>R$ ${parseFloat(r.valor).toFixed(2)}</td>
                    <td>${dataExibicao}</td>
                    <td>
                        <button type="button" onclick="excluirReceita(${r.id}, ${caminhaoId})">🗑️ Excluir</button>
                    </td>
                `;
                total += parseFloat(r.valor);
                tbody.appendChild(linha);
            });

            totalEl.textContent = `Total: R$ ${total.toFixed(2)}`;
            modal.style.display = "flex";
        } catch (erro) {
            console.error("Erro:", erro);
            alert("Não foi possível carregar as receitas.");
        }
    }

    function fecharModalListaReceitas() {
        document.getElementById("modalListaReceitas").style.display = "none";
    }

    async function excluirReceita(receitaId, caminhaoId) {
        if (!confirm("Excluir esta receita?")) return;

        try {
            const resposta = await fetch(`/api/receitas/${receitaId}`, { method: "DELETE" });
            const result = await resposta.json();

            if (resposta.ok) {
                alert(result.message || "Receita excluída!");
                listarReceitas(caminhaoId);
            } else {
                alert(result.error || "Erro ao excluir.");
            }
        } catch (erro) {
            console.error("Erro no fetch de exclusão:", erro);
        }
} 
