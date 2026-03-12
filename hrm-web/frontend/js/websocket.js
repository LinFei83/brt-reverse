/**
 * WebSocket 客户端管理
 */

class WebSocketClient {
    constructor() {
        this.ws = null;
        this.reconnectInterval = 3000;
        this.reconnectTimer = null;
        this.isManualClose = false;
        this.messageHandlers = new Set();
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket 连接已建立');
            this.isManualClose = false;
            if (this.reconnectTimer) {
                clearTimeout(this.reconnectTimer);
                this.reconnectTimer = null;
            }
            this.startHeartbeat();
        };

        this.ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.handleMessage(message);
            } catch (e) {
                console.error('解析消息失败:', e);
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket 错误:', error);
        };

        this.ws.onclose = () => {
            console.log('WebSocket 连接已关闭');
            this.stopHeartbeat();
            
            if (!this.isManualClose) {
                this.reconnectTimer = setTimeout(() => {
                    console.log('尝试重新连接...');
                    this.connect();
                }, this.reconnectInterval);
            }
        };
    }

    disconnect() {
        this.isManualClose = true;
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }

    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            this.send({ type: 'ping' });
        }, 30000);
    }

    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }

    onMessage(handler) {
        this.messageHandlers.add(handler);
    }

    offMessage(handler) {
        this.messageHandlers.delete(handler);
    }

    handleMessage(message) {
        this.messageHandlers.forEach(handler => {
            try {
                handler(message);
            } catch (e) {
                console.error('消息处理器错误:', e);
            }
        });
    }
}

const wsClient = new WebSocketClient();
