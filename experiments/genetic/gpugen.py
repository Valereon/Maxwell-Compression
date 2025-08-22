import numpy as np
from numba import cuda, jit
import math

file = r"01110111011010000110000101110100011100110010000001110101011100000010000001100100011010010111000001110011011010000110100101110100"

seed = 5767678
OFFSET_SIZE = 128 # how far each seed is from the base
BIT_LENGTH = 64 # how many bits to try and match
NUMBER_OF_SEEDS = 512 # number of entrys in the roster MUST BE divisble by 2
BATCH_SIZE = 4096 # number of seeds to process in parallel on GPU




def GetNoise(pos, current_seed):
    rng = np.random.Generator(np.random.PCG64(current_seed * pos))
    return rng.random()



def encode(current_seed=None):
    if current_seed is None:
        current_seed = seed
    
    i = 0
    chunkIndex = 0
    tape = []
    while(True):
        if(chunkIndex >= len(file)):
            break

        num = GetNoise(i, current_seed)

        num = num * (10 ** BIT_LENGTH) # make it not a decimal
        num = str(abs(num))
        num = num.replace(".", "")
        chunkInNoise = num[0:BIT_LENGTH] # i know this is overkill cause for 2 bits itll be 0-99 but it gets formatted so whatever        
        
        chunkInNoise = chunkInNoise.zfill(BIT_LENGTH)
        chunkInNoise = int(chunkInNoise)
        
        binaryBits = format(chunkInNoise % (2**BIT_LENGTH), f'0{BIT_LENGTH}b')
        
        if(file[chunkIndex:chunkIndex+2] == binaryBits):
            # print(f"chunkInNoise: '{chunkInNoise}' -> binary: {binaryBits}")
            tape.append(True)
            chunkIndex += 2
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
    return (skips + len(tape) / BIT_LENGTH) / len(tape) # number of skips divided by the number of matches needed to compress the tape divided by the width of the tape so 80 skips + (128 needed bytes divided by 2) so 80+64/128 = 1.125 inflation

@cuda.jit
def encode_batch_gpu(seeds, file_data, file_length, bit_length, results, scores):
    # Get thread ID
    idx = cuda.grid(1)
    
    if idx >= len(seeds):
        return
    
    current_seed = seeds[idx]
    i = 0
    chunkIndex = 0
    tape_index = 0
    skips = 0
    
    while chunkIndex < file_length:
        # PCG64-like random number generation (simplified for GPU)
        state = current_seed * i
        state = ((state * 1664525) + 1013904223) % (2**32)
        num = state / (2**32)  # Convert to 0-1 range
        
        num = num * (10 ** bit_length)
        num = abs(num)
        
        # Extract digits (simplified string operations for GPU)
        temp = int(num)
        chunkInNoise = temp % (10 ** bit_length)
        chunkInNoise = chunkInNoise % (2 ** bit_length)
        
        # Convert to binary representation
        match = True
        for bit in range(bit_length):
            if chunkIndex + bit >= file_length:
                match = False
                break
            file_bit = file_data[chunkIndex + bit] - ord('0')  # Convert char to int
            noise_bit = (chunkInNoise >> (bit_length - 1 - bit)) & 1
            if file_bit != noise_bit:
                match = False
                break
        
        if match and chunkIndex + bit_length <= file_length:
            results[idx * 1000 + tape_index] = 1  # True
            chunkIndex += bit_length
        else:
            results[idx * 1000 + tape_index] = 0  # False
            skips += 1
        
        tape_index += 1
        i += 1
        
        if tape_index >= 1000:  # Prevent overflow
            break
    
    # Calculate score
    total_tape_length = tape_index
    if total_tape_length > 0:
        scores[idx] = (skips + total_tape_length / bit_length) / total_tape_length
    else:
        scores[idx] = 999.0  # Invalid score

def process_seeds_gpu(seeds_list):
    # Convert file to array for GPU processing
    file_array = np.array([ord(c) for c in file], dtype=np.uint8)
    
    # Prepare GPU arrays
    seeds_gpu = cuda.to_device(np.array(seeds_list, dtype=np.int64))
    file_gpu = cuda.to_device(file_array)
    results_gpu = cuda.device_array((len(seeds_list) * 1000,), dtype=np.int32)
    scores_gpu = cuda.device_array(len(seeds_list), dtype=np.float32)
    
    # Configure GPU execution
    threads_per_block = 128
    blocks_per_grid = (len(seeds_list) + threads_per_block - 1) // threads_per_block
    
    # Launch kernel
    encode_batch_gpu[blocks_per_grid, threads_per_block](
        seeds_gpu, file_gpu, len(file), BIT_LENGTH, results_gpu, scores_gpu
    )
    
    # Copy results back
    scores = scores_gpu.copy_to_host()
    results = results_gpu.copy_to_host()
    
    return scores, results
            


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


bestSeed = 0
bestSeedsScore = 10
finalTape = []

i = 0
current_seed = seed
while True:
    # Create batch of seeds to test
    seeds_to_test = []
    for batch_idx in range(BATCH_SIZE):
        current_seed += OFFSET_SIZE
        seeds_to_test.append(current_seed)
    
    # Process batch on GPU
    scores, results = process_seeds_gpu(seeds_to_test)
    
    # Check each score
    for batch_idx, score in enumerate(scores):
        if(score < bestSeedsScore):
            print(f"better ratio achieved at {i + batch_idx}th iteration")
            bestSeed = seeds_to_test[batch_idx]
            bestSeedsScore = score
            print(bestSeedsScore)
            print(bestSeed)
            # Reconstruct tape from results for this seed
            tape_start = batch_idx * 1000
            finalTape = [bool(results[tape_start + j]) for j in range(1000) if results[tape_start + j] != -1]
        if(score < 1.0):
            print("COMPRESSION ACHIEVED!!!!!!")
            print(f"TOOK {i + batch_idx} ITERATIONS FROM STARTING SEED AT {OFFSET_SIZE} offsets")
            
            bestSeed = seeds_to_test[batch_idx]
            bestSeedsScore = score
            # Reconstruct tape from results for this seed
            tape_start = batch_idx * 1000
            finalTape = [bool(results[tape_start + j]) for j in range(1000) if results[tape_start + j] != -1]
            print(score)
            break
    
    if bestSeedsScore < 1.0:
        break
        
    i += BATCH_SIZE   



print(f"COMPRESSION SEED FOR THIS IS {bestSeed}")

for i in finalTape:
    if(i is True):
        print("1")
    else:
        print("0")

print(len(finalTape))            
        
        
        


