import numpy as np

file = r"01110111011010000110000101110100011100110010000001110101011100000010000001100100011010010111000001110011011010000110100101110100"

seed = 59678
OFFSET_SIZE = 1024 # how far each seed is from the base
BIT_LENGTH = 64 # how many bits to try and match
NUMBER_OF_SEEDS = 512 # number of entrys in the roster MUST BE divisble by 2






def encode():
    rng = np.random.Generator(np.random.PCG64(seed))
    i = 0
    chunkIndex = 0
    tape = []
    while(True):
        if(i > BIT_LENGTH * 4):
            break
        if(chunkIndex >= len(file)):
            break

        num = rng.random()
        scaled = int(abs(num) * (10 ** BIT_LENGTH))
        chunkInNoise = scaled % (10 ** BIT_LENGTH)
        
        bitNumber = chunkInNoise % (2**BIT_LENGTH)
        binaryBits = bin(bitNumber)[2:].zfill(BIT_LENGTH)
        
        if(file[chunkIndex:chunkIndex+BIT_LENGTH] == binaryBits):
            # print(f"chunkInNoise: '{chunkInNoise}' -> binary: {binaryBits}")
            tape.append(True)
            chunkIndex += BIT_LENGTH
        else:
            tape.append(False)
        i += 1
    return tape


# any score below 1 is compression anything above is inflation
def ScoreTape(tape):
    skips = 0
    for i in tape:
        if(i is False):
            skips += 1
    return ((skips + (len(file) / BIT_LENGTH))) / len(file) # number of skips divided by the number of matches needed to compress the tape divided by the width of the tape so 80 skips + (128 needed bytes divided by 2) so 80+64/128 = 1.125 inflation
            

bestSeed = 0
tape = encode()
bestSeedsScore = ScoreTape(tape)

i = 0
while True:
    seed += OFFSET_SIZE
    score = ScoreTape(encode())
    if(score < bestSeedsScore):
        print(f"better ratio acheived at {i}th iteration")
        bestSeed = seed
        bestSeedsScore = score
        print(bestSeed)
        print(bestSeedsScore)
    if(score < 1.0):
        print("COMPRESSION ACHEIVED!!!!!!")
        print(f"TOOK {i} ITERAIONS FROM STARTING SEED AT {OFFSET_SIZE} offsets")
        
        bestSeed = seed
        bestSeedsScore = score
        print(score)
        break
    i += 1   



# print(f"COMPRESSION SEED FOR THIS IS {bestSeed}")
# seed = 1047838
# finalTape = encode()

# for i in finalTape:
#     if(i is True):
#         print("1", end="")
#     else:
#         print("0", end="")

# print(len(finalTape))            
        
        
        







# orignalSeed = seed
# startingSeeds = []
# winners = []
# winnersDict = {}
# finalTape = []
# for i in range(NUMBER_OF_SEEDS//4):
#     if(len(startingSeeds) == 0):
#         for x in range(NUMBER_OF_SEEDS):
#             seed += OFFSET_SIZE
#             startingSeeds.append(seed)        
#     if(len(startingSeeds) == 1):
#         break   
            
        
    
#     for z in range(0,len(startingSeeds),2):
#         seed = startingSeeds[z]
#         tape1 = encode()
#         score1 = ScoreTape(tape1)
        
#         seed = startingSeeds[z + 1]
#         tape2 = encode()
#         score2 = ScoreTape(tape2)
        
#         print(f"score 1 {score1}, score 2 {score2}")
        
#         if(score1 <= score2):
#             winners.append(startingSeeds[z])
#             winnersDict[score1] = startingSeeds[z]
#         else:
#             winners.append(startingSeeds[z + 1])
#             winnersDict[score2] = startingSeeds[z + 1]
            
#     startingSeeds = winners.copy()
#     winners.clear()

