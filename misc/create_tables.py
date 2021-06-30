import sqlite3

conn = sqlite3.connect("main.db")
# Set the row_factory
conn.row_factory = sqlite3.Row
# Return the connection
cur = conn.cursor()

def create_table_urls():
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS urls (
            pkid INTEGER PRIMARY KEY,
            url VARCHAR(255) NOT NULL UNIQUE,
            description VARCHAR(255) NOT NULL
        );
        """
    )

def create_table_properties():
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY,
            rm_id INTEGER NOT NULL UNIQUE,
            rm_property_type VARCHAR(255) DEFAULT NULL,
            rm_bedrooms INTEGER DEFAULT NULL,
            rm_bathrooms INTEGER DEFAULT NULL,
            rm_commercial VARCHAR(255) DEFAULT NULL,
            rm_display_address VARCHAR(255) DEFAULT NULL,
            rm_display_status VARCHAR(255) DEFAULT NULL,
            rm_latitude FLOAT DEFAULT NULL,
            rm_longitude FLOAT DEFAULT NULL,
            rm_price INTEGER DEFAULT NULL,
            rm_first_visible_date VARCHAR(255) DEFAULT NULL,
            rm_postcode VARCHAR(20) DEFAULT NULL,
            rm_delivery_point_id VARCHAR(20) DEFAULT NULL,
            rm_epc_cert BOOLEAN DEFAULT 0,
            rm_epc_cert_url VARCHAR(255) DEFAULT NULL,
            rm_epc_cert_address VARCHAR(255) DEFAULT NULL,


        );
        """
    )

def drop_table_urls():
    cur.execute(
        """
        DROP TABLE IF EXISTS urls;
        """
    )

def drop_table_properties():
    cur.execute(
        """
        DROP TABLE IF EXISTS properties;
        """
    )

def main():

    drop = False

    if drop:
        drop_table_urls()
        drop_table_properties()
    
    create_table_urls()
    create_table_properties()



if __name__ == "__main__":
    main()
