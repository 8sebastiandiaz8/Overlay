/**
 * Alert Box Widget — shows animated alerts for stream events.
 */
(function () {
    const container = document.getElementById('alert-container');
    const username = container.querySelector('.alert-username');
    const message = container.querySelector('.alert-message');
    const icon = container.querySelector('.alert-icon');

    const alertQueue = [];
    let isShowing = false;

    function showAlert(data) {
        alertQueue.push(data);
        if (!isShowing) processQueue();
    }

    function processQueue() {
        if (alertQueue.length === 0) {
            isShowing = false;
            return;
        }
        isShowing = true;
        const data = alertQueue.shift();

        // Set content based on event type
        switch (data.type) {
            case 'follow':
                icon.textContent = '💜';
                username.textContent = data.username || 'Someone';
                message.textContent = 'just followed!';
                break;
            case 'subscription':
                icon.textContent = '⭐';
                username.textContent = data.username || 'Someone';
                message.textContent = 'subscribed!';
                break;
            case 'donation':
                icon.textContent = '💰';
                username.textContent = data.username || 'Someone';
                message.textContent = `donated $${data.amount || '0'}!`;
                break;
            default:
                icon.textContent = '🎉';
                username.textContent = data.username || 'Event';
                message.textContent = data.message || '';
        }

        container.classList.remove('hidden');

        // Hide after 5 seconds
        setTimeout(() => {
            container.classList.add('hidden');
            setTimeout(processQueue, 600);
        }, 5000);
    }

    // Listen for messages from parent window
    window.addEventListener('message', (e) => {
        if (e.data && e.data.type) {
            showAlert(e.data);
        }
    });
})();
