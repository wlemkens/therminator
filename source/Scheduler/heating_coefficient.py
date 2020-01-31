import os
import numpy as np
import datetime

def getStartIndices(data):
    indices = np.where(data[1:] - data[:-1] == 1)[0]
    if len(indices) > 0:
        dif = indices[1:] - indices[:-1]
        ends = np.where(dif != 1)
        if len(ends) > 0:
            head = indices[0]
            return np.append(head, indices[ends[0] + 1])
        return indices[0]
    return np.array([])


def getEndIndices(data):
    indices = np.where(data[1:] - data[:-1] == 1)[0] + 1
    ends = np.where(indices[1:] - indices[:-1] != 1)
    if len(ends) > 0:
        return np.append(indices[ends[0]], indices[-1])
    return indices[-1]

def filterBlock(block):
    return np.array(np.where(block[1:] - block[:-1] > 0)[0])


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
    if len(indices) > 0:
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

        hs = (np.concatenate(dTh_blocks) + np.concatenate(deltaT_ext_blocks) * h_loss) / np.concatenate(deltaT_err_blocks)
        h = np.nanmedian(hs)
    else:
        h = 0.005
    # print(h)
    return h / 2

def calculateHeatLoss(actP, times, temperatures, exteriorT):
    # Check state when heating is off
    offIndices = np.array(np.where(np.array(actP) == 0)[0])
    offOffsets = np.where(offIndices[1:] - offIndices[:-1] == 1)[0]
    offOffsetsP1 = offOffsets + 1
    offStarts = np.append(offOffsets[0], offOffsets[np.where(offOffsets[1:] - offOffsets[:-1] != 1)[0] + 1])
    offEnds = np.append(offOffsetsP1[np.where(offOffsetsP1[1:] - offOffsetsP1[:-1] != 1)[0]], offOffsetsP1[-1])

    dts = np.array(np.array(times)[offEnds]) - np.array(np.array(times)[offStarts])
    dTs = np.array(np.array(temperatures)[offEnds]) - np.array(np.array(temperatures)[offStarts])
    dTs_ext = np.array(np.array(temperatures)[offStarts]) - np.array(np.array(exteriorT)[offStarts])
    seconds = np.array([dt for dt in dts])
    Tdt = dTs / dTs_ext / dts
    Tdt_filtered = Tdt[~np.isnan(Tdt)]
    Tdt_filtered = Tdt_filtered[np.where(Tdt_filtered > 0)]
    h_loss = np.mean(Tdt_filtered)
    return h_loss

def getLogs(directory):
    list = os.listdir(directory)

    # Loop and add files to list.
    pairs = []
    for file in list:
        if file.endswith(".log"):
            # Use join to get full file path.
            location = os.path.join(directory, file)

            # Get size and add to list of tuples.
            size = os.path.getsize(location)
            pairs.append((size, file))

    # Sort list of tuples by the first element, size.
    pairs.sort(key=lambda s: s[0], reverse=True)
    return [os.path.join(directory,file[1]) for file in pairs]

def isValidLog(log):
    with open(log, "r") as f:
        lineNb = 0
        for line in f:
            parts = line.split(";")
            return len(parts) == 18


def loadLog(log):
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
    with open(log, "r") as f:
        lineNb = 0
        for line in f:
            if lineNb > 0:
                parts = line.split(";")
                time = datetime.datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S').timestamp()
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
    return np.array(times), np.array(livingSP), np.array(livingT), np.array(badkamerSP), np.array(badkamerT), np.array(bureauSP), np.array(bureauT), np.array(nathanSP), np.array(nathanT), np.array(reqP), np.array(actP), np.array(exteriorT)

def loadLogV2(log):
    times = []
    livingSP = []
    livingT = []
    livingOn = []
    badkamerSP = []
    badkamerT = []
    badkamerOn = []
    bureauSP = []
    bureauT = []
    bureauOn = []
    nathanSP = []
    nathanT = []
    nathanOn = []
    reqP = []
    actP = []
    exteriorT = []
    with open(log, "r") as f:
        lineNb = 0
        for line in f:
            if lineNb > 0:
                parts = line.split(";")
                time = datetime.datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S').timestamp()
                times += [time]
                livingSP += [float(parts[1])]
                livingT += [float(parts[2])]
                livingOn += [int(parts[3])]
                badkamerSP += [float(parts[5])]
                badkamerT += [float(parts[6])]
                badkamerOn += [int(parts[7])]
                bureauSP += [float(parts[9])]
                bureauT += [float(parts[10])]
                bureauOn += [int(parts[11])]
                nathanSP += [float(parts[13])]
                nathanT += [float(parts[14])]
                nathanOn += [int(parts[15])]
                reqP += [float(parts[17])]
                actP += [float(parts[18])]
                exteriorT += [float(parts[21])]
            lineNb += 1
    return np.array(times), np.array(livingSP), np.array(livingT), np.array(livingOn), np.array(badkamerSP), np.array(badkamerT), np.array(badkamerOn), np.array(bureauSP), np.array(bureauT), np.array(bureauOn), np.array(nathanSP), np.array(nathanT), np.array(nathanT), np.array(reqP), np.array(actP), np.array(exteriorT)


def calculateCoefficientsFromBestLog(directory):
    logs = getLogs(directory)
    for logFile in logs:
        if isValidLog(logFile):
            log = loadLog(logFile)
            return calculateCoefficientsFromLog(log)

def calculateCoefficientsFromLog(log):
    # living, badkamer, bureau, nathan
    h_loss = {}
    h = {}
    h_loss["living"] = calculateHeatLoss(log[10], log[0], log[2], log[11])
    h["living"] = calculateLinearHeatingCurve(log[0], log[1], log[2], log[11], h_loss["living"], [log[3], log[5], log[7]], [log[4], log[6], log[8]])
    h_loss["badkamer"] = calculateHeatLoss(log[10], log[0], log[4], log[11])
    h["badkamer"] = calculateLinearHeatingCurve(log[0], log[3], log[4], log[11], h_loss["badkamer"], [log[1], log[5], log[7]], [log[2], log[6], log[8]])
    h_loss["bureau"] = calculateHeatLoss(log[10], log[0], log[6], log[11])
    h["bureau"] = calculateLinearHeatingCurve(log[0], log[5], log[6], log[11], h_loss["bureau"], [log[1], log[3], log[7]], [log[2], log[4], log[8]])
    h_loss["kamer_nathan"] = calculateHeatLoss(log[10], log[0], log[8], log[11])
    h["kamer_nathan"] = calculateLinearHeatingCurve(log[0], log[7], log[8], log[11], h_loss["kamer_nathan"], [log[1], log[3], log[5]], [log[2], log[4], log[6]])
    return h, h_loss

def calculateSetpoint(tTime, targetTemperature, temperature, externalTemperature, h_loss, h):
    now = datetime.datetime.now()
    nowTime = now.hour * 3600 + now.hour * 60 + now.second
    targetTime = tTime
    if nowTime > tTime:
        targetTime += 24 * 3600
    # The temperature difference the system can have in the available time
    deltaT_in = targetTemperature - temperature
    deltaT_out = externalTemperature - temperature
    dT_in = deltaT_in * h
    dT_out = deltaT_out * h_loss
    deltaT = (dT_in + dT_out) * (targetTime - nowTime)
    spTemperature = targetTemperature - deltaT
    return spTemperature

def simulateFutureTemperature(tTime, targetTemperature, temperature, externalTemperature, h_loss, h, steps):
    now = datetime.datetime.now()
    nowTime = now.hour * 3600 + now.hour * 60 + now.second
    targetTime = tTime
    if nowTime > tTime:
        targetTime += 24 * 3600
    deltaTime = targetTime - nowTime
    stepSize = deltaTime / steps
    simTemperature = temperature
    for time in np.arange(0, deltaTime, stepSize):
        deltaT_out = externalTemperature - simTemperature
        dT_out = deltaT_out * h_loss
        T_loss = dT_out * stepSize
        deltaT_in = max(0, targetTemperature - simTemperature - T_loss)
        dT_in = deltaT_in * h
        T_heat = dT_in * stepSize
        simTemperature += T_heat
        if simTemperature > targetTemperature:
            return simTemperature
        simTemperature += T_loss
    return simTemperature