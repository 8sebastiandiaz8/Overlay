/**
 * Chat Box Widget — displays chat messages on the overlay.
 */
(function () {
    const messages = document.getElementById('messages');
    const MAX_MESSAGES = 50;

    function addMessage(data) {
        const el = document.createElement('div');
        el.className = 'chat-message';

        const user = document.createElement('span');
        user.className = 'chat-username';
        user.textContent = data.username || 'Anon';

        const text = document.createTextNode(data.message || '');

        el.appendChild(user);
        el.appendChild(text);
        messages.appendChild(el);

        // Limit messages
        while (messages.children.length > MAX_MESSAGES) {
            messages.removeChild(messages.firstChild);
        }

        // Auto-scroll
        messages.scrollTop = messages.scrollHeight;
    }

    // Listen for messages from parent window
    window.addEventListener('message', (e) => {
        if (e.data && e.data.type === 'chat_message') {
            addMessage(e.data);
        }
    });
})();
