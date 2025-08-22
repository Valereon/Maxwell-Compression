import perlin_noise
import random

file = r"01110111011010000110000101110100011100110010000001110101011100000010000001100100011010010111000001110011011010000110100101110100"

seed = 30796
numberOfOffsets = 1

def resetSeeds():
    global noise, noise1, noise2, noise3, noise4, noise5
    noise = perlin_noise.PerlinNoise(1, seed)
    noise5  = perlin_noise.PerlinNoise(2, seed)
    noise1 = perlin_noise.PerlinNoise(4, seed)
    noise2 = perlin_noise.PerlinNoise(6,seed)
    noise3 = perlin_noise.PerlinNoise(8,seed)
    noise4 = perlin_noise.PerlinNoise(10,seed)


def layerNoise(pos):
    return noise1.noise(pos) + noise2.noise(pos) + noise3.noise(pos) + noise4.noise(pos) + noise5.noise(pos) + noise.noise(pos)

resetSeeds()
def encode():
    i = 0
    chunkIndex = 0
    tape = []
    while(True):
        if(chunkIndex >= len(file)):
            break

        num = str(layerNoise(i/100))

        if(num.__contains__("-")):
            chunkInNoise = num[3:5]
        else:
            chunkInNoise = num[2:4]
                
        binary_4bit = format(int(chunkInNoise) % 4, '02b').zfill(2)
        if(file[chunkIndex:chunkIndex+2] == binary_4bit):
            print(f"chunkInNoise: '{chunkInNoise}' -> binary: {binary_4bit}")
            tape.append(True)
            chunkIndex += 2
        else:
            tape.append(False)
        i += 1
    return tape




smallestTape = encode()
# smallestTapeSeed = 0
# for i in range(numberOfOffsets):
#     seed = random.randint(0,100000)
#     resetSeeds()
#     tape = encode()
#     if(len(tape) < len(smallestTape)):
#         print("IT HAPENEDNIENFGPINEFPINWPIFNWEPIFNPIOWENFPINEWFPINWEFPINPIEWFNPIEWNFPINEFPIN")
#         smallestTape = tape
#         smallestTapeSeed = seed
#     print(f"looped {i}")


finalString = ""
with open("tape.txt", "w") as file:
    for i in range(len(smallestTape)):
        if(smallestTape[i] == True):
            finalString += "1"
        else:
            finalString += "0"

    file.write(finalString)


# print(smallestTapeSeed)