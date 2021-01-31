#######################################
# 2.1 level format to 1.9 level format converter
# for the truest dashers
# *probably not finished!*
# by zmx
######################################


# these all deal with the level string

from typing import List, Dict
import objCharts
from commonTypes import LevelString, RobDict
from functools import reduce

'''
what follows will be an explanation of the color header format in 1.9 and below
(i assume you know the level header format)

kS33 -> col 1
kS34 -> col 2
kS35 -> col 3
kS36 -> col 4

kS29 -> BG -> 1000
kS30 -> Ground -> 1001
kS31 -> L -> 1002
kS37 -> 3DL -> 1003
kS32 -> Obj -> 1004

next is the 2.1 format
the third number provided is how 1.9 colors convert to 2.1 (and string)

kS38,color|color|color|color|,
colors are in the format
1_r_2_g_3_b_4_-1_5_blending_6_id...
note that 1.9 is nice about things with extra values
and usually just chops them off

and the color format itself is the same as 1.9's
'''


def convertColorHeader(colorHeader: str) -> str:
    '''
    converts color header from the 2.1 format to 1.9 and below's format
    - expects string in form kS38,|..|..|
    - returns string in form kS29,..,kS30,...
    '''

    colorConversionSheet = objCharts.headerColorID

    # colors to array
    actualValue = colorHeader.split(',')[-1]
    colors = actualValue.split('|')

    headerArray = []

    for color in colors[:-1]:
        colorDict = parseKeyVarArray(color, '_')
        try:
            headerColorIndex = colorConversionSheet[int(colorDict['6'])]
            header = f'{headerColorIndex},{color}'
            headerArray.append(header)
            # print(f'Header Convert: {color} -> {header}')
        except BaseException:
            pass

    finalHeader = ','.join(headerArray)
    return finalHeader

def convertColorHeaderPointEight(header: str) -> RobDict:
    """
    takes a 1.9 color header and converts it to a 1.6 equivalent
    """
    header_name, header_value = header.split(',')

    correct_header = next(
        (x for x in objCharts.point_six_headers if x["point_nine_equivalent"] == header_name), None)
    if not correct_header:
        return {}

    color_dict = parseKeyVarArray(header_value, '_')

    color_string = {
        correct_header['color_keys'].r: color_dict["1"],
        correct_header['color_keys'].g: color_dict["2"],
        correct_header['color_keys'].b: color_dict["3"]
    }

    if 'player_color_key' in correct_header and "4" in color_dict:
        color_string[correct_header['player_color_key']] = color_dict["4"]

    if 'blend_key' in correct_header and "5" in color_dict:
        color_string[correct_header['blend_key']] = color_dict["5"]

    return color_string

def convertColors(cols: str) -> str:
    '''
    converts 2.1 objects to their 1.9 forms
    - expects string like 1,32,2,21;1,43,2,33;
    - returns string in the exact same format
    '''

    objectArray = cols.split(';')
    newObject = []

    # ends with a ;
    for objec in objectArray[:-1]:
        if objec.startswith('1,899'):
            try:
                newObject.append(convertColTrigger(objec))
            except BaseException:
                newObject.append(objec)
        elif ",21," in objec or ",22," in objec:
            try:
                newObj = convObjID(objec)
                newObject.append(convertColObj(newObj))
            except BaseException:
                newObj = convObjID(objec)
                newObject.append(newObj)
        else:
            newObj = convObjID(objec)
            newObject.append(newObj)

    # blank space to add ; to end
    newObject.append('')
    return ';'.join(newObject)


'''
i'll explain this too

color triggers retain much of the values set except for
id (1) -> 899
color id is now index 23

1000 -> bg -> 29
1001 -> g -> 30
1002 -> l -> 104
1004 -> obj -> 105
1003 -> 3dl -> 744
1 -> col 1 -> 221
2 -> col 2 -> 717
3 -> col 3 -> 718
4 -> col 4 -> 743
'''


def convertColTrigger(string: str) -> str:
    '''
    converts 2.1 color triggers to 1.9 color triggers
    - expects string in form 1,899,2,3,3,2,23,4
    - returns string in form 1,743,2,3,3,2
    '''
    colorConversionSheet = objCharts.colorTrigObj

    parseCol = parseKeyVarArray(string, ',')
    try:
        newCol = colorConversionSheet[int(parseCol['23'])]
    except BaseException:
        # rob is lazy, made this col1 why rob
        newCol = colorConversionSheet[1]
    newObjString = string.replace("1,899,", f"1,{newCol},")
    # print(f'Color Convert: {string} -> {newObjString}')
    return newObjString


'''
robtop also messe with object
2.1 -> 1.9
index 21 -> index 19
index 22 usually overrides index 19
index 21 was used for line color, so we do that too
1005 -> 1
1006 -> 2
1007 -> 5
1 -> 3
2 -> 4
3 -> 6
4 -> 7
'''


def convertColObj(string: str) -> str:
    '''
    converts obj colors to their 1.9 forms
    - expects string in format 1,2,2,5,3,3,22,4
    - returns string in format 1,2,2,5,3,3,19,7
    '''
    objConversionSheet = objCharts.objColors

    parseCol = parseKeyVarArray(string, ',')
    try:
        newCol = objConversionSheet[int(parseCol['22'])]
        newObjString = string.replace(f',22,{parseCol["22"]}', f',19,{newCol}')
    except BaseException:
        newCol = objConversionSheet[int(parseCol['21'])]
        newObjString = string.replace(f',21,{parseCol["21"]}', f',19,{newCol}')
    # print(f'Color Obj Convert: {string} -> {newObjString}')
    return newObjString

# roberti also mess with object ids cause .. why not?
# last 1.9 object is 744 so we'll use that as a base point for "illegal
# objects"


def convObjID(string: str) -> str:
    '''
    converts obj ids to their 1.9 forms
    - expects string in format 1,667,2,34,3,54
    - returns string in format 1,1338,2,34,3,54
    '''
    objConversionSheet = objCharts.objIds

    if convClubstep:  # don't convert clubstep blocks by default
        objConversionSheet = {
            **objConversionSheet,
            **objCharts.clubstepObjConv}
    if convGlow:
        objConversionSheet = {**objConversionSheet, **objCharts.glowObj}
    if convColor:
        objConversionSheet = {**objConversionSheet,
                              **objCharts.colorDefaultBlockObj}

    parseObj = parseKeyVarArray(string, ',')
    try:
        newObj = objConversionSheet[int(parseObj['1'])]
        newObjString = string.replace(f'1,{parseObj["1"]}', f'1,{newObj}')
        # print(f'Obj Convert: {string} -> {newObjString}')
        return newObjString
    except BaseException:
        # nothing to be done
        if int(parseObj['1']) > max_objects and int(parseObj['1']
                                            ) not in illegalObj:
            # 744 is the last object in 1.9
            illegalObj.append(int(parseObj['1']))
            # print(f'Illegal object found! ID: {parseObj["1"]}')

        if remove_invalid_objects and int(parseObj['1']) > max_objects:
            return ""

        return string


illegalObj: List[int] = []
convClubstep: bool = False
convGlow: bool = False
convColor: bool = False
max_objects = 744
remove_invalid_objects = True

def parseKeyVarArray(string: str, splitter: str) -> RobDict:
    """
    parses the special robtop style array
    - expects string like 1,53,2,65,3,14.3
    - returns dict like {'1': '53', '2': '65', '3': '14.3'}
    """

    arrayFirstSplit: List[str] = string.split(splitter)

    finalDict: Dict[str, str] = {}

    for index, value in enumerate(arrayFirstSplit):
        # if odd then we on index
        if index % 2 == 0:
            finalDict[arrayFirstSplit[index]] = arrayFirstSplit[index + 1]

    return RobDict(finalDict)

def convLevelStringPointEight(string: LevelString) -> LevelString:
    """
    Converts a 1.9 level string to a >1.8 format
    """

    levelObjects = string.decode().split(';')
    levelHeader = levelObjects.pop(0)

    splitHeader = parseKeyVarArray(levelHeader, ",")
    if "kS38" in splitHeader:
        splitHeader.update(parseKeyVarArray(convertColorHeader(f"kS38,{splitHeader['kS38']}"), ","))
        del splitHeader["kS38"]

    if 'kS29' in splitHeader:
        for index, header in splitHeader.copy().items():
            if (index.startswith("kS")):
                if int(index[2:]) >= 37:
                    continue
                splitHeader.update(convertColorHeaderPointEight(f"{index},{header}"))
                del splitHeader[index]

    header_list = list(reduce(lambda x, y: x + y, splitHeader.items()))

    newHeader = ','.join(header_list)

    newColors = convertColors(';'.join(levelObjects))

    return LevelString((newHeader + ';' + newColors).encode())

def convLevelString(string: LevelString) -> LevelString:
    '''
    converts a 2.1 level string to 1.9 format
    - expects level string
    - returns level string
    '''

    levelObjects = string.decode().split(';')
    levelHeader = levelObjects.pop(0)

    splitHeader = levelHeader.split(',')
    if 'kS38' in levelHeader:
        splitHeader[1] = convertColorHeader(','.join(splitHeader[:2]))
        splitHeader.pop(0)
    newHeader = ','.join(splitHeader)

    newColors = convertColors(';'.join(levelObjects))

    return LevelString((newHeader + ';' + newColors).encode())
    # print(f'Header Conv: {levelHeader} -> {newHeader}')


def illegalObjInfo(illegalObjs: List[int]) -> Dict[int, str]:
    '''
    parses the illegal obj variable to have basic block names
    only the ones used often should be listed here
    others will just say unknown
    '''
    objConversionSheet = objCharts.objNames

    detailIllegalObj: Dict[int, str] = {}

    for illegalObj in sorted(illegalObjs):
        detailIllegalObj[illegalObj] = objConversionSheet.get(
            illegalObj, "unknown")

    return detailIllegalObj


if __name__ == "__main__":
    import sys
    filename = sys.argv[1]

    point_six = False
    if (len(sys.argv) > 2):
        point_six = True
        max_objects = 196

        print("1.6 conversion enabled!")

    with open(filename + '.txt', 'rb') as levelFile:
        if (point_six):
            level_string = convLevelStringPointEight(levelFile.read())
        else:
            level_string = convLevelString(levelFile.read())

        illegalObjs: Dict[int, str] = illegalObjInfo(illegalObj)

        for objID, name in illegalObjs.items():
            print(f"Illegal object: {objID} ({name})")

        with open(filename + '-conv.txt', 'wb') as convFile:
            convFile.write(level_string)

    print('conversion done!')
