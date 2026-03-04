/**
 * Overlay Editor — drag & drop + resize widgets on a canvas.
 */
(function () {
    let widgets = [];
    let selectedWidget = null;
    let isDragging = false;
    let isResizing = false;
    let dragOffset = { x: 0, y: 0 };

    function init() {
        const canvas = document.getElementById('editor-canvas');
        const nameInput = document.getElementById('overlay-name');
        const saveBtn = document.getElementById('save-btn');
        const previewBtn = document.getElementById('preview-btn');
        const addSelect = document.getElementById('add-widget-select');

        if (!canvas) return;

        // Load overlay data
        loadOverlay();

        // Add widget
        addSelect.addEventListener('change', () => {
            const type = addSelect.value;
            if (!type) return;
            addWidget(type);
            addSelect.value = '';
        });

        // Save
        saveBtn.addEventListener('click', saveOverlay);

        // Preview URL
        previewBtn.addEventListener('click', async () => {
            try {
                const res = await fetch(`/api/overlays/${overlayId}`);
                const data = await res.json();
                if (data.public_url_token) {
                    const url = `${window.location.origin}/overlay/${data.public_url_token}`;
                    await navigator.clipboard.writeText(url);
                    alert('OBS URL copied: ' + url);
                }
            } catch {
                alert('Could not get preview URL.');
            }
        });

        // Canvas mouse events for drag & drop
        canvas.addEventListener('mousedown', onMouseDown);
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    }

    async function loadOverlay() {
        if (typeof overlayId === 'undefined') return;
        try {
            const res = await fetch(`/api/overlays/${overlayId}`);
            const data = await res.json();
            const nameInput = document.getElementById('overlay-name');
            if (nameInput) nameInput.value = data.name || '';

            if (data.widgets_config && Array.isArray(data.widgets_config)) {
                data.widgets_config.forEach(w => addWidgetToCanvas(w));
            }
        } catch {
            console.log('No existing overlay data found.');
        }
    }

    function addWidget(type) {
        const w = {
            id: 'w-' + Date.now(),
            widget_type: type,
            name: type.replace('-', ' '),
            position_x: 50,
            position_y: 50,
            width: 300,
            height: 200,
            z_index: widgets.length + 1,
        };
        widgets.push(w);
        addWidgetToCanvas(w);
    }

    function addWidgetToCanvas(w) {
        if (!widgets.find(x => x.id === w.id)) widgets.push(w);

        const canvas = document.getElementById('editor-canvas');
        const el = document.createElement('div');
        el.className = 'editor-widget';
        el.dataset.id = w.id;
        el.style.left = (w.position_x || 0) + 'px';
        el.style.top = (w.position_y || 0) + 'px';
        el.style.width = (w.width || 300) + 'px';
        el.style.height = (w.height || 200) + 'px';
        el.style.zIndex = w.z_index || 1;

        el.innerHTML = `
            <span class="widget-label">${w.widget_type || w.name}</span>
            <div class="resize-handle"></div>
            <button class="delete-widget" title="Remove">×</button>
        `;

        // Delete handler
        el.querySelector('.delete-widget').addEventListener('click', (e) => {
            e.stopPropagation();
            widgets = widgets.filter(x => x.id !== w.id);
            el.remove();
        });

        canvas.appendChild(el);
    }

    function onMouseDown(e) {
        const widgetEl = e.target.closest('.editor-widget');
        if (!widgetEl) {
            deselectAll();
            return;
        }

        // Check if clicking resize handle
        if (e.target.classList.contains('resize-handle')) {
            isResizing = true;
            selectedWidget = widgetEl;
            widgetEl.classList.add('selected');
            return;
        }

        // Start dragging
        isDragging = true;
        selectedWidget = widgetEl;
        deselectAll();
        widgetEl.classList.add('selected');

        const rect = widgetEl.getBoundingClientRect();
        dragOffset.x = e.clientX - rect.left;
        dragOffset.y = e.clientY - rect.top;
    }

    function onMouseMove(e) {
        if (!selectedWidget) return;
        const canvas = document.getElementById('editor-canvas');
        const canvasRect = canvas.getBoundingClientRect();

        if (isDragging) {
            const x = e.clientX - canvasRect.left - dragOffset.x;
            const y = e.clientY - canvasRect.top - dragOffset.y;
            selectedWidget.style.left = Math.max(0, x) + 'px';
            selectedWidget.style.top = Math.max(0, y) + 'px';
            updateWidgetData(selectedWidget);
        }

        if (isResizing) {
            const wRect = selectedWidget.getBoundingClientRect();
            const w = e.clientX - wRect.left;
            const h = e.clientY - wRect.top;
            selectedWidget.style.width = Math.max(50, w) + 'px';
            selectedWidget.style.height = Math.max(50, h) + 'px';
            updateWidgetData(selectedWidget);
        }
    }

    function onMouseUp() {
        isDragging = false;
        isResizing = false;
    }

    function deselectAll() {
        document.querySelectorAll('.editor-widget').forEach(el => el.classList.remove('selected'));
    }

    function updateWidgetData(el) {
        const id = el.dataset.id;
        const w = widgets.find(x => x.id === id);
        if (w) {
            w.position_x = parseInt(el.style.left) || 0;
            w.position_y = parseInt(el.style.top) || 0;
            w.width = parseInt(el.style.width) || 300;
            w.height = parseInt(el.style.height) || 200;
        }
    }

    async function saveOverlay() {
        if (typeof overlayId === 'undefined') return;
        const nameInput = document.getElementById('overlay-name');
        try {
            await fetch(`/api/overlays/${overlayId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: nameInput ? nameInput.value : 'Untitled',
                    widgets_config: widgets,
                }),
            });
            alert('Overlay saved!');
        } catch {
            alert('Failed to save overlay.');
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
