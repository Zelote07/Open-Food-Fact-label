// Navigation Logic
const navBtns = document.querySelectorAll('.nav-btn');
const sections = document.querySelectorAll('.page-section');

navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        navBtns.forEach(b => b.classList.remove('active'));
        sections.forEach(s => s.classList.remove('active'));
        
        btn.classList.add('active');
        const targetId = btn.getAttribute('data-target');
        document.getElementById(targetId).classList.add('active');

        if (['nutri-ml', 'nutri-shap', 'eco-ml', 'eco-shap'].includes(targetId)) {
            window.dispatchEvent(new Event('resize'));
        }
    });
});

// Theme Toggle Logic
const themeBtn = document.getElementById('theme-toggle');
let isDarkMode = false;

themeBtn.addEventListener('click', () => {
    isDarkMode = !isDarkMode;
    if (isDarkMode) {
        document.documentElement.setAttribute('data-theme', 'dark');
        themeBtn.innerText = 'MODE CLAIR';
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        themeBtn.innerText = 'MODE SOMBRE';
    }
    renderPlots();
});

// ML Dash Initialization
function initMLDash() {
    if (typeof mlData === 'undefined') return;

    // --- NUTRI-SCORE ---
    if (mlData.nutri) {
        const kpiCont = document.getElementById('nutri-kpi-container');
        const acc = (mlData.nutri.metrics.accuracy * 100).toFixed(1) + '%';
        const f1 = (mlData.nutri.metrics.f1_macro * 100).toFixed(1) + '%';
        kpiCont.innerHTML = `
            <div class="kpi-box"><div class="kpi-val">${acc}</div><div class="kpi-label">ACCURACY</div></div>
            <div class="kpi-box"><div class="kpi-val">${f1}</div><div class="kpi-label">MACRO F1</div></div>
            <div class="kpi-box"><div class="kpi-val">${mlData.nutri.metrics.log_loss}</div><div class="kpi-label">LOG LOSS</div></div>
        `;
    }

    // --- ECO-SCORE ---
    if (mlData.eco) {
        const kpiCont = document.getElementById('eco-kpi-container');
        const acc = (mlData.eco.metrics.accuracy * 100).toFixed(1) + '%';
        const f1 = (mlData.eco.metrics.f1_macro * 100).toFixed(1) + '%';
        kpiCont.innerHTML = `
            <div class="kpi-box"><div class="kpi-val">${acc}</div><div class="kpi-label">ACCURACY</div></div>
            <div class="kpi-box"><div class="kpi-val">${f1}</div><div class="kpi-label">MACRO F1</div></div>
            <div class="kpi-box"><div class="kpi-val">${mlData.eco.metrics.log_loss}</div><div class="kpi-label">LOG LOSS</div></div>
        `;
    }

    renderPlots();
}

function renderPlots() {
    if (typeof mlData === 'undefined') return;

    const fontColor = isDarkMode ? '#F5F5F5' : '#111111';
    const gridColor = isDarkMode ? '#333333' : '#CCCCCC';
    const accentColor = isDarkMode ? '#FF5A5A' : '#E13D3D';
    const ecoColor = isDarkMode ? '#04C463' : '#038141';

    const layoutConfig = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: { l: 40, r: 20, t: 10, b: 30 },
        font: { family: 'Space Mono, monospace', color: fontColor, size: 10 },
        xaxis: { gridcolor: gridColor, zerolinecolor: gridColor },
        yaxis: { gridcolor: gridColor, zerolinecolor: gridColor }
    };

    // Nutri-Score Charts
    if (mlData.nutri.learning_curves) {
        Plotly.newPlot('nutri-learning-curves-chart', [
            { x: mlData.nutri.learning_curves.epoch, y: mlData.nutri.learning_curves.train_loss, type: 'scatter', mode: 'lines', name: 'TRAIN', line: {color: fontColor, width: 2} },
            { x: mlData.nutri.learning_curves.epoch, y: mlData.nutri.learning_curves.val_loss, type: 'scatter', mode: 'lines', name: 'VAL', line: {color: accentColor, width: 2} }
        ], { ...layoutConfig, legend: { orientation: 'h', y: 1.1 } }, {responsive: true});
    }


    if (mlData.nutri.feature_importance) {
        Plotly.newPlot('nutri-shap-bar-chart', [{
            x: mlData.nutri.feature_importance.Importance, y: mlData.nutri.feature_importance.Feature,
            type: 'bar', orientation: 'h', marker: { color: fontColor }
        }], { ...layoutConfig, margin: { l: 150, r: 20, t: 10, b: 40 }, xaxis: {gridcolor: gridColor}, yaxis: {showgrid: false} }, {responsive: true});
    }

    // Eco-Score Charts
    if (mlData.eco.learning_curves) {
        Plotly.newPlot('eco-learning-curves-chart', [
            { x: mlData.eco.learning_curves.epoch, y: mlData.eco.learning_curves.train_loss, type: 'scatter', mode: 'lines', name: 'TRAIN', line: {color: fontColor, width: 2} },
            { x: mlData.eco.learning_curves.epoch, y: mlData.eco.learning_curves.val_loss, type: 'scatter', mode: 'lines', name: 'VAL', line: {color: ecoColor, width: 2} }
        ], { ...layoutConfig, legend: { orientation: 'h', y: 1.1 } }, {responsive: true});
    }


    if (mlData.eco.feature_importance) {
        Plotly.newPlot('eco-shap-bar-chart', [{
            x: mlData.eco.feature_importance.Importance, y: mlData.eco.feature_importance.Feature,
            type: 'bar', orientation: 'h', marker: { color: ecoColor }
        }], { ...layoutConfig, margin: { l: 150, r: 20, t: 10, b: 40 }, xaxis: {gridcolor: gridColor}, yaxis: {showgrid: false} }, {responsive: true});
    }
}

// -------------------------------------------------------------------------
// SIMULATEURS
// -------------------------------------------------------------------------

const points = {
    energy: val => val <= 335 ? 0 : val > 3350 ? 10 : Math.floor((val - 0.0001) / 335),
    sugar: val => val <= 3.4 ? 0 : val > 51.0 ? 15 : Math.floor((val - 0.0001) / 3.4),
    sfa: val => val <= 1 ? 0 : val > 10 ? 10 : Math.floor((val - 0.0001) / 1.0),
    salt: val => val <= 0.2 ? 0 : val > 4.0 ? 20 : Math.floor((val - 0.0001) / 0.2),
    proteins: val => val <= 2.4 ? 0 : val > 16.8 ? 7 : Math.floor((val - 0.0001) / 2.4),
    fibers: val => val <= 3.0 ? 0 : val <= 4.1 ? 1 : val <= 5.2 ? 2 : val <= 6.3 ? 3 : val <= 7.4 ? 4 : 5
};

function calculateNutriScore() {
    const e = parseFloat(document.getElementById('inp-energy').value) || 0;
    const su = parseFloat(document.getElementById('inp-sugar').value) || 0;
    const sfa = parseFloat(document.getElementById('inp-sfa').value) || 0;
    const sa = parseFloat(document.getElementById('inp-salt').value) || 0;
    
    const p = parseFloat(document.getElementById('inp-proteins').value) || 0;
    const f = parseFloat(document.getElementById('inp-fibers').value) || 0;

    const ptA = points.energy(e) + points.sugar(su) + points.sfa(sfa) + points.salt(sa);
    const ptC = points.proteins(p) + points.fibers(f);

    let score = ptA - ptC;
    let details = `A(${ptA}) - C(${ptC})`;

    let letter = "E"; let color = "#E13D3D";
    if (score <= 0) { letter = "A"; color = "#038141"; }
    else if (score <= 2) { letter = "B"; color = "#85BB2F"; }
    else if (score <= 10) { letter = "C"; color = "#FECB02"; }
    else if (score <= 18) { letter = "D"; color = "#EE8100"; }

    const badge = document.getElementById('nutri-badge');
    if(badge) {
        badge.innerText = letter;
        badge.style.color = color;
        document.getElementById('nutri-score-val').innerText = score;
        document.getElementById('nutri-details').innerText = details;
    }
}

function calculateEcoScore() {
    const pefSelect = document.getElementById('inp-pef');
    if(!pefSelect) return;

    const pef = parseInt(pefSelect.value) || 0;
    let bonus = 0;
    
    const origin = document.getElementById('inp-origin').value;
    bonus += parseInt(origin);
    
    bonus += parseInt(document.getElementById('inp-bio').value) || 0;
    bonus += parseInt(document.getElementById('inp-pack').value) || 0;
    
    let score = pef + bonus;
    if (score > 100) score = 100;
    if (score < 0) score = 0;

    let letter = "E"; let color = "#E13D3D";
    if (score >= 80) { letter = "A"; color = "#038141"; }
    else if (score >= 60) { letter = "B"; color = "#85BB2F"; }
    else if (score >= 40) { letter = "C"; color = "#FECB02"; }
    else if (score >= 20) { letter = "D"; color = "#EE8100"; }

    const badge = document.getElementById('eco-badge');
    badge.innerText = letter;
    badge.style.color = color;
    document.getElementById('eco-score-val').innerText = score + "/100";
    document.getElementById('eco-details').innerText = `${pef} PEF ${bonus >= 0 ? '+' : ''}${bonus} bonus`;
}

// Global Listeners
const inputs = document.querySelectorAll('input, select');
inputs.forEach(inp => {
    inp.addEventListener('input', () => {
        calculateNutriScore();
        calculateEcoScore();
    });
});

window.addEventListener('DOMContentLoaded', () => {
    initMLDash();
    calculateNutriScore();
    calculateEcoScore();
});
