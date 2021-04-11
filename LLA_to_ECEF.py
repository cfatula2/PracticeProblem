import argparse
import math
import os
import sys

from bisect import bisect_left

# Compute ECEF position vector using latitude (degrees), 
# longitude (degrees), and altitude (meters)
def computeECEF(lat, long, alt):
    f = 1/298.257223563
    a = 6378137

    b = a*(1-f)
    e2 = (a ** 2 - b ** 2) / (a ** 2)
    N = a / math.sqrt(1 - e2*(math.sin(math.radians(lat)) ** 2))
    
    x = (N + alt)*(math.cos(math.radians(lat)))*(math.cos(math.radians(long)))
    y = (N + alt)*(math.cos(math.radians(lat)))*(math.sin(math.radians(long)))
    z = (((b**2)/(a**2))*N + alt)*(math.sin(math.radians(lat)))
    
    return x, y, z

# Compute velocity using ECEF positions in same plane
def computeVelocity(oldTime, newTime, oldPosition, newPosition):
    velocity = 0
    if oldTime >= 0 and newTime >= oldTime:
        velocity = (newPosition - oldPosition)/(newTime - oldTime)
    return velocity

# Compute velocity vector using ECEF x, y, z positions for adjacent 
# data points
def computeVelocityVector(previousRow, currentRow):
    velocityVector = []
    
    for coordIndex in range(4,7):
        vel = computeVelocity(previousRow[0], currentRow[0], \
            previousRow[coordIndex], currentRow[coordIndex])
        velocityVector.append(vel)
    
    return velocityVector
    
# Read and parse input file, convert LLA to ECEF x,y,z coordinates,
# and compute velocities
# Each row of positionData list should contain the following when this
# function completes:
# [timestamp, lat, long, alt, x, y, z, Vx, Vy, Vz]
def performConversion(filePath):
    file = open(filePath, 'r')
    
    positionData = []
    timeStamps = []
    index = 0
    
    for line in file:
        line = line.strip()
        data = line.split(",")
        data = [float(x) for x in data]
        if len(data) == 4:
            timeStamps.append(data[0])
            x, y, z = computeECEF(data[1], data[2], data[3]*1000)
            data.append(x)
            data.append(y)
            data.append(z)

            velVec = []
            if index > 0:
                velVec = computeVelocityVector(positionData[index-1], data)
            else:
                velVec = [0, 0, 0]
            for vel in velVec:
                data.append(vel)
            
            positionData.append(data)    
            index+=1
    file.close()
    
    return positionData

# Interpolate individual element in velocity vector    
def interpolateVelocity (ts, prevTs, postTs, prevVel, postVel):
    deltaTime = postTs - prevTs
    deltaVel = postVel - prevVel
    return prevVel + (((ts - prevTs)/ deltaTime))* deltaVel
    
# Interpolate velocity vector for a given timestamp using known data from
# adjacent timestamps
def interpolateVelocityVector (ts, rowBefore, rowAfter):
    velVector = []
    
    for velIndex in range(7,10):
        interpVel = interpolateVelocity(ts, rowBefore[0], rowAfter[0], \
            rowBefore[velIndex], rowAfter[velIndex])
        velVector.append(interpVel)
    
    return velVector

# Determine adjacent existing rows for a given random timestamp, if
# such rows exist, to use to interpolate velocity vector
def findClosest(ecefData, timestampToFind):
    timestampColumn = [row[0] for row in ecefData]
    position = bisect_left(timestampColumn, timestampToFind)
    
    # If timestampToFind < first timestamp in data OR 
    # timestampToFind > last timestamp in data, cannot perform 
    # velocity interpolation
    if (position == 0 or position == len(ecefData)): 
        print("Not enough data for interpolation")
        return 0, 0
    rowBefore = ecefData[position - 1]
    rowAfter = ecefData[position]
    
    return rowBefore, rowAfter

# Main routine
def main(filePath, timeStampsToInterpolate):
    ecefData = performConversion(filePath)

    for ts in timeStampsToInterpolate:
        before, after = findClosest(ecefData, ts)
        if (before and after):
            x, y, z = interpolateVelocityVector(ts, before, after)
            print("{} : [{}, {}, {}]".format(ts, x, y, z)) 

if __name__ == "__main__":
    desc = "Given an input CSV file with the following - A UNIX timestamp (in seconds \
        since the UNIX epoch), WGS84 Latitude in degrees, WGS84 Longitude in degrees \
        \n  WGS84 altitude in kilometers - compute the Earth-centered, \
        earth-fixed x, y, and z coordinates in meters and velocities in meters/sec in \
        the x, y, and z planes"
    parser = argparse.ArgumentParser(description = desc)
    parser.add_argument('-f', required = True, help = "Input CSV file")
    parser.add_argument('-t', required = False, help = "Optional timestamp(s) \
        from which to interpolate velocity vector", nargs='+', type = float)
    args = parser.parse_args()
    
    if not os.path.isfile(args.f):
        print("File " + args.f + " does not exist")
        parser.print_help()
        sys.exit()

    main(args.f, args.t)