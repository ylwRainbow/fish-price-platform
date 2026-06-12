-- 数据库：PostgreSQL 语法（MySQL 请按需调整类型/索引）

CREATE TABLE IF NOT EXISTS fishes (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  alias VARCHAR(100),
  species_code VARCHAR(50),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_fishes_species_code ON fishes (species_code);

CREATE TABLE IF NOT EXISTS markets (
  id SERIAL PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  region_code VARCHAR(20),
  source_code VARCHAR(50),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_markets_name_region ON markets (name, region_code);

CREATE TABLE IF NOT EXISTS prices (
  id BIGSERIAL PRIMARY KEY,
  fish_id INTEGER NOT NULL REFERENCES fishes(id),
  market_id INTEGER NOT NULL REFERENCES markets(id),
  price NUMERIC(12,4) NOT NULL,
  currency VARCHAR(10) DEFAULT 'CNY',
  unit VARCHAR(20) DEFAULT 'kg',
  ts TIMESTAMP NOT NULL,
  price_type VARCHAR(20) DEFAULT 'pond',
  source_url TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_prices_fish_market_ts ON prices (fish_id, market_id, ts);
CREATE UNIQUE INDEX IF NOT EXISTS uq_prices_natural ON prices (fish_id, market_id, ts, price);

CREATE TABLE IF NOT EXISTS forecasts (
  id BIGSERIAL PRIMARY KEY,
  fish_id INTEGER NOT NULL REFERENCES fishes(id),
  market_id INTEGER NOT NULL REFERENCES markets(id),
  horizon INTEGER NOT NULL,
  predicted_at TIMESTAMP NOT NULL,
  model VARCHAR(50) NOT NULL,
  price NUMERIC(12,4) NOT NULL,
  lower NUMERIC(12,4),
  upper NUMERIC(12,4),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_forecasts_fish_market ON forecasts (fish_id, market_id);
CREATE INDEX IF NOT EXISTS idx_forecasts_predicted_at ON forecasts (predicted_at);
