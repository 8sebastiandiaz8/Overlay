/**
 * Payments module — Stripe and PayPal integration.
 */

async function purchaseWithStripe(productId) {
    try {
        const res = await fetch('/payments/stripe/create-checkout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId }),
        });
        const data = await res.json();
        if (data.checkout_url) {
            window.location.href = data.checkout_url;
        } else {
            alert('Could not create checkout session.');
        }
    } catch {
        alert('Payment error. Please try again.');
    }
}

function initPayPalButton(productId, containerId) {
    if (typeof paypal === 'undefined') {
        console.warn('PayPal SDK not loaded');
        return;
    }

    paypal.Buttons({
        createOrder: async () => {
            const res = await fetch('/payments/paypal/create-order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ product_id: productId }),
            });
            const data = await res.json();
            return data.order_id;
        },
        onApprove: async (data) => {
            await fetch('/payments/paypal/capture-order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ order_id: data.orderID }),
            });
            window.location.href = '/store?purchase=success';
        },
        onError: () => {
            alert('PayPal payment failed. Please try again.');
        },
    }).render(containerId);
}
