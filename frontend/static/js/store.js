/**
 * Store module — loads and displays products.
 */
(function () {
    let currentFilter = '';

    function init() {
        const grid = document.getElementById('products-grid');
        if (!grid) return;

        loadProducts();

        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilter = btn.dataset.type || '';
                loadProducts();
            });
        });
    }

    async function loadProducts() {
        const grid = document.getElementById('products-grid');
        const url = currentFilter
            ? `/store/api/products?product_type=${encodeURIComponent(currentFilter)}`
            : '/store/api/products';

        try {
            const res = await fetch(url);
            const data = await res.json();

            if (data.products && data.products.length > 0) {
                grid.innerHTML = data.products.map(p => `
                    <div class="product-card">
                        <div class="product-preview">
                            ${p.preview_url
                                ? `<img src="${p.preview_url}" alt="${p.name}">`
                                : '🎨'}
                        </div>
                        <div class="product-info">
                            <h3>${p.name}</h3>
                            <p>${p.description || 'No description'}</p>
                            ${p.tags ? `<div class="product-tags">${p.tags.map(t => `<span class="tag">${t}</span>`).join('')}</div>` : ''}
                            <div class="product-footer">
                                <span class="product-price">${p.price > 0 ? '$' + p.price.toFixed(2) : 'Free'}</span>
                                <button class="btn btn-sm btn-primary" onclick="alert('Purchase coming soon!')">
                                    ${p.price > 0 ? 'Buy' : 'Install'}
                                </button>
                            </div>
                        </div>
                    </div>
                `).join('');
            } else {
                grid.innerHTML = '<p class="loading-text">No products available yet.</p>';
            }
        } catch {
            grid.innerHTML = '<p class="loading-text">Could not load products.</p>';
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
