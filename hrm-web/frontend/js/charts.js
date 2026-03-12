/**
 * 图表管理器
 */

class ChartManager {
    constructor() {
        this.ecgChart = null;
        this.accChart = null;
        this.rriChart = null;
        this.maxDataPoints = 500;
        this.ecgData = [];
        this.accData = { x: [], y: [], z: [] };
        this.rriData = [];
        
        this.initCharts();
    }

    initCharts() {
        const commonOptions = {
            responsive: true,
            maintainAspectRatio: true,
            animation: false,
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#cbd5e1'
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                },
                y: {
                    display: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                }
            }
        };

        this.ecgChart = new Chart(document.getElementById('ecg-chart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'ECG (mV)',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 1.5,
                    pointRadius: 0,
                    tension: 0.1
                }]
            },
            options: commonOptions
        });

        this.accChart = new Chart(document.getElementById('acc-chart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'X轴',
                        data: [],
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        borderWidth: 1.5,
                        pointRadius: 0,
                        tension: 0.1
                    },
                    {
                        label: 'Y轴',
                        data: [],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 1.5,
                        pointRadius: 0,
                        tension: 0.1
                    },
                    {
                        label: 'Z轴',
                        data: [],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 1.5,
                        pointRadius: 0,
                        tension: 0.1
                    }
                ]
            },
            options: commonOptions
        });

        this.rriChart = new Chart(document.getElementById('rri-chart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'R-R间期 (ms)',
                    data: [],
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    borderWidth: 2,
                    pointRadius: 3,
                    pointBackgroundColor: '#8b5cf6',
                    tension: 0.1
                }]
            },
            options: commonOptions
        });
    }

    updateECG(ecgValues) {
        if (!ecgValues || ecgValues.length === 0) return;

        this.ecgData.push(...ecgValues);
        
        if (this.ecgData.length > this.maxDataPoints) {
            this.ecgData = this.ecgData.slice(-this.maxDataPoints);
        }

        const labels = Array.from({ length: this.ecgData.length }, (_, i) => i);
        
        this.ecgChart.data.labels = labels;
        this.ecgChart.data.datasets[0].data = this.ecgData;
        this.ecgChart.update('none');
        
        document.getElementById('ecg-count').textContent = `${this.ecgData.length} 点`;
    }

    updateAccelerometer(accData) {
        if (!accData) return;

        this.accData.x.push(accData.x1);
        this.accData.y.push(accData.y1);
        this.accData.z.push(accData.z1);

        ['x', 'y', 'z'].forEach(axis => {
            if (this.accData[axis].length > this.maxDataPoints) {
                this.accData[axis] = this.accData[axis].slice(-this.maxDataPoints);
            }
        });

        const labels = Array.from({ length: this.accData.x.length }, (_, i) => i);
        
        this.accChart.data.labels = labels;
        this.accChart.data.datasets[0].data = this.accData.x;
        this.accChart.data.datasets[1].data = this.accData.y;
        this.accChart.data.datasets[2].data = this.accData.z;
        this.accChart.update('none');
        
        document.getElementById('acc-count').textContent = `${this.accData.x.length} 点`;
    }

    updateRRI(rriValues) {
        if (!rriValues || rriValues.length === 0) return;

        this.rriData.push(...rriValues);
        
        if (this.rriData.length > this.maxDataPoints) {
            this.rriData = this.rriData.slice(-this.maxDataPoints);
        }

        const labels = Array.from({ length: this.rriData.length }, (_, i) => i);
        
        this.rriChart.data.labels = labels;
        this.rriChart.data.datasets[0].data = this.rriData;
        this.rriChart.update('none');
        
        document.getElementById('rri-count').textContent = `${this.rriData.length} 点`;
    }

    clearAll() {
        this.ecgData = [];
        this.accData = { x: [], y: [], z: [] };
        this.rriData = [];
        
        this.ecgChart.data.labels = [];
        this.ecgChart.data.datasets[0].data = [];
        this.ecgChart.update();
        
        this.accChart.data.labels = [];
        this.accChart.data.datasets.forEach(ds => ds.data = []);
        this.accChart.update();
        
        this.rriChart.data.labels = [];
        this.rriChart.data.datasets[0].data = [];
        this.rriChart.update();
        
        document.getElementById('ecg-count').textContent = '0 点';
        document.getElementById('acc-count').textContent = '0 点';
        document.getElementById('rri-count').textContent = '0 点';
    }
}

const chartManager = new ChartManager();
