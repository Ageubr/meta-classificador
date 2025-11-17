// API Base URL - usa URL relativa para funcionar em qualquer ambiente
const API_URL = window.location.origin;

// Log para debug
console.log('🔍 API URL:', API_URL);

// Elements
const form = document.getElementById('vulnerabilityForm');
const predictBtn = document.getElementById('predictBtn');
const analyzeLLMBtn = document.getElementById('analyzeLLMBtn');
const resultsSection = document.getElementById('resultsSection');
const resultsContent = document.getElementById('resultsContent');
const llmSection = document.getElementById('llmSection');
const llmContent = document.getElementById('llmContent');
const loadingOverlay = document.getElementById('loadingOverlay');
const loadingText = document.getElementById('loadingText');
const apiStatus = document.getElementById('apiStatus');

// Check API health on load
async function checkAPIHealth() {
    console.log('🔍 Verificando saúde da API em:', `${API_URL}/health`);
    try {
        const response = await fetch(`${API_URL}/health`);
        console.log('✅ Resposta da API:', response.status);
        const data = await response.json();
        console.log('📊 Dados da API:', data);
        
        if (data.status === 'healthy') {
            apiStatus.innerHTML = '<span class="status-dot online"></span><span class="status-text">API Online ✓</span>';
        } else {
            apiStatus.innerHTML = '<span class="status-dot"></span><span class="status-text">API Offline</span>';
        }
    } catch (error) {
        console.error('❌ Erro ao verificar API:', error);
        apiStatus.innerHTML = '<span class="status-dot"></span><span class="status-text">API Offline</span>';
    }
}

// Get form data
function getFormData() {
    const data = {};
    
    // Dados numéricos inteiros
    data.idade_responsavel = parseInt(document.getElementById('idade_responsavel').value);
    data.numero_membros = parseInt(document.getElementById('numero_membros').value);
    data.criancas = parseInt(document.getElementById('criancas').value);
    data.idosos = parseInt(document.getElementById('idosos').value);
    data.pessoas_trabalhando = parseInt(document.getElementById('pessoas_trabalhando').value);
    data.comodos = parseInt(document.getElementById('comodos').value);
    data.tempo_residencia = parseInt(document.getElementById('tempo_residencia').value);
    
    // Dados numéricos decimais
    data.renda_per_capita = parseFloat(document.getElementById('renda_per_capita').value);
    data.valor_bolsa_familia = parseFloat(document.getElementById('valor_bolsa_familia').value);
    
    // Checkboxes (sempre incluir, mesmo se false)
    data.possui_agua_encanada = document.getElementById('possui_agua_encanada').checked;
    data.possui_esgoto = document.getElementById('possui_esgoto').checked;
    data.possui_coleta_lixo = document.getElementById('possui_coleta_lixo').checked;
    data.possui_energia = document.getElementById('possui_energia').checked;
    data.possui_banheiro = document.getElementById('possui_banheiro').checked;
    
    // Boolean do select
    data.recebe_bolsa_familia = document.getElementById('recebe_bolsa_familia').value === 'true';
    
    // Strings
    data.material_parede = document.getElementById('material_parede').value;
    data.material_teto = document.getElementById('material_teto').value;
    data.nivel_escolaridade = document.getElementById('nivel_escolaridade').value;
    data.situacao_trabalho = document.getElementById('situacao_trabalho').value;
    
    return data;
}

// Show loading
function showLoading() {
    loadingOverlay.classList.add('active');
}

// Hide loading
function hideLoading() {
    loadingOverlay.classList.remove('active');
}

// Display prediction results
function displayResults(data) {
    // Suporta tanto /predict quanto /analyze (nomes de campos diferentes)
    const rfPred = data.vulnerabilidade_rf || data.predicao_rf;
    const xgbPred = data.vulnerabilidade_xgb || data.predicao_xgb;
    const rfProb = data.probabilidade_rf || data.probabilidades_rf;
    const xgbProb = data.probabilidade_xgb || data.probabilidades_xgb;
    
    if (!rfPred || !xgbPred) {
        console.error('Dados incompletos:', data);
        return;
    }
    
    const rfClass = rfPred.toLowerCase();
    const xgbClass = xgbPred.toLowerCase();
    
    resultsContent.innerHTML = `
        <div class="result-grid">
            <div class="result-card">
                <h3>🌲 Random Forest</h3>
                <div class="vulnerability-badge ${rfClass}">
                    ${rfPred}
                </div>
                <div class="probability-bar">
                    <div class="probability-label">
                        <span>Baixa</span>
                        <span>${(rfProb.Baixa * 100).toFixed(1)}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${rfProb.Baixa * 100}%"></div>
                    </div>
                </div>
                <div class="probability-bar">
                    <div class="probability-label">
                        <span>Média</span>
                        <span>${(rfProb.Média * 100).toFixed(1)}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${rfProb.Média * 100}%"></div>
                    </div>
                </div>
                <div class="probability-bar">
                    <div class="probability-label">
                        <span>Alta</span>
                        <span>${(rfProb.Alta * 100).toFixed(1)}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${rfProb.Alta * 100}%"></div>
                    </div>
                </div>
            </div>
            
            <div class="result-card">
                <h3>⚡ XGBoost</h3>
                <div class="vulnerability-badge ${xgbClass}">
                    ${xgbPred}
                </div>
                <div class="probability-bar">
                    <div class="probability-label">
                        <span>Baixa</span>
                        <span>${(xgbProb.Baixa * 100).toFixed(1)}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${xgbProb.Baixa * 100}%"></div>
                    </div>
                </div>
                <div class="probability-bar">
                    <div class="probability-label">
                        <span>Média</span>
                        <span>${(xgbProb.Média * 100).toFixed(1)}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${xgbProb.Média * 100}%"></div>
                    </div>
                </div>
                <div class="probability-bar">
                    <div class="probability-label">
                        <span>Alta</span>
                        <span>${(xgbProb.Alta * 100).toFixed(1)}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${xgbProb.Alta * 100}%"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div style="margin-top: 20px; padding: 15px; background: #f0f9ff; border-left: 4px solid #2563eb; border-radius: 8px;">
            <strong>📊 Interpretação:</strong><br>
            <span style="margin-top: 10px; display: block;">
                ${getInterpretation({
                    vulnerabilidade_rf: rfPred,
                    vulnerabilidade_xgb: xgbPred
                })}
            </span>
        </div>
    `;
    
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Verificar divergência e alertar
    checkDivergence(rfPred, xgbPred);
}

// Get interpretation
function getInterpretation(data) {
    const rf = data.vulnerabilidade_rf;
    const xgb = data.vulnerabilidade_xgb;
    
    if (rf === xgb) {
        return `Ambos os modelos concordam: vulnerabilidade <strong>${rf}</strong>. 
                Alta confiabilidade na classificação.`;
    } else {
        return `⚠️ <strong style="color: #dc2626;">ATENÇÃO - Os modelos divergem:</strong><br>
                <span style="color: #dc2626;">Random Forest indica <strong>${rf}</strong> e XGBoost indica <strong>${xgb}</strong>.</span><br>
                <span style="color: #ea580c; font-weight: 600;">Recomenda-se análise qualitativa com IA para decisão final.</span>`;
    }
}

// Display LLM analysis
function displayLLMAnalysis(data) {
    if (data.analise_llm) {
        llmContent.textContent = data.analise_llm;
    } else {
        llmContent.innerHTML = `
            <div style="text-align: center; padding: 40px;">
                <p style="font-size: 1.2em; color: #f59e0b;">⚠️ Análise LLM não disponível</p>
                <p style="margin-top: 10px; color: #6b7280;">
                    O serviço pode estar temporariamente indisponível devido ao limite de taxa da API gratuita.
                    <br>Por favor, aguarde alguns segundos e tente novamente.
                </p>
            </div>
        `;
    }
    
    llmSection.style.display = 'block';
    llmSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Handle predict form submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const data = getFormData();
    console.log('📤 Enviando dados para predição:', data);
    showLoading();
    
    try {
        console.log('🔗 POST', `${API_URL}/predict`);
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        console.log('📥 Resposta recebida:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Erro da API:', errorText);
            throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
        }
        
        const result = await response.json();
        console.log('✅ Resultado:', result);
        displayResults(result);
        
        // Hide LLM section
        llmSection.style.display = 'none';
        
    } catch (error) {
        console.error('❌ Erro completo:', error);
        alert(`❌ Erro ao processar análise:\n${error.message}\n\nVerifique o console (F12) para mais detalhes.`);
    } finally {
        hideLoading();
    }
});

// Handle LLM analysis
analyzeLLMBtn.addEventListener('click', async () => {
    const data = getFormData();
    console.log('📤 Enviando dados para análise LLM:', data);
    showLoading();
    loadingText.textContent = 'Gerando análise com IA (pode levar 10-30 segundos)...';
    
    try {
        console.log('🔗 POST', `${API_URL}/analyze`);
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        console.log('📥 Resposta recebida:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Erro da API:', errorText);
            throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
        }
        
        const result = await response.json();
        console.log('✅ Resultado LLM:', result);
        displayResults(result);
        displayLLMAnalysis(result);
        
    } catch (error) {
        console.error('❌ Erro completo:', error);
        alert(`❌ Erro ao processar análise com IA:\n${error.message}\n\nVerifique o console (F12) para mais detalhes.`);
    } finally {
        loadingText.textContent = 'Processando análise...';
        hideLoading();
    }
});

// Check API on load
checkAPIHealth();

// Check API every 30 seconds
setInterval(checkAPIHealth, 30000);

// Verificar divergência entre modelos
function checkDivergence(rfPred, xgbPred) {
    if (rfPred !== xgbPred) {
        // Adicionar animação de pulso no botão LLM
        analyzeLLMBtn.style.animation = 'pulse 2s infinite';
        analyzeLLMBtn.style.boxShadow = '0 0 20px rgba(239, 68, 68, 0.5)';
        
        // Mostrar modal de alerta após 500ms
        setTimeout(() => {
            // Criar modal
            const modal = document.createElement('div');
            modal.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                animation: fadeIn 0.3s ease;
            `;
            
            const modalContent = document.createElement('div');
            modalContent.style.cssText = `
                background: white;
                padding: 30px;
                border-radius: 15px;
                max-width: 500px;
                text-align: center;
                animation: slideIn 0.3s ease;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            `;
            
            modalContent.innerHTML = `
                <div style="font-size: 48px; margin-bottom: 15px;">⚠️</div>
                <h2 style="color: #dc2626; margin-bottom: 15px;">Divergência Detectada!</h2>
                <p style="font-size: 16px; margin-bottom: 20px; color: #374151;">
                    Os modelos <strong>Random Forest</strong> e <strong>XGBoost</strong> discordam na classificação:<br><br>
                    <span style="color: #059669;">Random Forest: <strong>${rfPred}</strong></span><br>
                    <span style="color: #dc2626;">XGBoost: <strong>${xgbPred}</strong></span>
                </p>
                <p style="font-size: 14px; margin-bottom: 25px; color: #6b7280;">
                    Para casos divergentes, recomendamos fortemente usar a <strong>Análise com IA</strong> 
                    para uma avaliação qualitativa completa.
                </p>
                <button id="useLLMBtn" style="
                    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    font-size: 16px;
                    font-weight: 600;
                    border-radius: 8px;
                    cursor: pointer;
                    margin-right: 10px;
                    transition: transform 0.2s;
                ">🤖 Usar Análise com IA</button>
                <button id="dismissBtn" style="
                    background: #e5e7eb;
                    color: #374151;
                    border: none;
                    padding: 15px 30px;
                    font-size: 16px;
                    font-weight: 600;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: transform 0.2s;
                ">Fechar</button>
            `;
            
            modal.appendChild(modalContent);
            document.body.appendChild(modal);
            
            // Evento para usar LLM
            document.getElementById('useLLMBtn').addEventListener('click', () => {
                modal.remove();
                analyzeLLMBtn.click();
            });
            
            // Evento para fechar
            document.getElementById('dismissBtn').addEventListener('click', () => {
                modal.remove();
            });
            
            // Fechar ao clicar fora
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.remove();
                }
            });
        }, 500);
    } else {
        // Remover animação se não houver divergência
        analyzeLLMBtn.style.animation = '';
        analyzeLLMBtn.style.boxShadow = '';
    }
}
