import asyncpg
from backend.config import settings

pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    """Return the connection pool, creating it if necessary."""
    global pool
    if pool is None and settings.DATABASE_URL:
        pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL, min_size=1, max_size=5)
    return pool


async def close_pool() -> None:
    """Close the connection pool."""
    global pool
    if pool is not None:
        await pool.close()
        pool = None


DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twitch_id VARCHAR(50) UNIQUE,
    kick_id VARCHAR(50) UNIQUE,
    username VARCHAR(100) NOT NULL,
    display_name VARCHAR(100),
    avatar_url TEXT,
    email VARCHAR(255),
    plan VARCHAR(20) DEFAULT 'free',
    twitch_access_token TEXT,
    twitch_refresh_token TEXT,
    kick_access_token TEXT,
    kick_refresh_token TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS overlays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    resolution_w INTEGER DEFAULT 1920,
    resolution_h INTEGER DEFAULT 1080,
    widgets_config JSONB NOT NULL DEFAULT '[]',
    is_active BOOLEAN DEFAULT false,
    public_url_token VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_widgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    overlay_id UUID REFERENCES overlays(id) ON DELETE CASCADE,
    widget_type VARCHAR(100) NOT NULL,
    name VARCHAR(200),
    config JSONB NOT NULL DEFAULT '{}',
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    width INTEGER DEFAULT 300,
    height INTEGER DEFAULT 200,
    z_index INTEGER DEFAULT 1,
    is_visible BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    seller_id UUID REFERENCES users(id),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'USD',
    product_type VARCHAR(50) NOT NULL,
    preview_url TEXT,
    download_files JSONB,
    tags TEXT[],
    is_published BOOLEAN DEFAULT false,
    downloads_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS purchases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    product_id UUID REFERENCES products(id),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method VARCHAR(20),
    payment_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stream_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    platform VARCHAR(20) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);
"""
