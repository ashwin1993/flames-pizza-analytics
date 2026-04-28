-- FLAMES PIZZA — orders table
-- Source: POS Order Listing (Petpooja)

CREATE TABLE orders (
    order_id            SERIAL PRIMARY KEY,
    pos_order_no        VARCHAR(20),
    client_order_id     VARCHAR(50),
    order_date          DATE NOT NULL,
    order_time          TIME,
    order_year          INT,
    order_month         INT,
    order_quarter       INT,
    day_of_week         VARCHAR(10),
    hour_of_day         INT,
    platform            VARCHAR(30),
    order_type          VARCHAR(20),
    table_size          INT,
    item_subtotal       DECIMAL(10,2),
    discount            DECIMAL(10,2) DEFAULT 0,
    container_charge    DECIMAL(10,2) DEFAULT 0,
    delivery_charge     DECIMAL(10,2) DEFAULT 0,
    tax                 DECIMAL(10,2),
    round_off           DECIMAL(5,2) DEFAULT 0,
    grand_total         DECIMAL(10,2),
    payment_type        VARCHAR(30),
    payment_description VARCHAR(100),
    order_status        VARCHAR(20) DEFAULT 'completed',
    sequence_name       VARCHAR(50),
    covid_period        BOOLEAN DEFAULT FALSE,
    is_platform_order   BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMP DEFAULT NOW(),
    data_source         VARCHAR(50) DEFAULT 'POS'
);
