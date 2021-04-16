To run this Python script, first make sure Python 3 is installed on the target
machine. 

Note: If python has not been added to your PATH environment variable, include 
"python " prior to the arguments described below.


How to run LLA_to_ECEF.py:

Synopsis:
LLA_to_ECEF.py -f PATH_TO_CSV_FILE -t [timestamps to interpolate] 

LLA_to_ECEF.py               Absolute or relative path to LLA_to_ECEF.py
PATH_TO_CSV_FILE             Absolute or relative path to input CSV file
[timestamps to interpolate]  Space separated list of timestamps from which to 
							 interpolate a velocity vector

Run LLA_to_ECEF.py -h OR LLA_to_ECEF.py --help for additional help with the 
arguments.


Summary of processing performed by LLA_to_ECEF.py:
	1. Parse input arguments
	2. Open CSV data file
	3. Read and parse each line of CSV data file, perform ECEF conversion 
	   and velocity computation
		- Store data from each line in a list
		- Using latitude, longitude, and altitude, compute ECEF x, y, z   
		  coordinates and append to list
		- Compute and append velocity vector to list. Final format should be:
		  [timestamp, lat, long, alt, x, y, z, V_x, V_y, V_z]
		- Append list to position data table, which is a list-of-lists
	4. Use completed position data table to interpolate velocity vector for
	   given timestamp(s)
		- Find adjacent entries in position data table for preceding and 
		  subsequent timestamps (if they exist, otherwise print error 
		  message)
		- Linearly interpolate velocity vector at given timestamp
		- Return and print velocity vector in the following format:
		  Timestamp : [Velocity_x, Velocity_y, Velocity_z]