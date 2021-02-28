# WSPR-Python

Python 3 Script that pulls data from WSPR.net and is processed 
using BeautifulSoup into Postgres database.
This will provide a database of data which can be used to evaluate antenna performance
and/or band conditions.

The Developers/Admins use case is for a WebTechnologies - https://www.bangor.ac.uk/computer-science-and-electronic-engineering/postgraduate-modules/ICE-4111 - module to incorporate the data
into a customized website via Javascript calls into the Postgres database, of course
you can use it however you like :)

## Requirements

- Postgres DB (can be remote or local)
- Python Packages 
   - Beautiful Soup
   - requests
   - time
   - datetime
   - psycopgp2

- A method to transmit WSPR packets
   - WSJT-X in WSPR mode - https://physics.princeton.edu/pulsar/k1jt/wsjtx.html
   - RasperryPi with WSPR Hat - https://tapr.org/product/wspr/

## RF Setup

To benefit the most from this script you will need a method of transmitting WSPR packets.

The setup used here is a RaspberryPi with a 40M WSPR Pi Hat into a horizontal inverted-v
Dipole mounted at a 1/4 wave distance vertically (10 meters) which has given good results.

See - https://www.qsl.net/aa3rl/ant2.html

## Setup

Install is assumed on Linux Ubuntu.

### Postgres

- Install postgres via apt
```
sudo apt update
sudo apt install postgresql postgresql-contrib
```

If you are running the script locally you will be ok to use localhost, else modify

Modify the listen address, in this case listen all interfaces

```
vi /etc/postgresql/12/main/postgresql.conf
#------------------------------------------------------------------------------
# CONNECTIONS AND AUTHENTICATION
#------------------------------------------------------------------------------

# - Connection Settings -

listen_addresses = '*'          # what IP address(es) to listen on;
```

The setup the ACL for your local network, or if feeling brave all (0.0.0.0/0)

```
vi /etc/postgresql/12/main/pg_hba.conf
host    all             all             192.168.1.0/24          trust
```

- Create a WSPR account

```
createuser --interactive
Enter name of role to add: wspr
Shall the new role be a superuser? (y/n) y
```

- Create WSPR Database

```
createdb wspr
```

The script creates a table, but you can create it via the follow

```
sudo -u wspr psql

create table newspots (
   timestamp varchar(20),
   tx_call varchar(20),
   freq real, 
   snr integer,
   drift integer,
   tx_loc varchar(6),
   dbm varchar(3),
   power real,
   rx_call varchar(20),
   rx_loc varchar(6),
   distance integer,
   az integer,
   mode varchar(6)
);
```
### Database Note
Please note the database is setup to truncate each time.
Currently I'm creating an MVP as my assignment is on Web Technologies and not just Python.
Feel free to modify and request a trunk/merge if you want to add to the project.
With my WSPR station transmitting every 10 minutes, i get 2 weeks of data returned in the DB.

### Python Packages

- Install Postgres Python connector
```
sudo apt-get install python-psycopg2-doc -y
sudo apt-get install python3-psycopg2
sudo apt-get install python3-psycopg2-dbg
```

### Modify script parameters
Modify the following lines to match your environment

- Postgress connection
```
        conn = psycopg2.connect(
            user="wspr",
            password="THEPASSWORDFORWSPR",
            host="THESERVERIPADDRESS",
            port=5432,
            database="wspr"
           )
```
- Account ID and Number of records

```
# globals
callsign = '2e0fwe'
records = 10000
```

# Running
The script is self contained and running in a loop. The simpliest way is to just call the script
```
python3 wspr_monitor.py
```
Whereby it will loop around pulling stats from WSPR and putting them into the Postgres Database
Normal Output, which can be redicted to a log file if so desired is as follows.
```
Date and time = 28/02/2021 21:46:30
Getting Records via http
Connected to database!
Truncate table
Inserting new records into newspots....
Records NOT inserted......
Records inserted complete
Hoovering tables
date and time = 28/02/2021 21:48:46
sleeping for five minutes
```

putting the script in screen or a background process will keep it running.

## Verify output

From the command line the 'wspr' account can be used to pull data out.

```
su - wspr
psql
select * from newspots;
   timestamp     | tx_call |   freq    | snr | drift | tx_loc | dbm | power |   rx_call   | rx_loc | distance |  az   |  mode  
------------------+---------+-----------+-----+-------+--------+-----+-------+-------------+--------+----------+-------+--------
 2021-02-28 20:14 | 2E0FWE  |  7.040178 | -27 |     0 | IO90bs | +23 |   0.2 | SM2BYC      | KP25ax |     2235 |  1389 | WSPR-2
 2021-02-28 20:14 | 2E0FWE  |  7.040127 | -16 |     0 | IO90bs | +23 |   0.2 | OE6RHT      | JN77sb |     1334 |   829 | WSPR-2
 2021-02-28 20:14 | 2E0FWE  |  7.040154 | -17 |     0 | IO90bs | +23 |   0.2 | IQ4JO       | JN63hx |     1324 |   823 | WSPR-2
 2021-02-28 20:14 | 2E0FWE  |  7.040152 | -22 |     0 | IO90bs | +23 |   0.2 | S56KVJ      | JN76tm |     1366 |   849 | WSPR-2
 ```

 Using standard queries can build a powerful knowledge base of WSPR info of your station.
 
