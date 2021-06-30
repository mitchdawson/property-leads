DROP TABLE IF EXISTS urls;
DROP TABLE IF EXISTS properties;



CREATE TABLE urls (
    id INTEGER PRIMARY KEY,
    rm_url VARCHAR(255) NOT NULL UNIQUE,
    rm_url_description VARCHAR(255) NOT NULL,
);

CREATE INDEX IF NOT EXISTS url_idx ON urls (id);

CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY,
    rm_property_id INTEGER NOT NULL UNIQUE,
    rm_property_type VARCHAR(255) DEFAULT NULL,
    rm_bedrooms INTEGER DEFAULT NULL,
    rm_bathrooms INTEGER DEFAULT NULL,
    rm_commercial VARCHAR(255) DEFAULT NULL,
    rm_display_address VARCHAR(255) DEFAULT NULL,
    rm_display_status VARCHAR(255) DEFAULT NULL,
    rm_real_address VARCHAR(255) DEFAULT NULL,
    rm_latitude FLOAT DEFAULT NULL,
    rm_longitude FLOAT DEFAULT NULL,
    rm_price INTEGER DEFAULT NULL,
    rm_first_visible_date VARCHAR(255) DEFAULT NULL,
    rm_url VARCHAR(255) DEFAULT NULL,
    rm_postcode VARCHAR(20) DEFAULT NULL,
    rm_delivery_point_id VARCHAR(20) DEFAULT NULL,
    rm_epc_cert BOOLEAN DEFAULT 0,
    rm_epc_cert_url VARCHAR(255) DEFAULT NULL,
    rm_epc_cert_address VARCHAR(255) DEFAULT NULL,
    rm_sale_history_attempted BOOLEAN DEFAULT 0,
);

CREATE UNIQUE INDEX IF NOT EXISTS property_idx ON properties (id);
CREATE UNIQUE INDEX IF NOT EXISTS rm_property_idx ON properties (rm_property_id);

CREATE TABLE sale_history (
    id INTEGER PRIMARY KEY,
    sale_date VARCHAR(50) NOT NULL,
    sale_price VARCHAR(50) NOT NULL,
    property_id INTEGER NOT NULL,
    FOREIGN KEY(property_id) REFERENCES properties(id) ON DELETE CASCADE,
);

CREATE UNIQUE INDEX IF NOT EXISTS sale_history_idx ON sale_history (id);

-- CREATE TABLE lists (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     title TEXT NOT NULL
-- );

-- CREATE TABLE properties (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     list_id INTEGER NOT NULL,
--     created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     content TEXT NOT NULL,
--     FOREIGN KEY (list_id) REFERENCES lists (id)
-- );