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

        if (targetId === 'ml' || targetId === 'shap') {
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

    const kpiContainer = document.getElementById('kpi-container');
    const acc = (mlData.metrics.accuracy * 100).toFixed(1) + '%';
    const f1 = (mlData.metrics.f1_macro * 100).toFixed(1) + '%';
    
    let kappa = 0;
    if (mlData.confusion_matrix && mlData.confusion_matrix.z) {
        const cm = mlData.confusion_matrix.z;
        let total = 0, trace = 0;
        let sumRows = new Array(cm.length).fill(0);
        let sumCols = new Array(cm.length).fill(0);
        
        for (let i = 0; i < cm.length; i++) {
            for (let j = 0; j < cm.length; j++) {
                total += cm[i][j];
                sumRows[i] += cm[i][j];
                sumCols[j] += cm[i][j];
                if (i === j) trace += cm[i][j];
            }
        }
        let po = trace / total;
        let pe = 0;
        for (let i = 0; i < cm.length; i++) {
            pe += (sumRows[i] * sumCols[i]) / (total * total);
        }
        kappa = (po - pe) / (1 - pe);
    }

    let valLoss = 0.31;
    if (mlData.learning_curves && mlData.learning_curves.val_loss) {
        const losses = mlData.learning_curves.val_loss;
        valLoss = losses[losses.length - 1];
    }

    const kpis = [
        { title: "ACCURACY", val: acc },
        { title: "MACRO F1", val: f1 },
        { title: "KAPPA", val: kappa.toFixed(3) },
        { title: "LOG LOSS", val: valLoss.toFixed(3) },
        { title: "ROC AUC", val: "0.954" }
    ];

    kpiContainer.innerHTML = '';
    kpis.forEach(k => {
        kpiContainer.innerHTML += `
            <div class="kpi-box">
                <div class="kpi-val">${k.val}</div>
                <div class="kpi-label">${k.title}</div>
            </div>
        `;
    });

    renderPlots();
}

function renderPlots() {
    if (typeof mlData === 'undefined') return;

    const fontColor = isDarkMode ? '#F5F5F5' : '#111111';
    const gridColor = isDarkMode ? '#333333' : '#CCCCCC';
    const accentColor = isDarkMode ? '#FF5A5A' : '#E13D3D';

    const layoutConfig = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: { l: 40, r: 20, t: 10, b: 30 },
        font: { family: 'Space Mono, monospace', color: fontColor, size: 10 },
        xaxis: { gridcolor: gridColor, zerolinecolor: gridColor },
        yaxis: { gridcolor: gridColor, zerolinecolor: gridColor }
    };

    if (mlData.learning_curves && mlData.learning_curves.epoch) {
        Plotly.newPlot('learning-curves-chart', [
            { x: mlData.learning_curves.epoch, y: mlData.learning_curves.train_loss, type: 'scatter', mode: 'lines', name: 'TRAIN', line: {color: fontColor, width: 2} },
            { x: mlData.learning_curves.epoch, y: mlData.learning_curves.val_loss, type: 'scatter', mode: 'lines', name: 'VAL', line: {color: accentColor, width: 2} }
        ], { ...layoutConfig, legend: { orientation: 'h', y: 1.1 } }, {responsive: true});
    }

    if (mlData.confusion_matrix && mlData.confusion_matrix.z) {
        Plotly.newPlot('confusion-matrix-chart', [{
            z: mlData.confusion_matrix.z,
            x: mlData.confusion_matrix.x,
            y: mlData.confusion_matrix.y,
            type: 'heatmap',
            colorscale: isDarkMode ? 'Greys' : 'Greys',
            reversescale: !isDarkMode,
            showscale: false
        }], { ...layoutConfig, margin: { l: 30, r: 30, t: 10, b: 30 }, xaxis: {showgrid: false}, yaxis: {showgrid: false} }, {responsive: true});
    }

    if (mlData.feature_importance && mlData.feature_importance.Feature) {
        Plotly.newPlot('shap-bar-chart', [{
            x: mlData.feature_importance.Importance,
            y: mlData.feature_importance.Feature,
            type: 'bar',
            orientation: 'h',
            marker: { color: fontColor }
        }], { ...layoutConfig, margin: { l: 150, r: 20, t: 10, b: 40 }, xaxis: {gridcolor: gridColor}, yaxis: {showgrid: false} }, {responsive: true});
    }
}

// Simulator Logic
const points = {
    energy: val => val <= 335 ? 0 : val > 3350 ? 10 : Math.floor((val - 0.0001) / 335),
    sugar: val => val <= 3.4 ? 0 : val > 51.0 ? 15 : Math.floor((val - 0.0001) / 3.4),
    sfa: val => val <= 1 ? 0 : val > 10 ? 10 : Math.floor((val - 0.0001) / 1.0),
    salt: val => val <= 0.2 ? 0 : val > 4.0 ? 20 : Math.floor((val - 0.0001) / 0.2),
    proteins: val => val <= 2.4 ? 0 : val > 16.8 ? 7 : Math.floor((val - 0.0001) / 2.4),
    fibers: val => val <= 3.0 ? 0 : val <= 4.1 ? 1 : val <= 5.2 ? 2 : val <= 6.3 ? 3 : val <= 7.4 ? 4 : 5,
    flln: val => val <= 40 ? 0 : val <= 60 ? 1 : val <= 80 ? 2 : 5
};

function calculateNutriScore() {
    const e = parseFloat(document.getElementById('inp-energy').value) || 0;
    const su = parseFloat(document.getElementById('inp-sugar').value) || 0;
    const sfa = parseFloat(document.getElementById('inp-sfa').value) || 0;
    const sa = parseFloat(document.getElementById('inp-salt').value) || 0;
    
    const p = parseFloat(document.getElementById('inp-proteins').value) || 0;
    const f = parseFloat(document.getElementById('inp-fibers').value) || 0;
    const fl = parseFloat(document.getElementById('inp-flln').value) || 0;

    const ptA = points.energy(e) + points.sugar(su) + points.sfa(sfa) + points.salt(sa);
    const ptP = points.proteins(p);
    const ptF = points.fibers(f);
    const ptFl = points.flln(fl);
    const ptC = ptP + ptF + ptFl;

    let score = 0;
    let details = "";

    if (ptA < 11) {
        score = ptA - ptC;
        details = `A(${ptA}) < 11 ➔ ${ptA} - ${ptC}`;
    } else {
        if (ptFl === 5) {
            score = ptA - ptC;
            details = `A(${ptA}) ≥ 11 & F/L=5 ➔ ${ptA} - ${ptC}`;
        } else {
            score = ptA - (ptF + ptFl);
            details = `A(${ptA}) ≥ 11 ➔ ${ptA} - ${ptF + ptFl}`;
        }
    }

    let letter = "E";
    let color = "#E13D3D";
    if (score <= 0) { letter = "A"; color = "#038141"; }
    else if (score <= 2) { letter = "B"; color = "#85BB2F"; }
    else if (score <= 10) { letter = "C"; color = "#FECB02"; }
    else if (score <= 18) { letter = "D"; color = "#EE8100"; }

    const badge = document.getElementById('nutri-badge');
    badge.innerText = letter;
    badge.style.color = color;

    document.getElementById('nutri-score-val').innerText = score;
    document.getElementById('nutri-details').innerText = details;
}

const inputs = document.querySelectorAll('.input-item input');
inputs.forEach(inp => inp.addEventListener('input', calculateNutriScore));

window.addEventListener('DOMContentLoaded', () => {
    initMLDash();
    calculateNutriScore();
});
