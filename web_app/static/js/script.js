// static/js/script.js
let latencyChart, throughputChart;
let updateInterval;

function toggleTest() {
    const form = document.getElementById('configForm');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

async function startTest() {
    // Clear existing charts only when starting a new session
    if (latencyChart) {
        latencyChart.destroy();
        latencyChart = null;
    }
    if (throughputChart) {
        throughputChart.destroy();
        throughputChart = null;
    }

    const name = document.getElementById('testName').value;
    const duration = document.getElementById('duration').value;
    
    const response = await fetch('api/sessions', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            name: name,
            config: { duration: parseFloat(duration) }
        })
    });
    
    if (response.ok) {
        toggleTest();
        startMonitoring();
    }
}

async function killTest() {
    const response = await fetch('api/sessions/current', {
        method: 'DELETE'
    });
    
    if (response.ok) {
        alert('Test session terminated');
        clearInterval(updateInterval);
        // Removed chart destruction here
    } else {
        const error = await response.json();
        alert(error.error || 'Failed to stop test');
    }
}

async function updateMetrics() {
    const response = await fetch('api/sessions/current');
    const data = await response.json();
    
    if (data.error) {
        clearInterval(updateInterval);
        // Removed chart destruction here
        return;
    }
    
    updateCharts(data.metrics);
}


function startMonitoring() {
    if (updateInterval) clearInterval(updateInterval);
    updateInterval = setInterval(updateMetrics, 5000);
    updateMetrics();
}

function updateCharts(metrics) {
    const latencyCtx = document.getElementById('latencyChart').getContext('2d');
    const throughputCtx = document.getElementById('throughputChart').getContext('2d');

    // Generate dynamic labels based on current data length
    const latencyLabels = metrics.latency_history.map((_, i) => i);
    const throughputLabels = metrics.throughput_history.map((_, i) => i);

    if (!latencyChart) {
        latencyChart = new Chart(latencyCtx, {
            type: 'line',
            data: {
                labels: latencyLabels,
                datasets: [{
                    label: 'Latency (seconds)',
                    data: metrics.latency_history,
                    borderColor: '#ff6384',
                    fill: false
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        type: 'linear',
                        title: {
                            display: true,
                            text: 'Seconds'
                        }
                    }
                }
            }
        });
    } else {
        // Update both labels and data
        latencyChart.data.labels = latencyLabels;
        latencyChart.data.datasets[0].data = metrics.latency_history;
        latencyChart.update();
    }

    if (!throughputChart) {
        throughputChart = new Chart(throughputCtx, {
            type: 'line',
            data: {
                labels: throughputLabels,
                datasets: [{
                    label: 'Requests/Second',
                    data: metrics.throughput_history,
                    borderColor: '#36a2eb',
                    fill: false
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: false,
                        type: 'logarithmic', // Better for large value ranges
                        title: {
                            display: true,
                            text: 'Req/Sec'
                        }
                    }
                }
            }
        });
    } else {
        // Update both labels and data
        throughputChart.data.labels = throughputLabels;
        throughputChart.data.datasets[0].data = metrics.throughput_history;
        throughputChart.update();
    }
}

// Initial load of archived tests
fetch('api/sessions/archived')
    .then(r => r.json())
    .then(sessions => {
        const list = document.getElementById('archivedList');
        sessions.forEach(session => {
            const li = document.createElement('li');
            li.textContent = session;
            li.onclick = () => viewArchived(session);
            list.appendChild(li);
        });
    });

async function viewArchived(name) {
    const response = await fetch(`api/sessions/archived/${name}`);
    const data = await response.json();
    alert(`Session ${name}\nDuration: ${data.metrics.duration}s\nTotal Requests: ${data.metrics.total_requests}`);
}