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

def filterBlock(block):
    return np.array(np.where(block[1:] - block[:-1] > 0)[0])


# Check state when heating is on
def calculateQuadraticHeatingCurve(times, setpoints, temperatures, externalTs, h_loss, otherSetpoints, otherTemperatures):
    # Filter the points where the set point is higher or equal to the temperature, but only for the requested room
    otherDiffs = [otherSP - otherT <= 0 for otherSP, otherT in zip(otherSetpoints, otherTemperatures)]
    diffs = setpoints - temperatures >= 0;
    samplePoints = diffs & np.array(otherDiffs).all(0)
    indices = np.where(samplePoints)[0]
    startIndices = indices[getStartIndices(indices)]
    endIndices = indices[getEndIndices(indices)]
    blocks = [[range(start, end + 1)] for start,end in zip(startIndices, endIndices)]
    temperatures_filtered = np.array([np.array(temperatures[block]) for block in blocks])
    setpoints_filtered =np.array([np.array(setpoints[block]) for block in blocks])
    externalTs_filtered =np.array([np.array(externalTs[block]) for block in blocks])
    times_filtered = np.array([np.array(times[block]) for block in blocks])
    blockIndices = [filterBlock(np.array(block)) for block in temperatures_filtered]
    dT_blocks = np.array([temps[block+1] - temps[block] for temps,block in zip(temperatures_filtered, blockIndices)])
    dt_blocks = np.array([times[block+1] - times[np.append([0], block[:-1]+1)] for times,block in zip(times_filtered, blockIndices)])
    dTh_blocks = dT_blocks/dt_blocks
    TSP_blocks = np.array([temps[np.append([0], block+1)][:-1] for temps,block in zip(setpoints_filtered, blockIndices)])
    T_blocks = np.array([temps[np.append([0], block+1)][:-1] for temps,block in zip(temperatures_filtered, blockIndices)])
    externalT_blocks = np.array([temps[np.append([0], block+1)][:-1] for temps,block in zip(externalTs_filtered, blockIndices)])
    deltaT_ext_blocks = T_blocks - externalT_blocks
    deltaT_err_blocks = TSP_blocks - T_blocks
    # print("dTh", (dTh_blocks))
    # print("deltaT_ext", (deltaT_ext_blocks))
    # print("deltaT_err", (deltaT_err_blocks))
    deltaT_err_1 = np.concatenate([block[:-2] for block in deltaT_err_blocks])
    deltaT_err_2 = np.concatenate([block[1:-1] for block in deltaT_err_blocks])
    deltaT_err_3 = np.concatenate([block[2:] for block in deltaT_err_blocks])
    deltaT_ext_1 = np.concatenate([block[:-2] for block in deltaT_ext_blocks])
    deltaT_ext_2 = np.concatenate([block[1:-1] for block in deltaT_ext_blocks])
    deltaT_ext_3 = np.concatenate([block[2:] for block in deltaT_ext_blocks])
    # print ("deltaT_err_1", deltaT_err_1)
    # print ("deltaT_err_2", deltaT_err_2)
    # print ("deltaT_err_3", deltaT_err_3)
    # print ("deltaT_ext_1", deltaT_ext_1)
    # print ("deltaT_ext_2", deltaT_ext_2)
    # print ("deltaT_ext_3", deltaT_ext_3)
    b = h_loss * ((deltaT_ext_1 - deltaT_ext_2) / (deltaT_err_1**2 - deltaT_err_2**2) - (deltaT_ext_2 - deltaT_ext_3) / (deltaT_err_2**2 - deltaT_err_3**2)) / ((deltaT_err_1 - deltaT_err_2) / (deltaT_err_1**2 - deltaT_err_2**2) - (deltaT_err_2 - deltaT_err_3) / (deltaT_err_2**2 - deltaT_err_3**2))
    a = h_loss * ((deltaT_ext_1 - deltaT_ext_2) / (deltaT_err_1**2 - deltaT_err_2**2)) - b * ((deltaT_err_1 - deltaT_err_2) / (deltaT_err_1**2 - deltaT_err_2**2))
    # print("a", a)
    # print("b", b)
    print("median a =",np.nanmedian(a))
    print("median b =",np.nanmedian(b))
    return [np.nanmedian(a), np.nanmedian(b)]

def calculateLinearHeatingCurve(times, setpoints, temperatures, externalTs, h_loss, otherSetpoints, otherTemperatures):
    # Filter the points where the set point is higher or equal to the temperature, but only for the requested room
    otherDiffs = [otherSP - otherT <= 0 for otherSP, otherT in zip(otherSetpoints, otherTemperatures)]
    diffs = setpoints - temperatures >= 0;
    samplePoints = diffs & np.array(otherDiffs).all(0)
    indices = np.where(samplePoints)[0]
    startIndices = indices[getStartIndices(indices)]
    endIndices = indices[getEndIndices(indices)]
    blocks = [[range(start, end + 1)] for start,end in zip(startIndices, endIndices)]
    temperatures_filtered = np.array([np.array(temperatures[block]) for block in blocks])
    setpoints_filtered =np.array([np.array(setpoints[block]) for block in blocks])
    externalTs_filtered =np.array([np.array(externalTs[block]) for block in blocks])
    times_filtered = np.array([np.array(times[block]) for block in blocks])
    blockIndices = [filterBlock(np.array(block)) for block in temperatures_filtered]
    dT_blocks = np.array([temps[block+1] - temps[block] for temps,block in zip(temperatures_filtered, blockIndices)])
    dt_blocks = np.array([times[block+1] - times[np.append([0], block[:-1]+1)] for times,block in zip(times_filtered, blockIndices)])
    dTh_blocks = dT_blocks/dt_blocks
    TSP_blocks = np.array([temps[np.append([0], block+1)][:-1] for temps,block in zip(setpoints_filtered, blockIndices)])
    T_blocks = np.array([temps[np.append([0], block+1)][:-1] for temps,block in zip(temperatures_filtered, blockIndices)])
    externalT_blocks = np.array([temps[np.append([0], block+1)][:-1] for temps,block in zip(externalTs_filtered, blockIndices)])
    deltaT_ext_blocks = T_blocks - externalT_blocks
    deltaT_err_blocks = TSP_blocks - T_blocks

    h = (np.concatenate(dTh_blocks) + np.concatenate(deltaT_ext_blocks) * h_loss) / np.concatenate(deltaT_err_blocks)
    # print(h)
    return h



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
times = np.array(times)
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
h_loss_living = np.mean(Tdt_living_filtered)
h_loss_bureau = np.mean(Tdt_bureau_filtered)
h_loss_badkamer = np.mean(Tdt_badkamer_filtered)
h_loss_nathan = np.mean(Tdt_nathan_filtered)
print("Living heat loss {:}°C/°Cs".format(np.median(Tdt_living_filtered)))
print("Living heat loss {:}°C/°Cs".format(np.mean(Tdt_living_filtered)))
print("Bureau heat loss {:}°C/°Cs".format(np.median(Tdt_bureau_filtered)))
print("Bureau heat loss {:}°C/°Cs".format(np.mean(Tdt_bureau_filtered)))
print("Badkamer heat loss {:}°C/°Cs".format(np.median(Tdt_badkamer_filtered)))
print("Badkamer heat loss {:}°C/°Cs".format(np.mean(Tdt_badkamer_filtered)))
print("Nathan heat loss {:}°C/°Cs".format(np.median(Tdt_nathan_filtered)))
print("Nathan heat loss {:}°C/°Cs".format(np.mean(Tdt_nathan_filtered)))

secs = np.array([timestmp.timestamp() for timestmp in times])
h_living = calculateLinearHeatingCurve(secs, livingSP, livingT, exteriorT, h_loss_living, [livingSP, bureauSP, badkamerSP, nathanSP], [livingT, bureauT, badkamerT, nathanT])
h_bureau = calculateLinearHeatingCurve(secs, bureauSP, livingT, exteriorT, h_loss_living, [bureauSP, badkamerSP, nathanSP], [livingT, badkamerT, nathanT])
h_badkamer = calculateLinearHeatingCurve(secs, badkamerSP, badkamerT, exteriorT, h_loss_badkamer, [livingSP, bureauSP, nathanSP], [livingT, bureauT, nathanT])
h_nathan = calculateLinearHeatingCurve(secs, nathanSP, nathanT, exteriorT, h_loss_nathan, [livingSP, bureauSP, badkamerSP], [livingT, bureauT, badkamerT])
print("Living heating coefficient {:}°C/°Cs".format(h_living))
print("Bureau heating coefficient {:}°C/°Cs".format(h_bureau))
print("Badkamer heating coefficient {:}°C/°Cs".format(h_badkamer))
print("Nathan heating coefficient {:}°C/°Cs".format(h_nathan))
