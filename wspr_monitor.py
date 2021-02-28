""""WSPR Monitor 

This script pulls data from WSPRnet 'old' DB API via BeauutifulSoup
and puts them into a Postgres Database where the data can be used
for analysis.

The callsign and amount of records can be adjusted in the  globals.
The system depends on a 'remote' postgres db being available, although the script
can be easily be modified to localhost to run on the same system.

The resulting data can be queried from postgres, a simple query
to return all data can be select * from newspots.

The data values available are the same as those in the WSPR web interface.
timestamp, tx_call, freq, snr, drift, tx_loc, dbm, power, rx_call, rx_loc, distance, az, mode.

The script is comprised of two functions.
    
    getspots(records,callsign) - returns WSPR data from wsprnet.org
    gettime() - get the current date and time value used for logs

Overall the script takes about 5 minutes to run, 
designed to interleave between the 10 minute transmission period of a WSPR station.

"""



# importing the libraries
from bs4 import BeautifulSoup
import requests
#import datetime
import time
from datetime import datetime,timedelta
import psycopg2

def getspots(nrspots, callsign):
    """Gets spots via http and inserts into PostgresDB

    Parameters
    ----------
    nrspots : int
        The amount of spots to returns from WSPRnet
    callsign : string
        Callsign of the user to be monitored

    Returns
    -------
    newspots
        an array of WSPR data deterimined by the number of spots
        and call sign given
    """
    # URL to curl values from, pull the max
    url="https://wsprnet.org/olddb?mode=html&band=all&limit=" + str(nrspots) + "&findcall=" + str(callsign) + "&findreporter=&sort=date"

    # Make a GET request to fetch the raw HTML content
    html_content = requests.get(url).text

    # Parse the html content
    soup = BeautifulSoup(html_content, "html.parser")
    data = []
    table = soup.find_all('table')[2]
    rows = table.findAll('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele]) # Get rid of empty values

    # Strip empty rows
    newspots = [ele for ele in data if ele]
    #print (newspots)

    # put newspots into a database

    conn = None
    data = None

    try:
        conn = psycopg2.connect(
            user="wspr",
            password="PASSWORD",
            host="SERVERIP",
            port=5432,
            database="wspr"
           )

        conn.autocommit = True

        cur = conn.cursor()
        print ("Connected to database!")
        # truncate table
        print ("Truncate table")
        cur.execute ('truncate newspots')
        conn.commit()
        cur.execute('create table if not exists newspots(timestamp timestamp(20), tx_call varchar(10), freq real, snr integer, drift integer,  tx_loc varchar(6), dbm varchar(3), power integer, rx_call varchar(10), rx_loc varchar(6), distance integer, az integer, mode varchar(6))')
        print ("Inserting new records into newspots....")
        for row in newspots:      
            #print (row)
            insert_stmt = 'INSERT INTO newspots (timestamp, tx_call, freq, snr, drift, tx_loc, dbm, power, rx_call, rx_loc, distance, az, mode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING'
            cur.execute(insert_stmt, row)
            # data = cur.fetchall()
            # Commit your changes in the database
            conn.commit()
            
        if not data:
            print ("Records NOT inserted......")
            conn.commit()
        print("Records inserted complete")
        print ("Hoovering tables")
        cur.execute('vacuum (verbose, analyze) newspots')
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error connecting to Postgres Platform: {e}")
    except Exception as e:
        print("Exception in _query: %s" % e)
    finally:
        if conn:
            conn.close()
    return (newspots)

def gettime():
    """Prints the current date and time

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    now = datetime.now()
    #print("now =", now)
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print("date and time =", dt_string)	
    return()

# globals
callsign = 'YOURCALLSIGN'
records = 10000
sleeptime = 60

while 1==1:
    gettime()
    print ("Getting Records via http")
    getspots(records,callsign)
    gettime()
    print ("sleeping for five minutes")
    time.sleep(300)    
