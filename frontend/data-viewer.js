// API Base URL
const API_URL = window.location.origin;

let currentData = null;

// Carregar lista de arquivos ao iniciar
document.addEventListener('DOMContentLoaded', () => {
    carregarArquivos();
});

// Carrega lista de arquivos CSV disponíveis
async function carregarArquivos() {
    try {
        console.log('📁 Carregando arquivos...');
        const response = await fetch(`${API_URL}/data/files`);
        const data = await response.json();
        
        console.log('✅ Arquivos carregados:', data);
        exibirArquivos(data.arquivos);
    } catch (error) {
        console.error('❌ Erro ao carregar arquivos:', error);
        document.getElementById('fileList').innerHTML = `
            <div class="loading">
                <p style="color: #e74c3c;">❌ Erro ao carregar arquivos</p>
                <p style="font-size: 14px;">${error.message}</p>
            </div>
        `;
    }
}

// Exibe cards dos arquivos disponíveis
function exibirArquivos(arquivos) {
    const fileList = document.getElementById('fileList');
    
    if (!arquivos || arquivos.length === 0) {
        fileList.innerHTML = `
            <div class="loading">
                <p>📂 Nenhum arquivo CSV encontrado na pasta data/</p>
                <p style="font-size: 14px;">Adicione arquivos CSV na pasta data/ para começar</p>
            </div>
        `;
        return;
    }
    
    fileList.innerHTML = arquivos.map(arquivo => `
        <div class="file-card" onclick="processarArquivo('${arquivo.caminho_relativo}')">
            <h3>📄 ${arquivo.nome}</h3>
            <div class="file-info">
                <div>📊 ${arquivo.linhas.toLocaleString('pt-BR')} registros</div>
                <div>📈 ${arquivo.colunas} colunas</div>
                <div>💾 ${arquivo.tamanho_mb} MB</div>
            </div>
        </div>
    `).join('');
}

// Processa arquivo selecionado
async function processarArquivo(filepath) {
    console.log('🔄 Processando arquivo:', filepath);
    
    // Obter quantidade selecionada
    const maxRows = document.getElementById('maxRows').value;
    console.log(`📊 Processando ${maxRows} registros`);
    
    // Mostrar loading
    document.getElementById('fileList').innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Processando ${filepath}...</p>
            <p style="font-size: 14px;">Carregando ${parseInt(maxRows).toLocaleString('pt-BR')} registros e aplicando modelos ML...</p>
        </div>
    `;
    
    // Esconder seções anteriores
    document.getElementById('summarySection').style.display = 'none';
    document.getElementById('municipalitySection').style.display = 'none';
    document.getElementById('llmSection').style.display = 'none';
    
    try {
        let data;
        
        // Detectar se é arquivo do governo (base_amostra)
        const isGovFile = filepath.includes('base_amostra');
        
        if (isGovFile) {
            console.log('📋 Arquivo do governo detectado, usando endpoint especial...');
            // Usar endpoint que mapeia automaticamente COM a quantidade selecionada
            const response = await fetch(`${API_URL}/data/analyze-governo?filepath=${encodeURIComponent(filepath)}&max_rows=${maxRows}`);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Erro HTTP: ${response.status}`);
            }
            
            data = await response.json();
            console.log('✅ Arquivo do governo processado:', data.tipo_detectado);
        } else {
            // Usar endpoint normal para arquivos já convertidos
            const response = await fetch(`${API_URL}/data/analyze-municipality?filepath=${encodeURIComponent(filepath)}`);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Erro HTTP: ${response.status}`);
            }
            
            data = await response.json();
        }
        
        console.log('✅ Dados processados:', data);
        
        currentData = data;
        
        // Exibir resultados
        exibirEstatisticasGerais(data);
        exibirMunicipios(data.municipios);
        exibirAnaliseLLM(data.analise_ia || data.analise_llm);
        
        // Recarregar lista de arquivos
        carregarArquivos();
        
    } catch (error) {
        console.error('❌ Erro ao processar arquivo:', error);
        document.getElementById('fileList').innerHTML = `
            <div class="loading">
                <p style="color: #e74c3c;">❌ Erro ao processar arquivo</p>
                <p style="font-size: 14px;">${error.message}</p>
                <button class="btn-process" onclick="carregarArquivos()">Tentar Novamente</button>
            </div>
        `;
    }
}

// Exibe estatísticas gerais
function exibirEstatisticasGerais(data) {
    const section = document.getElementById('summarySection');
    const statsDiv = document.getElementById('summaryStats');
    
    // Calcular estatísticas agregadas
    let totalMuitoAlta = 0, totalAlta = 0, totalMedia = 0, totalBaixa = 0;
    
    data.municipios.forEach(mun => {
        totalMuitoAlta += mun.vulnerabilidade['Muito Alta'];
        totalAlta += mun.vulnerabilidade['Alta'];
        totalMedia += mun.vulnerabilidade['Média'];
        totalBaixa += mun.vulnerabilidade['Baixa'];
    });
    
    const pctMuitoAlta = (totalMuitoAlta / data.total_registros * 100).toFixed(1);
    const pctAlta = (totalAlta / data.total_registros * 100).toFixed(1);
    
    statsDiv.innerHTML = `
        <div class="stat-card">
            <div class="stat-label">📊 Total de Registros</div>
            <div class="stat-value">${data.total_registros.toLocaleString('pt-BR')}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">📍 Municípios Analisados</div>
            <div class="stat-value">${data.total_municipios}</div>
        </div>
        <div class="stat-card" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);">
            <div class="stat-label">🔴 Vulnerabilidade Muito Alta</div>
            <div class="stat-value">${pctMuitoAlta}%</div>
            <div class="stat-label">${totalMuitoAlta.toLocaleString('pt-BR')} famílias</div>
        </div>
        <div class="stat-card" style="background: linear-gradient(135deg, #e67e22 0%, #d35400 100%);">
            <div class="stat-label">🟠 Vulnerabilidade Alta</div>
            <div class="stat-value">${pctAlta}%</div>
            <div class="stat-label">${totalAlta.toLocaleString('pt-BR')} famílias</div>
        </div>
    `;
    
    section.style.display = 'block';
}

// Exibe cards de municípios
function exibirMunicipios(municipios) {
    const section = document.getElementById('municipalitySection');
    const grid = document.getElementById('municipalityGrid');
    
    grid.innerHTML = municipios.map(mun => {
        const total = mun.total_familias;
        const vuln = mun.vulnerabilidade_percentual;
        const nomeMunicipio = mun.nome_municipio || `Município ${mun.codigo_municipio}`;
        
        return `
            <div class="municipality-card">
                <div class="municipality-header">
                    <div class="municipality-code">
                        📍 ${nomeMunicipio}
                    </div>
                    <div class="municipality-total">
                        ${total.toLocaleString('pt-BR')} famílias
                    </div>
                </div>
                
                <div class="vulnerability-bars">
                    <div class="vuln-bar">
                        <div class="vuln-bar-label">
                            <span>Muito Alta</span>
                            <span>${vuln['Muito Alta']}%</span>
                        </div>
                        <div class="vuln-bar-fill vuln-muito-alta" style="width: ${vuln['Muito Alta']}%">
                            ${mun.vulnerabilidade['Muito Alta']}
                        </div>
                    </div>
                    
                    <div class="vuln-bar">
                        <div class="vuln-bar-label">
                            <span>Alta</span>
                            <span>${vuln['Alta']}%</span>
                        </div>
                        <div class="vuln-bar-fill vuln-alta" style="width: ${vuln['Alta']}%">
                            ${mun.vulnerabilidade['Alta']}
                        </div>
                    </div>
                    
                    <div class="vuln-bar">
                        <div class="vuln-bar-label">
                            <span>Média</span>
                            <span>${vuln['Média']}%</span>
                        </div>
                        <div class="vuln-bar-fill vuln-media" style="width: ${Math.max(vuln['Média'], 5)}%">
                            ${mun.vulnerabilidade['Média']}
                        </div>
                    </div>
                    
                    <div class="vuln-bar">
                        <div class="vuln-bar-label">
                            <span>Baixa</span>
                            <span>${vuln['Baixa']}%</span>
                        </div>
                        <div class="vuln-bar-fill vuln-baixa" style="width: ${Math.max(vuln['Baixa'], 5)}%">
                            ${mun.vulnerabilidade['Baixa']}
                        </div>
                    </div>
                </div>
                
                <div class="indicators">
                    <div class="indicator">
                        <span class="indicator-label">💰 Renda per capita média</span>
                        <span class="indicator-value">R$ ${mun.indicadores.renda_per_capita_media.toFixed(2)}</span>
                    </div>
                    <div class="indicator">
                        <span class="indicator-label">👥 Tamanho médio da família</span>
                        <span class="indicator-value">${mun.indicadores.tamanho_familia_medio.toFixed(1)} pessoas</span>
                    </div>
                    <div class="indicator">
                        <span class="indicator-label">👴 Idade média</span>
                        <span class="indicator-value">${mun.indicadores.idade_media.toFixed(1)} anos</span>
                    </div>
                    <div class="indicator">
                        <span class="indicator-label">🎫 Bolsa Família</span>
                        <span class="indicator-value">${mun.indicadores.percentual_bolsa_familia.toFixed(1)}%</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    section.style.display = 'block';
}

// Exibe análise LLM formatada
function exibirAnaliseLLM(analise) {
    const section = document.getElementById('llmSection');
    const content = document.getElementById('llmContent');
    
    if (!analise || analise.includes('não disponível')) {
        content.innerHTML = `
            <p style="color: #e67e22;">
                ⚠️ Análise LLM não disponível. Configure a API key do Google Gemini para obter análises interpretativas.
            </p>
        `;
    } else {
        // Formatar markdown básico
        let formattedAnalise = analise
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/### (.*?)(\n|$)/g, '<h3>$1</h3>')
            .replace(/## (.*?)(\n|$)/g, '<h3>$1</h3>')
            .replace(/# (.*?)(\n|$)/g, '<h3>$1</h3>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/^\d+\.\s/gm, '<li>')
            .replace(/^-\s/gm, '<li>');
        
        content.innerHTML = `<p>${formattedAnalise}</p>`;
    }
    
    section.style.display = 'block';
}
