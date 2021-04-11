import math
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
    
# Read and parse input file, convert LLA to ECEF x,y,z coordinates,
# and compute velocities
# Each row of positionData list should contain the following when this
# function completes:
# [timestamp, lat, long, alt, x, y, z, Vx, Vy, Vz]
def performConversion(filePath):
    file = open(filePath, 'r')
    endOfFile = False
    positionData = []
    timeStamps = []
    index = 0
    while not endOfFile:
        line = file.readline()
        if line:
            line = line.strip()
            data = line.split(",")
            data = [float(x) for x in data]
            #data = list(np.float_(data))
            if len(data) == 4:
                timeStamps.append(data[0])
                x, y, z = computeECEF(data[1], data[2], data[3]*1000)
                data.append(x)
                data.append(y)
                data.append(z)
                coordIndex = 4
                for i in range(0,3):
                    if index > 0:
                        vel = computeVelocity(positionData[index-1][0], data[0], \
                        positionData[index-1][coordIndex], data[coordIndex])
                        data.append(vel)
                    else:
                        data.append(0)
                    coordIndex+=1
                positionData.append(data)
                index+=1
                # if (index >= 10):
                    # endOfFile = True
            # print(data)
        else:
            endOfFile = True
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
    velIndex = 7
    for i in range(0,3):
        interpVel = interpolateVelocity(ts, rowBefore[0], rowAfter[0], \
        rowBefore[velIndex], rowAfter[velIndex])
        velVector.append(interpVel)
        velIndex+=1
    
    return velVector

# Determine adjacent existing rows for a given random timestamp, if
# such rows exist, to use to interpolate velocity vector
def findClosest(ecefData, timestampToFind):
    timestampColumn = [row[0] for row in ecefData]
    position = bisect_left(timestampColumn, timestampToFind)
    
    if (position == 0): # timestampToFind < first timestamp in data
        print("Not enough data for interpolation")
        return 0, 0
    if (position == len(ecefData)): # timestampToFind > last timestamp in data
        print("Not enough data for interpolation")
        return 0, 0
    rowBefore = ecefData[position - 1]
    rowAfter = ecefData[position]
    
    #print(rowBefore)
    #print(rowAfter)
    
    return rowBefore, rowAfter

# Main routine
def main():
    if len(sys.argv) > 1:
        ecefData = performConversion(sys.argv[1])
        if len(sys.argv) >= 2:
            argIndex = 2
            while (argIndex < len(sys.argv)):
                timestamp = float(sys.argv[argIndex])
                print(timestamp, end = ": ")
                before, after = findClosest(ecefData, timestamp)
                if (before and after):
                    #print(timestamp, end = ": [")
                    x, y, z = interpolateVelocityVector(timestamp, before, after)
                    print("[", end = "")
                    print(x, end = ", ")
                    print(y, end = ", ")
                    print(z, end = "]\n")
                argIndex+=1
    #print(interpolateVelocity(7.4, 3, 15, 1, 10))

if __name__ == "__main__":
    main()