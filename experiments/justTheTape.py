import numpy as np
import zstd
from pathlib import Path
import perlin_noise
file = r""

seed = 345
OFFSET_SIZE = 1 # how far each seed is from the base
BIT_LENGTH = 4 # how many bits to try and match



rawData = []
bytesObj = Path("ogUNcomp.txt").read_bytes()
print()

for i in bytesObj:
    file += bin(i)[2:].zfill(8)
    
    
# with open("bin.txt", "wb") as writeFile:
#     for i in range(0,len(file), 8):
#         byteChunk = file[i:i+8]
#         if(len(byteChunk) == 8):
#             bytevalue = int(byteChunk,2)
#             writeFile.write(bytes([bytevalue]))
    

def encode():
    rng = np.random.Generator(np.random.PCG64(seed))
    i = 0
    chunkIndex = 0
    tape = []
    while(True):
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
            # print(f"true  {chunkIndex} out of {len(file)}")
            chunkIndex += BIT_LENGTH
        else: 
            tape.append(False)
        i += 1
    return tape



# any score below 1 is compression anything above is inflation
def ScoreTape(tape):
    zero_runs = putTogetherTapeFromList(tape).split("1")
    run_lengths = {}
    
    for run in zero_runs:
        if run == '':  # Empty = consecutive matches
            length = 0  # Special "match" symbol
        else:
            length = len(run)  # Run length
        
        run_lengths[length] = run_lengths.get(length, 0) + 1

    
    uniquePatterns = 0
    repeatedPatterns = 0
    for value in run_lengths.values():
        if(value > 1):
            repeatedPatterns += value
        else:
            uniquePatterns += value
    
    if(repeatedPatterns == 0):
        repeatedPatterns = 1
    return (uniquePatterns / repeatedPatterns) / len(run_lengths)
    
    
  
        
    
def putTogetherTapeFromList(tape):
    putTogetherTape = ""
    for i in tape:
        if(i is True):
            putTogetherTape += "1"
        else:
            putTogetherTape += "0"
    
    return putTogetherTape



bestSeed = 0
tape = encode()
bestSeedsScore = ScoreTape(tape)
print("Finished starter tape")
print(len(tape))

i = 0
while True:
    seed += OFFSET_SIZE
    tape = encode()
    score = ScoreTape(tape)
    # print(f"{seed} had a score of {score}")
    if(score < bestSeedsScore):
        print(f"better ratio acheived at {i}th iteration with the seed {seed} and a score of {score * 1000} and a len of {len(tape)}")
        bestSeed = seed
        bestSeedsScore = score
    i += 1   



seed = 383  # Use the same seed
finalTape = encode()  # Make sure encode takes seed parameter
finalTapeString = "".join("1" if bit else "0" for bit in finalTape)
print(len(finalTapeString))
bytesString = int(finalTapeString, 2).to_bytes((len(finalTapeString) + 7) // 8, 'big') # stack overflow https://stackoverflow.com/questions/32675679/convert-binary-string-to-bytearray-in-python-3




result = zstd.compress(bytesString, 22, 4)

with open("compressed.zstd", "wb") as file:
    file.write(result)

