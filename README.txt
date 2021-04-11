To run this Python script, first make sure Python 3 is installed on the target
machine. 

If python has not been added to your PATH environment variable, include 
"python " prior to the arguments described below.

Run LLA_to_ECEF.py using the following space separated arguments:
argv[0]	    - Path to LLA_to_ECEF.py in relation to location where script is 
			  being run
argv[1]     - Absolute or relative path to input CSV file
argv[2, ..] - Space separated list of timestamps to interpolate velocity 
			  vector

General summary of processing performed by LLA_to_ECEF.py:
	1. Open CSV data file
	2. Read and parse each line, perform ECEF conversion and velocity 
	   computation
		- Store data from each line in a list
		- Convert latitude, longitude, and altitude to ECEF x, y, z 
		  coordinates and append to list
		- Compute and append velocity vector to list
		- Append list for individual line to list-of-lists for all lines
	3. Use completed list-of-lists to interpolate velocity vector for given
	   timestamp(s) passed as argv[2, ..]
		- Find adjacent entries in list-of-lists for preceding and 
		  subsequent timestamps (if they exist)
		- Linearly interpolate velocity vector at given timestamp
		- Return and print velocity vector in the following format:
		  Timestamp : [Velocity_x, Velocity_y, Velocity_z]