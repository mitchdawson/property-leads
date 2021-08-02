DROP TABLE IF EXISTS urls;
DROP TABLE IF EXISTS properties;



-- CREATE TABLE urls (
--     id SERIAL PRIMARY KEY,
--     rm_url VARCHAR(255) NOT NULL UNIQUE,
--     rm_url_description VARCHAR(255) DEFAULT NULL,
--     url_enabled BOOLEAN NOT NULL DEFAULT TRUE
-- );
locationIdentifier=REGION%5E307&maxPrice=200000&minPrice=150000&radius=10.0&propertyTypes=semi-detached&primaryDisplayPropertyType=semidetachedhouses&includeSSTC=true&dontShow=sharedOwnership%2Cretirement%2CnewHome&furnishTypes=&keywords=

CREATE TABLE urls (
    id uuid DEFAULT uuid_generate_v4 (),
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "locationIdentifier" VARCHAR(255) DEFAULT NULL,
    "maxPrice" INTEGER DEFAULT NULL,
    "minPrice" INTEGER DEFAULT NULL,
    "radius" REAL DEFAULT 10.0,
    "propertyTypes" VARCHAR(255) DEFAULT NULL,
    "primaryDisplayPropertyType" VARCHAR(255) DEFAULT NULL,
    "includeSSTC" BOOLEAN NOT NULL DEFAULT TRUE,
    "dontShow" VARCHAR(255) DEFAULT NULL,
    "furnishTypes" VARCHAR(255) DEFAULT NULL,
    "keywords" VARCHAR(255) DEFAULT NULL,
    "description" VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (id)
);

-- CREATE TABLE urls (
--     id uuid DEFAULT uuid_generate_v4 (),
--     locationIdentifier VARCHAR(255) DEFAULT NULL,
--     maxPrice INTEGER DEFAULT NULL,
--     minPrice INTEGER DEFAULT NULL,
--     radius REAL DEFAULT 10.0,
--     propertyTypes VARCHAR(255) DEFAULT NULL,
--     primaryDisplayPropertyType VARCHAR(255) DEFAULT NULL,
--     includeSSTC BOOLEAN NOT NULL DEFAULT TRUE,
--     dontShow VARCHAR(255) DEFAULT NULL,
--     furnishTypes VARCHAR(255) DEFAULT NULL,
--     keywords VARCHAR(255) DEFAULT NULL,
--     description VARCHAR(255) DEFAULT NULL,
--     PRIMARY KEY (id)
-- );

CREATE INDEX IF NOT EXISTS url_idx ON urls (id);

CREATE TABLE IF NOT EXISTS properties (
    id uuid DEFAULT uuid_generate_v4 (),
    -- id SERIAL PRIMARY KEY,
    rm_property_id INTEGER UNIQUE,
    rm_description VARCHAR(255) DEFAULT NULL,
    rm_property_type VARCHAR(255) DEFAULT NULL,
    rm_bedrooms INTEGER DEFAULT NULL,
    rm_bathrooms INTEGER DEFAULT NULL,
    rm_commercial VARCHAR(255) DEFAULT NULL,
    rm_display_address VARCHAR(255) DEFAULT NULL,
    rm_display_status VARCHAR(255) DEFAULT NULL,
    rm_removed_timestamp TIMESTAMP DEFAULT NULL,
    rm_real_address VARCHAR(255) DEFAULT NULL,
    rm_latitude REAL DEFAULT NULL,
    rm_longitude REAL DEFAULT NULL,
    rm_listing_price INTEGER DEFAULT NULL,
    rm_first_visible_date VARCHAR(255) DEFAULT NULL,
    rm_property_url VARCHAR(255) DEFAULT NULL,
    rm_postcode VARCHAR(20) DEFAULT NULL,
    rm_delivery_point_id VARCHAR(20) DEFAULT NULL,
    rm_epc_cert BOOLEAN NOT NULL DEFAULT FALSE,
    rm_epc_cert_url VARCHAR(255) DEFAULT NULL,
    rm_epc_cert_address VARCHAR(255) DEFAULT NULL,
    rm_sale_history_attempted BOOLEAN NOT NULL DEFAULT FALSE,
    rm_sold_stc BOOLEAN NOT NULL DEFAULT FALSE,
    rm_sold_stc_timestamp TIMESTAMP DEFAULT NULL,
    rm_sold BOOLEAN NOT NULL DEFAULT FALSE,
    rm_sold_timestamp TIMESTAMP DEFAULT NULL,
    rm_sold_price INTEGER DEFAULT NULL,
    rm_sold_nearby_url VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX properties_idx ON properties (id, rm_property_id);


-- Create the sale_history table

CREATE TABLE sale_history (
    id uuid DEFAULT uuid_generate_v4 (),
    -- id DEFAULT uuid_generate_v4 (),
    sale_date VARCHAR(50) NOT NULL,
    sale_price VARCHAR(50) NOT NULL,
    property_id uuid REFERENCES properties,
    PRIMARY KEY (id)
);

CREATE INDEX sale_history_idx ON sale_history (id);

-- Create User
CREATE ROLE leadsapp WITH
  LOGIN
  NOSUPERUSER
  INHERIT
  NOCREATEDB
  NOCREATEROLE
  NOREPLICATION
  ENCRYPTED PASSWORD 'md5ba30ae682a6c88c58e9f92edade1a183';

-- Grant Priveleges
GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE public.properties TO leadsapp;
GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE public.sale_history TO leadsapp;
GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE public.urls TO leadsapp;



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