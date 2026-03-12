/**
 * 主应用逻辑
 */

class App {
    constructor() {
        this.packetCount = 0;
        this.currentMode = 'unknown';
        this.isConnected = false;
        this.statusCheckInterval = null;
        
        this.initElements();
        this.initEventListeners();
        this.initWebSocket();
        this.updateStatus();
        this.startStatusCheck();
    }

    initElements() {
        this.elements = {
            connectionStatus: document.getElementById('connection-status'),
            deviceMode: document.getElementById('device-mode'),
            heartRate: document.getElementById('heart-rate'),
            steps: document.getElementById('steps'),
            cadence: document.getElementById('cadence'),
            sportTime: document.getElementById('sport-time'),
            packetCount: document.getElementById('packet-count'),
            btnConnect: document.getElementById('btn-connect'),
            btnDisconnect: document.getElementById('btn-disconnect'),
            modeButtons: document.querySelectorAll('.btn-mode')
        };
    }

    initEventListeners() {
        this.elements.btnConnect.addEventListener('click', () => this.connectDevice());
        this.elements.btnDisconnect.addEventListener('click', () => this.disconnectDevice());
        
        this.elements.modeButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const mode = btn.dataset.mode;
                this.setMode(mode);
            });
        });
    }

    initWebSocket() {
        wsClient.onMessage((message) => this.handleWebSocketMessage(message));
        wsClient.connect();
    }

    startStatusCheck() {
        this.statusCheckInterval = setInterval(() => {
            this.updateStatus();
        }, 3000);
    }

    stopStatusCheck() {
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
            this.statusCheckInterval = null;
        }
    }

    async updateStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            this.isConnected = status.connected;
            this.currentMode = status.mode;
            
            this.elements.connectionStatus.textContent = status.connected ? '已连接' : '未连接';
            this.elements.connectionStatus.className = `status-value ${status.connected ? 'connected' : 'disconnected'}`;
            this.elements.deviceMode.textContent = this.getModeDisplayName(status.mode);
            
            this.updateButtonStates();
            this.updateModeButtons();
            
        } catch (e) {
            console.error('获取状态失败:', e);
        }
    }

    getModeDisplayName(mode) {
        const modeNames = {
            'sport': '运动模式',
            'ecg': '心电模式',
            'hrv': 'HRV模式',
            'unknown': '未知'
        };
        return modeNames[mode] || mode;
    }

    updateButtonStates() {
        this.elements.btnConnect.disabled = this.isConnected;
        this.elements.btnDisconnect.disabled = !this.isConnected;
        
        this.elements.modeButtons.forEach(btn => {
            btn.disabled = !this.isConnected;
        });
    }

    updateModeButtons() {
        this.elements.modeButtons.forEach(btn => {
            if (btn.dataset.mode === this.currentMode) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    async connectDevice() {
        try {
            this.elements.btnConnect.disabled = true;
            this.elements.btnConnect.textContent = '连接中...';
            
            const response = await fetch('/api/connect', { method: 'POST' });
            
            if (response.ok) {
                const result = await response.json();
                chartManager.clearAll();
                this.packetCount = 0;
                await new Promise(resolve => setTimeout(resolve, 1000));
                await this.updateStatus();
            } else {
                const error = await response.json();
                alert('设备连接失败: ' + (error.detail || '未知错误'));
            }
            
        } catch (e) {
            console.error('连接设备失败:', e);
            alert('连接设备失败: ' + e.message);
        } finally {
            this.elements.btnConnect.textContent = '连接设备';
            await this.updateStatus();
        }
    }

    async disconnectDevice() {
        try {
            const response = await fetch('/api/disconnect', { method: 'POST' });
            const result = await response.json();
            
            if (result.success) {
                await this.updateStatus();
            }
            
        } catch (e) {
            console.error('断开连接失败:', e);
        }
    }

    async setMode(mode) {
        try {
            const btn = document.querySelector(`[data-mode="${mode}"]`);
            const originalText = btn.textContent;
            
            this.elements.modeButtons.forEach(b => b.disabled = true);
            btn.textContent = '切换中...';
            
            const response = await fetch('/api/mode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode })
            });
            
            if (response.ok) {
                const result = await response.json();
                chartManager.clearAll();
                this.packetCount = 0;
                
                await new Promise(resolve => setTimeout(resolve, 1500));
                await this.updateStatus();
            } else {
                const error = await response.json();
                const errorMsg = error.detail || '未知错误';
                alert('模式切换失败: ' + errorMsg);
                
                if (errorMsg.includes('断开连接')) {
                    await this.updateStatus();
                }
            }
            
        } catch (e) {
            console.error('设置模式失败:', e);
            alert('模式切换失败: ' + e.message);
            await this.updateStatus();
        } finally {
            this.elements.modeButtons.forEach(btn => {
                btn.disabled = !this.isConnected;
                const modeName = btn.dataset.mode;
                btn.textContent = modeName === 'sport' ? '运动模式' : 
                                 modeName === 'ecg' ? '心电模式' : 'HRV模式';
            });
        }
    }

    handleWebSocketMessage(message) {
        this.packetCount++;
        this.elements.packetCount.textContent = this.packetCount;

        switch (message.type) {
            case 'ECG':
                if (message.data && message.data.ecg) {
                    chartManager.updateECG(message.data.ecg);
                }
                break;

            case 'GSensor':
                if (message.data) {
                    chartManager.updateAccelerometer(message.data);
                }
                break;

            case 'HR':
                if (message.data) {
                    this.updateHeartRateInfo(message.data);
                }
                break;

            case 'RRI':
                if (message.data && message.data.rri) {
                    chartManager.updateRRI(message.data.rri);
                }
                break;

            case 'ModeUpdate':
                if (message.data && message.data.mode) {
                    this.currentMode = message.data.mode;
                    this.elements.deviceMode.textContent = this.getModeDisplayName(message.data.mode);
                    this.updateModeButtons();
                }
                break;

            case 'SportModel':
            case 'XO':
            case 'SR':
                setTimeout(() => this.updateStatus(), 100);
                break;
            
            case 'pong':
                break;
        }
    }

    updateHeartRateInfo(data) {
        if (data.heart_rate !== undefined) {
            this.elements.heartRate.textContent = `${data.heart_rate.toFixed(1)} BPM`;
        }
        if (data.steps !== undefined) {
            this.elements.steps.textContent = data.steps;
        }
        if (data.cadence !== undefined) {
            this.elements.cadence.textContent = data.cadence;
        }
        if (data.sport_time !== undefined) {
            this.elements.sportTime.textContent = `${data.sport_time}s`;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});
