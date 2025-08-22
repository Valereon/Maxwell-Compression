import perlin_noise



seed = 30796



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


# loop over lenght of file


def binary_to_ascii(binary_string):
    ascii_string = ""
    for i in range(0, len(binary_string), 8):
        byte = binary_string[i:i+8]
        if len(byte) == 8:
            ascii_string += chr(int(byte, 2))
    return ascii_string




def decode(file):
    decodedString = ""
    skips = 0
    for z in range(len(file)):
        if(file[z] == "0"):
            skips += 1
            continue
        else:
            num = str(layerNoise(z/100))
            if(num.__contains__("-")):
                chunkInNoise = num[3:5]
            else:
                chunkInNoise = num[2:4]

            binary_4bit = format(int(chunkInNoise) % 4, '02b').zfill(2)
            print(f"chunkInNoise: '{chunkInNoise}' -> binary: {binary_4bit}")
            decodedString += binary_4bit
    print(decodedString)
    print(skips)
    return decodedString
    




finalString = ""
resetSeeds()
with open("tape.txt", "r") as file:
    decodedString = decode(file.readline())
    print(binary_to_ascii(decodedString))






