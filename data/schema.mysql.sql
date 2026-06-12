CREATE TABLE IF NOT EXISTS fishes (
  id INT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  alias VARCHAR(100),
  species_code VARCHAR(50),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_fishes_species_code ON fishes (species_code);

CREATE TABLE IF NOT EXISTS markets (
  id INT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  region_code VARCHAR(20),
  source_code VARCHAR(50),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_markets_name_region ON markets (name, region_code);

CREATE TABLE IF NOT EXISTS prices (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  fish_id INT NOT NULL,
  market_id INT NOT NULL,
  price DECIMAL(12,4) NOT NULL,
  currency VARCHAR(10) DEFAULT 'CNY',
  unit VARCHAR(20) DEFAULT 'kg',
  ts DATETIME NOT NULL,
  price_type VARCHAR(20) DEFAULT 'pond',
  source_url TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_prices_fish FOREIGN KEY (fish_id) REFERENCES fishes(id),
  CONSTRAINT fk_prices_market FOREIGN KEY (market_id) REFERENCES markets(id),
  UNIQUE KEY uq_prices_natural (fish_id, market_id, ts, price)
);

CREATE INDEX idx_prices_fish_market_ts ON prices (fish_id, market_id, ts);

CREATE TABLE IF NOT EXISTS forecasts (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  fish_id INT NOT NULL,
  market_id INT NOT NULL,
  horizon INT NOT NULL,
  predicted_at DATETIME NOT NULL,
  model VARCHAR(50) NOT NULL,
  price DECIMAL(12,4) NOT NULL,
  lower DECIMAL(12,4),
  upper DECIMAL(12,4),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_forecasts_fish FOREIGN KEY (fish_id) REFERENCES fishes(id),
  CONSTRAINT fk_forecasts_market FOREIGN KEY (market_id) REFERENCES markets(id)
);

CREATE INDEX idx_forecasts_fish_market ON forecasts (fish_id, market_id);
CREATE INDEX idx_forecasts_predicted_at ON forecasts (predicted_at);
