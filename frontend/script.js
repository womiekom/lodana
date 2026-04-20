const API_BASE_URL = 'http://localhost:8000';
let distributionChart = null;

async function checkApiStatus() {
    const statusText = document.getElementById('status-text');
    const statusDot = document.querySelector('.status-dot');
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        if (response.ok) {
            statusText.textContent = 'Online';
            statusDot.style.backgroundColor = 'var(--success)';
        }
    } catch (error) {
        statusText.textContent = 'Offline';
        statusDot.style.backgroundColor = 'var(--danger)';
    }
}

async function fetchDistributionData() {
    const totalArea = document.getElementById('total-area').value;
    const runBtn = document.getElementById('run-btn');
    
    runBtn.disabled = true;
    runBtn.textContent = 'Processing...';

    try {
        // Updated to use GET as the default method
        const response = await fetch(`${API_BASE_URL}/api/distribute-energy?total_area=${totalArea}`);
        
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        updateDashboard(data);
    } catch (error) {
        alert('Error: ' + error.message);
        console.error(error);
    } finally {
        runBtn.disabled = false;
        runBtn.textContent = 'Generate Distribution Plan';
    }
}

function updateDashboard(data) {
    const districts = data.distribution;
    
    // 1. Update Summaries
    const totalProd = data.total_production_kwh;
    let totalSurplus = 0;
    let totalDeficit = 0;
    let utilSum = 0;

    districts.forEach(d => {
        const gap = d.allocated_supply_kwh - d.estimated_demand_kwh;
        if (gap > 0) totalSurplus += gap;
        else totalDeficit += Math.abs(gap);
        utilSum += d.utilization_ratio;
    });

    document.getElementById('total-prod').textContent = totalProd.toLocaleString();
    document.getElementById('total-surplus').textContent = totalSurplus.toLocaleString(undefined, {maximumFractionDigits: 0});
    document.getElementById('total-deficit').textContent = totalDeficit.toLocaleString(undefined, {maximumFractionDigits: 0});
    document.getElementById('avg-utilization').textContent = (utilSum / districts.length).toFixed(1);

    // 2. Update Chart
    renderChart(districts);

    // 3. Update Table
    renderTable(districts);
}

function renderChart(districts) {
    const ctx = document.getElementById('distributionChart').getContext('2d');
    
    const labels = districts.map(d => d.district);
    const supplyData = districts.map(d => d.allocated_supply_kwh);
    const demandData = districts.map(d => d.estimated_demand_kwh);

    if (distributionChart) {
        distributionChart.destroy();
    }

    distributionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Allocated Supply (kWh)',
                    data: supplyData,
                    backgroundColor: '#3b82f6',
                    borderRadius: 4
                },
                {
                    label: 'Estimated Demand (kWh)',
                    data: demandData,
                    backgroundColor: '#94a3b8',
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Energy (kWh)' }
                }
            },
            plugins: {
                legend: { position: 'top' }
            }
        }
    });
}

function renderTable(districts) {
    const tbody = document.getElementById('table-body');
    tbody.innerHTML = '';

    districts.forEach(d => {
        const row = document.createElement('tr');
        const statusClass = d.status === 'Surplus' ? 'badge-surplus' : 'badge-deficit';
        
        row.innerHTML = `
            <td style="font-weight: 500;">${d.district}</td>
            <td>${d.allocated_supply_kwh.toLocaleString()}</td>
            <td>${d.estimated_demand_kwh.toLocaleString()}</td>
            <td>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="flex: 1; height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden;">
                        <div style="width: ${Math.min(d.utilization_ratio, 100)}%; height: 100%; background: ${d.status === 'Surplus' ? 'var(--success)' : 'var(--danger)'};"></div>
                    </div>
                    <span>${d.utilization_ratio}%</span>
                </div>
            </td>
            <td><span class="badge ${statusClass}">${d.status}</span></td>
        `;
        tbody.appendChild(row);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    checkApiStatus();
    document.getElementById('run-btn').addEventListener('click', fetchDistributionData);
    
    // Initial fetch
    fetchDistributionData();
});
