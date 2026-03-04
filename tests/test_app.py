import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.anyio
async def test_landing_page(client):
    """Landing page returns 200 and contains the brand name."""
    res = await client.get("/")
    assert res.status_code == 200
    assert "OverlayForge" in res.text


@pytest.mark.anyio
async def test_login_page(client):
    """Login page returns 200 and has Twitch/Kick buttons."""
    res = await client.get("/login")
    assert res.status_code == 200
    assert "Twitch" in res.text
    assert "Kick" in res.text


@pytest.mark.anyio
async def test_store_page(client):
    """Store page returns 200."""
    res = await client.get("/store")
    assert res.status_code == 200
    assert "Store" in res.text


@pytest.mark.anyio
async def test_dashboard_page(client):
    """Dashboard page returns 200."""
    res = await client.get("/dashboard")
    assert res.status_code == 200
    assert "Dashboard" in res.text


@pytest.mark.anyio
async def test_editor_page(client):
    """Editor page returns 200 with a dummy overlay ID."""
    res = await client.get("/editor/test-id-123")
    assert res.status_code == 200
    assert "editor" in res.text.lower()


@pytest.mark.anyio
async def test_overlay_live_page(client):
    """Overlay live page returns 200 with a token."""
    res = await client.get("/overlay/some-token")
    assert res.status_code == 200
    assert "overlay-root" in res.text


@pytest.mark.anyio
async def test_auth_me_unauthenticated(client):
    """Auth /me endpoint returns not authenticated when no cookie."""
    res = await client.get("/auth/me")
    assert res.status_code == 200
    data = res.json()
    assert data["authenticated"] is False


@pytest.mark.anyio
async def test_auth_logout(client):
    """Logout redirects to landing page."""
    res = await client.get("/auth/logout", follow_redirects=False)
    assert res.status_code in (302, 307)
    assert res.headers["location"] == "/"


@pytest.mark.anyio
async def test_twitch_login_redirect(client):
    """Twitch login redirects to Twitch OAuth URL."""
    res = await client.get("/auth/twitch", follow_redirects=False)
    assert res.status_code in (302, 307)
    assert "id.twitch.tv" in res.headers["location"]


@pytest.mark.anyio
async def test_kick_login_redirect(client):
    """Kick login redirects to Kick OAuth URL."""
    res = await client.get("/auth/kick", follow_redirects=False)
    assert res.status_code in (302, 307)
    assert "kick.com" in res.headers["location"]


@pytest.mark.anyio
async def test_static_css_served(client):
    """Static CSS files are served correctly."""
    res = await client.get("/static/css/base.css")
    assert res.status_code == 200
    assert "text/css" in res.headers["content-type"]


@pytest.mark.anyio
async def test_static_js_served(client):
    """Static JS files are served correctly."""
    res = await client.get("/static/js/auth.js")
    assert res.status_code == 200


@pytest.mark.anyio
async def test_widget_html_served(client):
    """Widget HTML files are accessible."""
    res = await client.get("/static/widgets/alert-box/widget.html")
    assert res.status_code == 200
    assert "alert-container" in res.text


@pytest.mark.anyio
async def test_overlays_api_unauthenticated(client):
    """Overlays API returns 401 when not authenticated."""
    res = await client.get("/api/overlays/")
    assert res.status_code == 401


@pytest.mark.anyio
async def test_store_api_products(client):
    """Store products API returns empty list without DB."""
    res = await client.get("/store/api/products")
    assert res.status_code == 200
    data = res.json()
    assert "products" in data
