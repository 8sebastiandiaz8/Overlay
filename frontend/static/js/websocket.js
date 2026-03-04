/**
 * OverlaySocket — WebSocket client for real-time overlay events.
 */
class OverlaySocket {
    constructor(userId) {
        this.userId = userId;
        this.handlers = {};
        this.connect();
    }

    connect() {
        const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.ws = new WebSocket(`${protocol}//${location.host}/ws/${this.userId}`);

        this.ws.onmessage = (e) => {
            try {
                const event = JSON.parse(e.data);
                if (event.type && this.handlers[event.type]) {
                    this.handlers[event.type](event.data);
                }
            } catch {
                // Ignore malformed messages
            }
        };

        this.ws.onerror = () => {
            console.warn('WebSocket error');
        };

        this.ws.onclose = () => {
            // Reconnect after 3 seconds
            setTimeout(() => this.connect(), 3000);
        };
    }

    on(eventType, callback) {
        this.handlers[eventType] = callback;
        return this;
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }
}
