CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS bronze.sales_order_header (
    sales_order_id INTEGER,
    revision_number SMALLINT,
    order_date TIMESTAMP,
    due_date TIMESTAMP,
    ship_date TIMESTAMP,
    status SMALLINT,
    online_order_flag BOOLEAN,
    sales_order_number VARCHAR(50),
    purchase_order_number VARCHAR(50),
    account_number VARCHAR(50),
    customer_id INTEGER,
    salesperson_id INTEGER,
    territory_id INTEGER,
    bill_to_address_id INTEGER,
    ship_to_address_id INTEGER,
    ship_method VARCHAR(50),
    credit_card_approval_code VARCHAR(15),
    currency_rate_id INTEGER,
    subtotal NUMERIC(19,4),
    tax_amt NUMERIC(19,4),
    freight NUMERIC(19,4),
    total_due NUMERIC(19,4),
    comment TEXT,
    _source_system VARCHAR(100),
    _source_table VARCHAR(100),
    _load_date TIMESTAMPTZ DEFAULT NOW(),
    _record_hash VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS bronze.sales_order_detail (
    sales_order_id INTEGER,
    sales_order_detail_id INTEGER,
    order_qty SMALLINT,
    product_id INTEGER,
    special_offer_id INTEGER,
    unit_price NUMERIC(19,4),
    unit_price_discount NUMERIC(19,4),
    line_total NUMERIC(19,4),
    rowguid VARCHAR(64),
    modified_date TIMESTAMP,
    _source_system VARCHAR(100),
    _source_table VARCHAR(100),
    _load_date TIMESTAMPTZ DEFAULT NOW(),
    _record_hash VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS bronze.customer (
    customer_id INTEGER,
    person_id INTEGER,
    store_id INTEGER,
    territory_id INTEGER,
    account_number VARCHAR(50),
    rowguid VARCHAR(64),
    modified_date TIMESTAMP,
    _source_system VARCHAR(100),
    _source_table VARCHAR(100),
    _load_date TIMESTAMPTZ DEFAULT NOW(),
    _record_hash VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS bronze.product (
    product_id INTEGER,
    name VARCHAR(255),
    product_number VARCHAR(50),
    make_flag BOOLEAN,
    finished_goods_flag BOOLEAN,
    color VARCHAR(30),
    safety_stock_level SMALLINT,
    reorder_point SMALLINT,
    standard_cost NUMERIC(19,4),
    list_price NUMERIC(19,4),
    size VARCHAR(10),
    size_unit_measure_code VARCHAR(3),
    weight_unit_measure_code VARCHAR(3),
    weight NUMERIC(8,2),
    days_to_manufacture INTEGER,
    product_line VARCHAR(2),
    class VARCHAR(2),
    style VARCHAR(2),
    product_subcategory_id INTEGER,
    product_model_id INTEGER,
    sell_start_date TIMESTAMP,
    sell_end_date TIMESTAMP,
    discontinued_date TIMESTAMP,
    rowguid VARCHAR(64),
    modified_date TIMESTAMP,
    _source_system VARCHAR(100),
    _source_table VARCHAR(100),
    _load_date TIMESTAMPTZ DEFAULT NOW(),
    _record_hash VARCHAR(64)
);
