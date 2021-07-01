import logging
from logging.handlers import RotatingFileHandler
from rightmove.rm_individual_property import RightMoveIndividualProperty
from rightmove.rm_property_search import RightMovePropertySearch
from rightmove.rm_property_sale_history import RightMovePropertySaleHistory
from rightmove.rm_area_sale_history import RightMoveAreaSaleHistory
from epc.epc import EPC
from database.pgsql import Database
from database.load_urls import load_urls
from client.client import WebClient
import json
import os
import threading
import time
import sys
from psycopg2 import OperationalError



def setup_logger():

    log_file = os.path.abspath(os.path.join(os.sep, os.getcwd(), 'logs', 'property_leads.log'))
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    # Create an instance for our logger
    logger = logging.getLogger()
    # Set the level to DEBUG
    logger.setLevel(logging.DEBUG)
    # Create the rotating File handler
    fh = RotatingFileHandler(
        os.path.join(os.getcwd(), log_file),
        mode='a', maxBytes=5000000, backupCount=50
    )
    # Set the level to DEBUG
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    # Define our input variables
    logger.info('Setting the appropriate input and config file paths')
    # Define our input variables
    logger.info('Initialising input variables')

    return logger

def main():

    running = threading.Event()
    program_sleep_time = 30 # Seconds

    # Create our logger instance
    logger = setup_logger()
    
    # Config file path
    config_path = os.path.abspath(os.path.join(os.sep, os.getcwd(), 'config', 'config.json'))

    # Open and Read the config Variables
    params = json.load(open(config_path, "r"))

    # Create an instance of the Database and pass in the parameters from the config file.
    db = Database(
        **params["database"]
    )
    # Url load Helper Function
    # load_urls(r"database\urls\southend.txt", db)

    # Create an instance of the WebClient Class and pass in the parameters from the config file.
    web_client = WebClient(
        **params["web_client"]
    )

    # Create an instance of the RightMovePropertySearch Class.
    rmps = RightMovePropertySearch(
        web_client,
        params["property_search"]["rm_maximum_results"],
        params["property_search"]["rm_sleep_time"],
        db,
        running,
        program_sleep_time
    )

    # Create an instance of the RightMoveIndividualProperty Class.
    rmip = RightMoveIndividualProperty(
        web_client,
        db,
        running,
        program_sleep_time
    )

    # Create an instance of the RightMoveSaleHistory Class.
    rmpsh = RightMovePropertySaleHistory(
        params["web_client"]["rm_base_url"],
        params["selenium"]["rm_sales_history_cookies_rpath"],
        params["selenium"]["rm_sales_history_element_rpath"],
        params["selenium"]["rm_sales_history_table_rpath"],
        db,
        running,
        program_sleep_time
    )

    # Create an instance of the RightMoveAreaSaleHistory Class.
    rmash = RightMoveAreaSaleHistory(
        web_client,
        db,
        running,
        program_sleep_time
    )

    # Create an instance of our Epc (Energy Performance Certificate) class.
    epc = EPC(
        program_sleep_time,
        db,
        running,
        params["epc"]["epc_base_url"]
    )

    # Run our Methods
    
    # # RightMovePropertySearch
    # rmps.start()

    # # RightMoveIndividualProperty Search
    # rmip.start()

    # # RightMovePropertySaleHistory
    # rmpsh.start()

    # RightMoveAreaSaleHistory
    rmash.start()

    # Epc
    # epc.start()


    try:
        while True:
            time.sleep(5)
           
    # rmps.join()
    except KeyboardInterrupt:
        logger.info("Keyboard interupt received")
        print("Keyboard interupt received")
        # Turn off the running flag.
        running.set()
        # Join the Threads (wait for them to complete)
        # rmps.join()
        # rmip.join()
        # rmpsh.join()
        rmash.join()
        # epc.join()        
    
    # Catch the Psycopg2 Operational Error and recreate the datebase connection.
    except OperationalError as e:
        logger.exception(str(e))
        logger.exception("Caught Psycopg2 Operational Error, restarting database connection")
        # Create a new datebase instance
        db = Database(
        **params["database"]
        )         

    
    # Exit with status 0
    sys.exit(0)






if __name__ == "__main__":
    main()