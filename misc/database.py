import sqlite3

class Database:

    def __init__(self, database_file_path="properties.db"):
        # Define the path to the sqlite3 database file.
        self.database_file_path = database_file_path
        self.connection = self.create_database_connection()
        self.cursor = self.connection.cursor()
        self.set_pragma_foreign_keys_on()

    def create_database_connection(self):
        """
        Method returns a connection to the sqlite datebase file.
        """
        conn = sqlite3.connect(self.database_file_path, check_same_thread=False)
        # Set the row_factory
        conn.row_factory = sqlite3.Row
        # Return the connection
        return conn

    def execute_sql_query(self, query):
        print(f"executing Sql Query")
        try:
            with self.connection:
                # Execute the Query
                return self.connection.execute(query).fetchall()
        except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
            print(str(e))
    
    def set_pragma_foreign_keys_on(self):
        self.cursor.execute("PRAGMA foreign_keys = ON")

    def bulk_insert_new_rm_properties_or_ignore(self, property_items):
        print(f"Inserting '{len(property_items)}' properties.")
        try:
            with self.connection:
                # Insert New Records or Ignore Existing Ones.
                self.connection.executemany(
                    """
                    INSERT OR IGNORE INTO properties (
                    rm_id, rm_description, rm_property_type,
                    rm_bedrooms, rm_bathrooms, rm_commercial,
                    rm_display_address, rm_display_status,
                    rm_latitude, rm_longitude, rm_price,
                    rm_first_visible_date, rm_url
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?);
                    """,
                    property_items
                )
        except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
            print("Could not complete insert operation")
            print(str(e))
            self.connection.rollback()
        else:
            # Commit
            self.connection.commit()

    def bulk_update_rm_properties(self, properties):
        print(f"Updating '{len(properties)}' properties.")
        try:
            with self.connection:
                # Update Existing Records
                for p in properties:
                    self.connection.execute(
                        f"""
                        UPDATE properties SET
                        rm_description = '{p["rm_description"]}', 
                        rm_property_type = '{p["rm_property_type"]}',
                        rm_bedrooms = '{p["rm_bedrooms"]}',
                        rm_bathrooms = '{p["rm_bathrooms"]}',
                        rm_commercial = '{p["rm_commercial"]}',
                        rm_display_address = '{p["rm_display_address"]}',
                        rm_display_status = '{p["rm_display_status"]}',
                        rm_latitude = '{p["rm_latitude"]}',
                        rm_longitude = '{p["rm_longitude"]}',
                        rm_price = {p["rm_price"]},
                        rm_first_visible_date = '{p["rm_first_visible_date"]}',
                        rm_url = '{p["rm_url"]}',
                        WHERE rm_id = {p["rm_id"]};
                        """
                    )
        except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
            print("Could not complete update operation")
            print(str(e))
            self.connection.rollback()
        else:
            # Commit
            self.connection.commit()
    
    def update_sale_history_attempted(self, property):
        print("Updating sale history attempted value")
        try:
            with self.connection:
                # Update Existing Records
                self.connection.execute(
                    f"""
                    UPDATE properties SET
                    rm_sale_history_attempted = 1
                    WHERE id = {property["id"]};
                    """
                )
        except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
            print("Could not complete update operation")
            print(str(e))
            self.connection.rollback()
        else:
            # Commit
            self.connection.commit()
    
    def update_postcode_dpi_epc_values(self, property):
        print("Updating postcode, deliveryPointid and epc values")
        try:
            with self.connection:
                # Update Existing Records
                self.connection.execute(
                    f"""
                    UPDATE properties SET
                    rm_postcode = '{property["postcode"]}',
                    rm_delivery_point_id = {property["rm_delivery_point_id"]},
                    rm_epc_cert_url = '{property["rm_epc_cert_url"]}',
                    rm_epc_cert = '{property["rm_epc_cert"]}'
                    WHERE id = {property["id"]};
                    """
                )
        except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
            print("Could not complete update operation")
            print(str(e))
            self.connection.rollback()
        else:
            # Commit
            self.connection.commit()


    def get_sale_history_data(self):
        print("Getting sale history data")
        pass

    def get_search_urls(self):
        print("Getting search urls.")
        try:
            with self.connection:
                # Select Search Urls.
                return self.cursor.execute(
                    """
                    SELECT * FROM urls;
                    """
                ).fetchall()
        except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
            print("Could not get search urls")
            print(str(e))
            return list()
    
    def get_properties_with_no_sale_history(self):
        print("Getting properties with no real address and no sales history attempted.")
        try:
            with self.connection:
                # Select Search Urls.
                return self.cursor.execute(
                    """
                    SELECT *
                    FROM properties
                    WHERE rm_sale_history_attempted = False
                    AND rm_postcode IS NOT NULL
                    AND id NOT IN (
                        SELECT property_id
                        FROM sale_history
                    );
                    """
                ).fetchall()
        except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
            print("Could not get search urls")
            print(str(e))

    def get_properties_with_no_postcode_values(self):
        print("Getting properties with postcodes with default NULL values")
        try:
            with self.connection:
                # Select Search Urls.
                return self.cursor.execute(
                    """
                    SELECT
                    id,
                    rm_url
                    FROM properties
                    WHERE rm_postcode IS NULL;
                    """
                ).fetchall()
        except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
            print("Could not get search urls")
            print(str(e))


    def insert_sale_history_data(self, sale_history_data, property):
        print("Inserting previous sale date and price data")
        try:
            with self.connection:
                # Iterate through the Sale_History_Data Dictionary.
                for sale_date, sale_price in sale_history_data.items():
                    # Select Search Urls.
                    self.cursor.execute(
                        """
                        INSERT INTO sale_history (
                        sale_price, sale_date, property_id
                        )
                        VALUES (?,?,?)
                        """, (sale_date, sale_price, property["id"])
                    )
        except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
            print("Could not get search urls")
            print(str(e))
    
    # def get_new_users_to_follow(self, count):
    #     return self.csr.execute("""
    #         SELECT * FROM followers
    #         WHERE following = 0
    #         ORDER BY follower_count DESC
    #         LIMIT {}
    #         """.format(count)
    #     ).fetchall()

    # def set_user_followed(self, id):
    #     self.csr.execute("""
    #         UPDATE followers
    #         SET following = {0}
    #         WHERE id = {1}
    #         """.format(1, id),
    #     )
    #     self.db.commit()