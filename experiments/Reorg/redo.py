import perlin_noise
import point
import csv

seed = 102602
xSize = 14
ySize = 14

points = []
fileContent = ""
BIT_LENGTH = 4
noisePoints = []
ZOOM_AMOUNT = 15
SEED_INCREMENT = 1
OCTAVES = 8
noise = None




def ReadFile(filePath):
    with open(filePath, 'r') as file:
        content = file.readlines()
    for i in content:
        point1 = point.Point(i.strip())
        points.append(point1)     



def GetNoise(x,y):
    return noise.noise((x,y))

def ChangeNoiseSeed(seed):
    global noise
    noise = perlin_noise.PerlinNoise(OCTAVES, seed)


def GetBinaryAtPoint(x,y):
    xyNoise = GetNoise(x/ZOOM_AMOUNT,y/ZOOM_AMOUNT)

    normalized = (xyNoise + 1) / 2
    
    max_val = (1 << BIT_LENGTH) - 1
    fitted_value = int(round(normalized * max_val))
    
    binary_formatted = format(fitted_value, f'0{BIT_LENGTH}b')
    return binary_formatted, fitted_value, xyNoise

def FillNoiseList():
    for y in range(ySize):
        for x in range(xSize):

            binary_Formatted, _, xyNoise = GetBinaryAtPoint(x,y)
            
            noisePoint = point.Point(binary_Formatted)
            noisePoint.SetXY(x,y)
            noisePoint.rawValue = xyNoise
            
            
            noisePoints.append(noisePoint)




def ReconstructText(string):
    """
    Reconstructs ASCII text from the reorganized points.
    Sorts points by their y-coordinate, then x-coordinate (row-major order),
    concatenates their binaryValue strings, and converts to ASCII characters.
    """
    
    sentence = "".join(string)
    # Convert binary string to ASCII (assuming 8-bit characters)
    print(sentence)
    ascii_text = ''
    for i in range(0, len(sentence), 8):
        byte = sentence[i:i+8]
        if len(byte) == 8:
            ascii_text += chr(int(byte, 2))
    
    return ascii_text


    
    
    
    
def Generate():
# ChangeNoiseSeed(SCRAMBLER_SEED)
    i = 0
    FillNoiseList()
    
    noisePoints.sort(key=lambda x : x.binaryValue)
    for y in range(ySize):
        for x in range(xSize):
            noisePoint = GetNoise(x/ZOOM_AMOUNT,y/ZOOM_AMOUNT)
            points[i].SetIdentifier(noisePoint)
            noisePoints[i].SetIdentifier(noisePoint)
            i += 1      


    ident_to_index = {npt.identifier: idx for idx, npt in enumerate(noisePoints)} # chat gpt

    finalList = []
    for i in range(len(points)):
        finalList.append("")
        
    for i in points:
        if(i.identifier in ident_to_index):
            finalList[ident_to_index[i.identifier]] = i.binaryValue

    # print(finalList)
    return finalList
    # points.sort(key= lambda x : x.identifier)


    

ReadFile("experiments/Reorg/main.txt")
     
ChangeNoiseSeed(seed)
finalList = Generate()
print("RECONSTRUCTED TEXT ==")
print(ReconstructText(finalList))
# DisplayGrayscalePlots()