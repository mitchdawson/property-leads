import psycopg2
from psycopg2.extras import execute_values
from psycopg2.pool import ThreadedConnectionPool
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

class Database:

    def __init__(self, db_name, db_user, db_password, db_host, db_port):
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port

        # Create the database connection.
        # conn = self.create_db_connection()

        # Create a threaded connection pool.
        self.pool = self.create_threaded_connection_pool()

    def create_threaded_connection_pool(self):
        return ThreadedConnectionPool(
            5,
            10,
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            cursor_factory=psycopg2.extras.DictCursor
        )
    
    # def create_db_connection(self):
    #     return psycopg2.connect(
    #         dbname=self.db_name,
    #         user=self.db_user,
    #         password=self.db_password,
    #         host=self.db_host,
    #         port=self.db_port,
    #         cursor_factory=psycopg2.extras.DictCursor
    #     )

    def get_properties_with_epc_url_and_no_real_address(self):
        """
        This query returns propeties that have an epc url but no real address
        and when a sale history attempt has been made but no sales history was found.
        """
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT
                    id, rm_epc_cert_url
                    FROM properties
                    WHERE rm_real_address IS NULL
                    AND rm_sale_history_attempted = true
                    AND rm_epc_cert_url IS NOT NULL
                    AND rm_epc_cert_address IS NULL
                    AND rm_epc_cert_address_attempted is false
                    AND id NOT IN (
                    SELECT property_id
                    FROM sale_history
                    )
                    ORDER BY created ASC 
                    LIMIT 100;
                    """
                )
                results = cur.fetchall()
            except Exception as e:
                logger.exception(str(e))
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                return
            else:
                logger.info(f"returning {len(results)} property id and display status objects")
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                return [dict(r) for r in results]
    
    def get_property_search_url_params(self):
        """
        Extracts urls from the datebase that have not been accessed in
        longer than 48 hours, limit to 50 results.
        """
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT
                    id,
                    "locationIdentifier",
                    "maxPrice",
                    "minPrice",
                    "radius",
                    "propertyTypes",
                    "primaryDisplayPropertyType",
                    "includeSSTC",
                    "dontShow"
                    FROM urls
                    WHERE accessed::timestamp < (now() - INTERVAL '48 hours')
                    ORDER BY accessed ASC
                    LIMIT 50;
                    """
                )
                results = cur.fetchall()
            except Exception as e:
                logger.exception(str(e))
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                return
            else:
                logger.info(f"returning {len(results)}")
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                return [dict(r) for r in results]
    
    def get_id_rm_property_id_display_status(self):
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT
                    id, rm_property_id, rm_display_status
                    FROM properties;
                    """
                )
                results = cur.fetchall()
            except Exception as e:
                logger.exception(str(e))
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                return
            else:
                logger.info(f"returning {len(results)} property id and display status objects")
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                return [dict(r) for r in results]

    # def get_properties_sold_stc_no_postcode_and_no_sold_nearby_url(self):
    #     with self.pool.getconn() as conn:
    #         try:
    #             cur.execute(
    #             """
    #             SELECT
    #             id, rm_property_url, rm_sold_stc, 
    #             rm_postcode, rm_sold_nearby_url
    #             FROM properties
    #             WHERE rm_sold_stc = true AND
    #             rm_postcode IS NULL OR
    #             rm_sold_stc = true AND
    #             rm_sold_nearby_url IS NULL;
    #             """
    #             )
    #             results = conn.cur.fetchall()
    #         except Exception as e:
    #             logger.exception(str(e))
    #             return
    #         else:
    #             logger.info(f"returning {len(results)} properties sold stc no postcode and no sold nearby url")
    #             return [dict(r) for r in results]
    
    def get_properties_with_no_postcode(self):
        """
        Get properties with no postcode value, limit to 100 results.
        """
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                """
                SELECT
                id, rm_property_url, 
                rm_postcode, rm_sold_nearby_url
                FROM properties
                WHERE rm_postcode IS NULL
                ORDER BY created ASC LIMIT 200;
                """
                )
                results = cur.fetchall()
            except Exception as e:
                logger.exception(str(e))
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                return
            else:
                logger.info(f"returning {len(results)} properties sold stc no postcode and no sold nearby url")
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                return [dict(r) for r in results]
    
    def get_properties_with_no_sale_history(self):
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                """
                SELECT *
                FROM properties
                WHERE rm_sale_history_attempted = false
                AND rm_postcode IS NOT NULL
                AND id NOT IN (
                    SELECT property_id
                    FROM sale_history
                )
                ORDER BY created ASC LIMIT 200;
                """
                )
                results = cur.fetchall()
            except Exception as e:
                logger.exception(str(e))
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                return
            else:
                logger.info(f"retrieved {len(results)} properties with no previous sale history attempt")
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                # Return the results.
                return [dict(r) for r in results]
    
    def get_properties_with_no_real_address_and_sale_history_attempted(self):
        """
        This method extracts properties where the real address has not been found,
        where a sales history attempt = True, and where there is at least one valid entries in the
        sales history table from this property id
        """
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                """
                SELECT id, rm_property_id, rm_postcode, rm_sold_nearby_url
                FROM properties
                WHERE rm_sale_history_attempted = true
                AND rm_sold_nearby_url IS NOT NULL
                AND rm_real_address IS NULL
                AND rm_real_address_attempted = false
                AND id IN (
                    SELECT property_id
                    FROM sale_history
                )
                ORDER BY created ASC LIMIT 200;
                """
                )
                results = cur.fetchall()
            except Exception as e:
                logger.exception(str(e))
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                return
            else:
                logger.info(f"retrieved {len(results)} properties with no real address but has a postcode and a sales history attempted")
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                # Return the results.
                return [dict(r) for r in results]

    def get_sale_history_for_property_id(self, property_id):
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                cur.execute(
                """
                SELECT sale_date, sale_price
                FROM sale_history
                WHERE property_id = %s
                ORDER BY sale_date DESC;
                """, [property_id]
                )
                results = cur.fetchall()
            except Exception as e:
                logger.exception(str(e))
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                return
            else:
                logger.info(f"retrived '{cur.rowcount}' sale histories for propert id '{property_id}'")
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                # Return the results.
                return [dict(r) for r in results]
    
    def delete_property_for_property_id(self, property_id):
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                # Build the SQL Statement.
                sql = """
                DELETE FROM properties
                WHERE id = uuid(%s);
                """
                # Use the psycopg2 execute_values function.
                cur.execute(sql, property_id)
            except Exception as e:
                logger.exception(str(e))
                conn.rollback()
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                # Return the results.
                return
            else:
                conn.commit()
                logger.info(f"Deleted property with id '{property_id}'")
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                return

    def delete_property_for_rm_property_id(self, rm_property_id):
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                # Build the SQL Statement.
                sql = """
                DELETE FROM properties
                WHERE rm_property_id = %s;
                """
                # Use the psycopg2 execute_values function.
                cur.execute(sql, rm_property_id)
            except Exception as e:
                logger.exception(str(e))
                conn.rollback()
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
            else:
                conn.commit()
                logger.info(f"Deleted property with id '{rm_property_id}'")
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                return

    def delete_from_urls(self):
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                # Build the SQL Statement.
                sql = """
                DELETE FROM urls;
                """
                # Use the psycopg2 execute_values function.
                cur.execute(sql)
            except Exception as e:
                logger.exception(str(e))
                conn.rollback()
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
            else:
                conn.commit()
                results = cur.rowcount
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                # Return the result count.
                return results
    
    
    def insert_urls(self, table, cols, values):
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                query  = "INSERT INTO %s(%s) VALUES %%s;" % (table, cols)
                print(query)
                execute_values(cur, query, values)
            except Exception as e:
                logger.exception(str(e))
                conn.rollback()
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                # Return.
                return
            else:
                conn.commit()
                count = cur.rowcount
                logger.info(f"urls inserted inserted = {cur.rowcount}")
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                # Return the result count.
                return count

    def insert_sale_history_data(self, sale_history_data_list):
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                # Build the SQL Statement.
                sql = """
                INSERT INTO sale_history (
                sale_date, sale_price, property_id
                ) VALUES %s;
                """
                # Use the psycopg2 execute_values function.
                execute_values(cur, sql, sale_history_data_list)
            except Exception as e:
                logger.exception(str(e))
                conn.rollback()
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                # Return
                return
            else:
                conn.commit()
                count = cur.rowcount
                logger.info(f"sale historys inserted = {count}")
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                # Return the result count.
                return count

    def insert_new_properties(self, new_property_values_list):
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                # Build the SQL Statement.
                sql = """
                INSERT INTO properties (
                rm_property_id, rm_description, rm_property_type,
                rm_bedrooms, rm_bathrooms, rm_commercial,
                rm_display_address, rm_display_status,
                rm_latitude, rm_longitude, rm_listing_price,
                rm_first_visible_date, rm_property_url
                ) VALUES %s;
                """
                # Use the psycopg2 execute_values function.
                execute_values(cur, sql, new_property_values_list)
            except Exception as e:
                logger.exception(str(e))
                conn.rollback()
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                # Return.
                return
            else:
                conn.commit()
                count = cur.rowcount
                logger.info(f"new properties inserted = {count}")
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                # Return the result count.
                return count
    
    def update_epc_cert_address(self, address_and_property_id_list):
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                sql = """
                UPDATE properties p
                SET rm_epc_cert_address = data.rm_epc_cert_address,
                rm_epc_cert_address_attempted = true
                FROM (VALUES %s) AS data (
                    rm_epc_cert_address,
                    id
                )
                WHERE p.id = uuid(data.id);
                """
                # Use the psycopg2 execute_values function.
                execute_values(cur, sql, address_and_property_id_list)
            except (Exception, psycopg2.Error) as e:
                logger.exception(str(e))
                conn.rollback()
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                # Return
                return None
            else:
                conn.commit()
                count = cur.rowcount
                logger.info(f"properties epc cert address updated = {cur.rowcount}")
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                # Return the result count.
                return count    
    
    def update_epc_cert_address_attempted(self, id_and_update_epc_cert_address_attempted_values):
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                sql = """
                UPDATE properties p
                SET rm_epc_cert_address_attempted = data.rm_epc_cert_address_attempted 
                FROM (VALUES %s) AS data (
                    rm_epc_cert_address_attempted,
                    id
                )
                WHERE p.id = uuid(data.id);
                """
                # Use the psycopg2 execute_values function.
                execute_values(cur, sql, id_and_update_epc_cert_address_attempted_values)
            except (Exception, psycopg2.Error) as e:
                logger.exception(str(e))
                conn.rollback()
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                # Return
                return None
            else:
                conn.commit()
                count = cur.rowcount
                logger.info(f"properties epc cert address attempted = {cur.rowcount}")
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                # Return the result count.
                return count

    
    def update_url_accessed(self, accessed_url_ids):
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                sql = """
                UPDATE urls u
                SET accessed = to_timestamp(data.timestamp, 'YYYY-MM-DD HH24:MI:SS')::timestamp without time zone
                FROM (VALUES %s) AS data (id, timestamp)
                WHERE u.id = uuid(data.id);
                """
                # Use the psycopg2 execute_values function.
                execute_values(cur, sql, accessed_url_ids)

            except (Exception, psycopg2.Error) as e:
                logger.exception(str(e))
                conn.rollback()
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                # Return
                return
            else:
                conn.commit()
                count = cur.rowcount
                logger.info(f"urls accessed updated = {count}")
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                # Return the result count.
                return count


    def update_property_sold_stc(self, sold_stc_values_list):
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                sql = """
                UPDATE properties p
                SET rm_display_status = data.rm_display_status, 
                rm_sold_stc = data.rm_sold_stc, 
                rm_sold_stc_timestamp = CURRENT_TIMESTAMP
                FROM (VALUES %s) AS data (
                    rm_display_status, rm_sold_stc, 
                    rm_property_id
                )
                WHERE p.rm_property_id = data.rm_property_id;
                """
                # Use the psycopg2 execute_values function.
                execute_values(cur, sql, sold_stc_values_list)
            except (Exception, psycopg2.Error) as e:
                logger.exception(str(e))
                conn.rollback()
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                # Return
                return None
            else:
                conn.commit()
                count = cur.rowcount
                logger.info(f"properties sold stc status updated = {cur.rowcount}")
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                # Return the result count.
                return count
    
    def update_property_postcode_sold_nearby_url_values(self, properties_values):
        """
        Currently only updating the postcode value.
        """
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                sql = """
                UPDATE properties p
                SET rm_postcode = data.rm_postcode,
                rm_sold_nearby_url = data.rm_sold_nearby_url,
                rm_epc_cert_url = data.rm_epc_cert_url
                FROM (VALUES %s) AS data (
                    id, rm_postcode, rm_sold_nearby_url, rm_epc_cert_url
                )
                WHERE p.id = uuid(data.id);
                """
                # Use the psycopg2 execute_values function.
                execute_values(cur, sql, properties_values)
            except (Exception, psycopg2.Error) as e:
                logger.exception(str(e))
                conn.rollback()
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                return
            else:
                count = cur.rowcount
                conn.commit()
                logger.info(f"properties postcode & sold nearby urls updated = {count}")
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                return count
    
    def update_sales_history_attempted(self, property_ids):
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                sql = """
                UPDATE properties p
                SET rm_sale_history_attempted = data.rm_sale_history_attempted
                FROM (VALUES %s) AS data (id, rm_sale_history_attempted)
                WHERE p.id = uuid(data.id);
                """
                # Use the psycopg2 execute_values function.
                execute_values(cur, sql, property_ids)
            except (Exception, psycopg2.Error) as e:
                logger.exception(str(e))
                conn.rollback()
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                return
            else:
                conn.commit()
                count = cur.rowcount
                logger.info(f"properties sales history attempted updated = {count}")
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                return count
    
    def update_real_address_attempted(self, property_ids_and_real_address_attempted_vals):
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                sql = """
                UPDATE properties p
                SET rm_real_address_attempted = data.rm_real_address_attempted
                FROM (VALUES %s) AS data (rm_real_address_attempted, id)
                WHERE p.id = uuid(data.id);
                """
                # Use the psycopg2 execute_values function.
                execute_values(cur, sql, property_ids_and_real_address_attempted_vals)
            except (Exception, psycopg2.Error) as e:
                logger.exception(str(e))
                conn.rollback()
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                return
            else:
                conn.commit()
                count = cur.rowcount
                logger.info(f"properties real address validation attempted updated = {count}")
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                return count

    def update_real_address_value(self, property_real_address_data):
        """
        Update the given property entry with the real address value and set the real_address_attempted value
        to True, using the given property id.
        """
        with self.pool.getconn() as conn:
            try:
                cur = conn.cursor()
                sql = """
                UPDATE properties p
                SET rm_real_address = data.rm_real_address, 
                rm_real_address_attempted = data.rm_real_address_attempted
                FROM (VALUES %s) AS data (rm_real_address, rm_real_address_attempted, id)
                WHERE p.id = uuid(data.id);
                """
                # Use the psycopg2 execute_values function.
                execute_values(cur, sql, property_real_address_data)
            except (Exception, psycopg2.Error) as e:
                logger.exception(str(e))
                conn.rollback()
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                return
            else:
                conn.commit()
                count = cur.rowcount
                # Close the cursor object
                cur.close()
                # Put the connection back into the pool.
                self.pool.putconn(conn)
                logger.info(f"properties real address updated = {count}")
                return count