console.log("Blue Tech Landing Page Loaded");

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Helper for Logging
function log(message, type = 'info') {
    const consoleLogs = document.getElementById('console-logs');
    const outputArea = document.getElementById('output-area');

    outputArea.style.display = 'block';

    let color = '#0f0'; // green
    if (type === 'error') color = '#ef4444'; // red
    if (type === 'warn') color = '#f59e0b'; // orange

    const line = document.createElement('div');
    line.style.color = color;
    line.style.marginBottom = '5px';
    line.innerText = `> ${message}`;

    consoleLogs.appendChild(line);
    consoleLogs.scrollTop = consoleLogs.scrollHeight;
}

async function runNewsScraper() {
    const btn = document.getElementById('btn-news');
    const originalText = btn.innerHTML;

    try {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Ejecutando...';
        log('Iniciando Scraping de Noticias...', 'info');

        const response = await fetch('/api/run-news', { method: 'POST' });
        const data = await response.json();

        if (data.status === 'success') {
            log(data.message, 'info');
            log(`Noticias guardadas en 'noticias_mundo.csv'`, 'info');
        } else {
            log(`Error: ${data.message}`, 'error');
        }

    } catch (error) {
        log(`Error de conexión: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

async function runPriceScraper() {
    const btn = document.getElementById('btn-prices');
    const originalText = btn.innerHTML;

    try {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Buscando Precios...';
        log('Iniciando Monitor de Precios (Tailoy, Brasil, Materiales BO)...', 'info');

        const response = await fetch('/api/run-prices', { method: 'POST' });
        const data = await response.json();

        if (data.logs && Array.isArray(data.logs)) {
            data.logs.forEach(msg => log(msg, 'info'));
        }

        if (data.status === 'success' || data.status === 'warning') {
            log(data.message, data.status === 'success' ? 'info' : 'warn');
        } else {
            log(`Error: ${data.message}`, 'error');
        }

    } catch (error) {
        log(`Error de conexión: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}
