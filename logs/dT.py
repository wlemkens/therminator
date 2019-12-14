import numpy as np
import sys
import datetime

times = []
livingSP = []
livingT = []
badkamerSP = []
badkamerT = []
bureauSP = []
bureauT = []
nathanSP = []
nathanT = []
reqP = []
actP = []
exteriorT = []

def getStartIndices(data):
    indices = np.where(data[1:] - data[:-1] == 1)[0]
    dif = indices[1:] - indices[:-1]
    return np.append(indices[0], indices[np.where(dif != 1)[0] + 1])

def getEndIndices(data):
    indices = np.where(data[1:] - data[:-1] == 1)[0] + 1
    return np.append(indices[np.where(indices[1:] - indices[:-1] != 1)[0]], indices[-1])

# Check state when heating is on
def calculateHeatingCurve(setpoints, temperatures, otherSetpoints, otherTemperatures):
    # Filter the points where the set point is higher or equal to the temperature, but only for the requested room
    otherDiffs = [otherSP - otherT <= 0 for otherSP, otherT in zip(otherSetpoints, otherTemperatures)]
    diffs = setpoints - temperatures >= 0;
    samplePoints = diffs & np.array(otherDiffs).all(0)
    indices = np.where(samplePoints)[0]
    startIndices = indices[getStartIndices(indices)]
    endIndices = indices[getEndIndices(indices)]
    blocks = [[range(start, end + 1)] for start,end in zip(startIndices, endIndices)]
    temperatures_filtered = [temperatures[block] for block in blocks]
    setpoints_filtered =[setpoints[block] for block in blocks]
    print(temperatures_filtered)
    print(setpoints_filtered)



def loadFile(filename):
    global times, livingSP, livingT, badkamerSP, badkamerT, bureauSP, bureauT, nathanSP, nathanT, reqP, actP, exteriorT
    with open(filename, "r") as f:
        lineNb = 0
        for line in f:
            if lineNb > 0:
                parts = line.split(";")
                time = datetime.datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S')
                times += [time]
                livingSP += [float(parts[1])]
                livingT += [float(parts[2])]
                badkamerSP += [float(parts[4])]
                badkamerT += [float(parts[5])]
                bureauSP += [float(parts[7])]
                bureauT += [float(parts[8])]
                nathanSP += [float(parts[10])]
                nathanT += [float(parts[11])]
                reqP += [float(parts[13])]
                actP += [float(parts[14])]
                exteriorT += [float(parts[17])]
            lineNb += 1


loadFile(sys.argv[1])
livingSP = np.array(livingSP)
livingT = np.array(livingT)
badkamerSP = np.array(badkamerSP)
badkamerT = np.array(badkamerT)
bureauSP = np.array(bureauSP)
bureauT = np.array(bureauT)
nathanSP = np.array(nathanSP)
nathanT = np.array(nathanT)
reqP = np.array(reqP)
actP = np.array(actP)
exteriorT = np.array(exteriorT)

# Check state when heating is off
offIndices = np.array(np.where(np.array(actP) == 0)[0])
offOffsets = np.where(offIndices[1:] - offIndices[:-1] == 1)[0]
offOffsetsP1 = offOffsets + 1
offStarts = np.append(offOffsets[0], offOffsets[np.where(offOffsets[1:] - offOffsets[:-1] != 1)[0] + 1])
offEnds = np.append(offOffsetsP1[np.where(offOffsetsP1[1:] - offOffsetsP1[:-1] != 1)[0]], offOffsetsP1[-1])

dts = np.array(np.array(times)[offEnds]) - np.array(np.array(times)[offStarts])
dTs_living = np.array(np.array(livingT)[offEnds]) - np.array(np.array(livingT)[offStarts])
dTs_bureau = np.array(np.array(bureauT)[offEnds]) - np.array(np.array(bureauT)[offStarts])
dTs_badkamer = np.array(np.array(badkamerT)[offEnds]) - np.array(np.array(badkamerT)[offStarts])
dTs_nathan = np.array(np.array(nathanT)[offEnds]) - np.array(np.array(nathanT)[offStarts])
dTs_living_ext = np.array(np.array(livingT)[offStarts]) - np.array(np.array(exteriorT)[offStarts])
dTs_bureau_ext = np.array(np.array(bureauT)[offStarts]) - np.array(np.array(exteriorT)[offStarts])
dTs_badkamer_ext = np.array(np.array(badkamerT)[offStarts]) - np.array(np.array(exteriorT)[offStarts])
dTs_nathan_ext = np.array(np.array(nathanT)[offStarts]) - np.array(np.array(exteriorT)[offStarts])
seconds = np.array([dt.total_seconds() for dt in dts])
Tdt_living = dTs_living / dTs_living_ext / seconds
Tdt_bureau = dTs_bureau / dTs_bureau_ext / seconds
Tdt_badkamer = dTs_badkamer / dTs_badkamer_ext / seconds
Tdt_nathan = dTs_nathan / dTs_nathan_ext / seconds
Tdt_living_filtered = Tdt_living[~np.isnan(Tdt_living)]
Tdt_living_filtered = Tdt_living_filtered[np.where(Tdt_living_filtered > 0)]
Tdt_bureau_filtered = Tdt_bureau[~np.isnan(Tdt_bureau)]
Tdt_bureau_filtered = Tdt_bureau_filtered[np.where(Tdt_bureau_filtered > 0)]
Tdt_badkamer_filtered = Tdt_badkamer[~np.isnan(Tdt_badkamer)]
Tdt_badkamer_filtered = Tdt_badkamer_filtered[np.where(Tdt_badkamer_filtered > 0)]
Tdt_nathan_filtered = Tdt_nathan[~np.isnan(Tdt_nathan)]
Tdt_nathan_filtered = Tdt_nathan_filtered[np.where(Tdt_nathan_filtered > 0)]
print("Living heat loss {:}°C/°Cs".format(np.median(Tdt_living_filtered)))
print("Living heat loss {:}°C/°Cs".format(np.mean(Tdt_living_filtered)))
print("Bureau heat loss {:}°C/°Cs".format(np.median(Tdt_bureau_filtered)))
print("Bureau heat loss {:}°C/°Cs".format(np.mean(Tdt_bureau_filtered)))
print("Badkamer heat loss {:}°C/°Cs".format(np.median(Tdt_badkamer_filtered)))
print("Badkamer heat loss {:}°C/°Cs".format(np.mean(Tdt_badkamer_filtered)))
print("Nathan heat loss {:}°C/°Cs".format(np.median(Tdt_nathan_filtered)))
print("Nathan heat loss {:}°C/°Cs".format(np.mean(Tdt_nathan_filtered)))

# livingSP = np.array([10,10,10,10,10,10,10])
# livingT = np.array([10,9,9,9,9,9,10])
# bureauSP = np.array([10,10,10,10,10,10,10])
# badkamerSP = np.array([10,11,11,10,10,10,10])
# nathanSP = np.array([10,10,10,10,10,10,10])
# bureauT = np.array([10,10,10,10,10,10,10])
# badkamerT = np.array([10,10,10,10,10,10,10])
# nathanT = np.array([10,10,10,10,10,10,10])
calculateHeatingCurve(livingSP, livingT, [bureauSP, badkamerSP, nathanSP], [bureauT, badkamerT, nathanT])

# should return 0,1
# starts = getStartIndices(np.array([1,2,3,6,8,9,10,11,15,16]))
# starts = getStartIndices(np.array([0,3,4,5,6]))
# print(starts)
