/**
 * Auth module — handles session state display in the navbar.
 */
(function () {
    async function checkAuth() {
        try {
            const res = await fetch('/auth/me');
            const data = await res.json();
            const el = document.getElementById('user-info');
            if (!el) return;

            if (data.authenticated && data.user) {
                el.innerHTML =
                    '<span style="color:var(--success)">● </span>' +
                    (data.user.display_name || data.user.username) +
                    ' <a href="/auth/logout" style="margin-left:0.5rem;font-size:0.85rem;">Logout</a>';
            } else {
                el.innerHTML = '<a href="/login">Login</a>';
            }
        } catch {
            // Silently ignore auth check failures
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', checkAuth);
    } else {
        checkAuth();
    }
})();
