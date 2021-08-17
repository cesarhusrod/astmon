# astmon

This package is composed by two steps:

    1. SQLite database creation
    2. Query and plotting filtered data

## 1. SQLite database creation
Use script create_database.py in this way

    python create_database.py --overwrite=True --output_dir=./ path_to_dat_files

It creates astmodDB.db database file in 'output_dir'. 

    - If overwrite=True then database is dropped and created again. It is filled with data taken from '*.dat' files located in 'path_to_dat_files'.
    
    - If overwrite=False, only new data not stored previously is inserted in database.

## 2. Querying and plotting filtered data

Use script astmon.py

Probed cases of use:

* Query in one time period and B, V filters

    python astmon.py --period '2020-03-01 00:00:00' '2020-04-15 23:59:59' --filters B V -v astmonDB.db

* Query in one time period, filters B and V, and positions 3, 4 and 5 

    python astmon.py --period '2020-03-01 00:00:00' '2020-04-15 23:59:59' --filters B V  --positions 3 4 5 -v astmonDB.db

* Query for 2 full years, all filters and all positions

    python astmon.py --years 2020 2021 -v astmonDB.db

* Query for one month in two years, all filters and all positions
    python astmon.py --years 2020 2021 --months 4 -v astmonDB.db
