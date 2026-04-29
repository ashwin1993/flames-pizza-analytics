-- FLAMES PIZZA — daily_revenue table
-- Source: POS Google Sheet (Rajani Revenue Sheet)
-- Contains: Daily platform revenue summaries 2018 - 2026

CREATE TABLE daily_revenue (
    revenue_id          SERIAL PRIMARY KEY,
    order_date          DATE NOT NULL,
    order_time          TIME,
    day_of_week         VARCHAR(10),
    hour_of_day         INT,
    order_month         VARCHAR(20),
    order_year          INT,
    platform            VARCHAR(50) NOT NULL,
    platform_raw        VARCHAR(50),
    my_amount           DECIMAL(10,2) DEFAULT 0,
    total_discount      DECIMAL(10,2) DEFAULT 0,
    packaging_charge    DECIMAL(10,2) DEFAULT 0,
    net_amount          DECIMAL(10,2),
    gst                 DECIMAL(10,2) DEFAULT 0,
    gross_amount        DECIMAL(10,2),
    covid_period        BOOLEAN DEFAULT FALSE,
    data_type           VARCHAR(20) DEFAULT 'summary',
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_daily_rev_date     ON daily_revenue(order_date);
CREATE INDEX idx_daily_rev_platform ON daily_revenue(platform);
CREATE INDEX idx_daily_rev_year     ON daily_revenue(order_year);
CREATE INDEX idx_daily_rev_covid    ON daily_revenue(covid_period);
