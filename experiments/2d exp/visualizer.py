import numpy as np
import matplotlib.pyplot as plt
import perlin_noise

# === SETTINGS ===
width, height = 128, 128
octaves = 6
seed = 25565

noiseArray = []

def resetSeeds():
    global noise, noise1, noise2, noise3, noise4, noise5
    noise = perlin_noise.PerlinNoise(1, seed)
    noise5  = perlin_noise.PerlinNoise(2, seed)
    noise1 = perlin_noise.PerlinNoise(4, seed)
    noise2 = perlin_noise.PerlinNoise(6,seed)
    noise3 = perlin_noise.PerlinNoise(8,seed)
    noise4 = perlin_noise.PerlinNoise(10,seed)


def layerNoise(x,y):
    return noise1.noise((x,y)) + noise2.noise((x,y)) + noise3.noise((x,y)) + noise4.noise((x,y)) + noise5.noise((x,y)) + noise.noise((x,y))







def get_noise(x, y):
    # Use integer indices
    return layerNoise(x/100,y/100)

resetSeeds()
# === GENERATE NOISE GRID ===
image = np.zeros((height, width))

for y in range(height):
    for x in range(width):
        val = get_noise(x, y)
        image[y][x] = (val + 1) / 2  # Normalize from [-1,1] to [0,1]

# === DISPLAY ===
plt.imshow(image, cmap='gray', interpolation='nearest')
plt.title(f"Perlin Noise (octaves={octaves}, seed={seed})")
plt.axis('off')
plt.show()