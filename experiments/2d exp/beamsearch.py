import hashlib

seed = 2789854
width = 32
height = 32
beamWidth = 5
bitMaxSearchLength = 17 # how many variations it will look for so 1,2,3,4,5,6,7,8 bit lengths
bitMinSearchLength = 1 # so if its 5 min and 8 max it will look for 5,6,7,8
inputData = r"01110111011010000110000101110100011100110010000001110101011100000010000001100100011010010111000001110011011010000110100101110100"

bitlengths = []

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class BitData:
    def __init__(self, pos, data):
        self.pos = pos
        self.data = data

class BitLength:
    def __init__(self, length):
        self.length = length
        self.data = []
    
    def addBit(self, vect2):
        self.data.append(vect2)

    def printListLength(self):
        print(len(self.data))

    def getListLength(self):
        return len(self.data)


def getNoise(x,y):
    inputStr = f"{seed}:{x}:{y}"
    
    hashObj = hashlib.sha256(inputStr.encode())
    hashHex = hashObj.hexdigest()
    
    hashInt = int(hashHex[:8], 16)
    
    return hashInt



def getBinaryNoise(x,y,bitLength):
    hashInt = getNoise(x,y)
    return format(hashInt % (2**bitLength), f'0{bitLength}b')




# make a static anayliss of the perlin grid based on widht and height and pick the best nodes
# that will offer the highest reward then beam search to it



def getAllStringCombos():
    currentBits = []
    for length in range(bitMinSearchLength, bitMaxSearchLength):
        currentLength = BitLength(length)
        for z in range(0,len(inputData) - length + 1):
            currentLength.addBit(inputData[z:z+length])
        currentBits.append(currentLength)

    
    for i in range(len(currentBits)):
        currentBits[i].data = list(set(currentBits[i].data))
    return currentBits






def analyze():
    currentBits = getAllStringCombos()    
    i = 0
    goodBits = []
    for length in range(bitMinSearchLength, bitMaxSearchLength):
        currentGoodBits = BitLength(length)
        for y in range(height):
            for x in range(width):
                num = str(getBinaryNoise(x,y,length))
                
                if(num in currentBits[i].data):
                    print(f"{num} and {x,y},,, {currentBits[i].data.index(num)}")
                    currentGoodBits.addBit(BitData(Vector2(x,y), num))
        i += 1
        goodBits.append(currentGoodBits)
    
    return goodBits
                
                







def main():
    global coords
    coords = analyze()
    print("done")
main()





def debug_hash_noise():
    """Debug what patterns the hash noise is actually generating"""
    
    hash_patterns = set()
    pattern_counts = {}
    
    for y in range(height):
        for x in range(width):
            pattern = getBinaryNoise(x, y, 8)  # 8-bit patterns
            hash_patterns.add(pattern)
            
            if pattern in pattern_counts:
                pattern_counts[pattern] += 1
            else:
                pattern_counts[pattern] = 1
    
    print(f"Hash noise generated {len(hash_patterns)} unique 8-bit patterns out of 256 possible")
    
    # Show distribution
    sorted_counts = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
    print("Top 10 most common patterns:")
    for pattern, count in sorted_counts[:10]:
        print(f"  {pattern}: {count} times")
    
    # Check if we're getting all 256 possible 8-bit patterns
    all_possible = set(format(i, '08b') for i in range(256))  # FIXED: 8-bit patterns
    missing = all_possible - hash_patterns
    print(f"Missing 8-bit patterns: {len(missing)} out of 256")
    
    return hash_patterns

def debug_input_patterns():
    """Debug what patterns are in your input data"""
    currentBits = getAllStringCombos()
    input_patterns = set(currentBits[0].data)  # This is 8-bit data
    
    print(f"Input has {len(input_patterns)} unique 8-bit patterns out of 256 possible")  # FIXED
    print(f"Sample input patterns: {sorted(list(input_patterns))[:10]}")
    
    return input_patterns

# Run both debugs
print("=== HASH NOISE DEBUG ===")
hash_patterns = debug_hash_noise()

print("\n=== INPUT DATA DEBUG ===")
input_patterns = debug_input_patterns()

print("\n=== OVERLAP ANALYSIS ===")
overlap = hash_patterns & input_patterns
print(f"Overlapping patterns: {len(overlap)} out of {len(input_patterns)} input patterns")
print(f"Overlap percentage: {len(overlap)/len(input_patterns)*100:.1f}%")
print(f"Overlapping patterns: {sorted(overlap)}")

# This should tell us if the issue is:
# 1. Hash noise covering all 32 patterns (shouldn't happen)
# 2. Input data having too many patterns
# 3. Some other bug



import matplotlib.pyplot as plt
import numpy as np

def plot_all_matches_and_noise(coords, grid_size, pixel_size):
    """
    Creates a plot showing all bit length matches side-by-side plus original noise.
    """
    width, height = grid_size
    num_bit_lengths = len(coords)
    
    # Create subplots: one for each bit length + one for noise
    fig, axes = plt.subplots(1, num_bit_lengths + 1, figsize=((num_bit_lengths + 1) * width * pixel_size / 100, height * pixel_size / 100))
    
    # Plot matches for each bit length
    for i, bit_length_data in enumerate(coords):
        # Create matches grid for this bit length
        matches_grid = np.zeros((height, width))
        
        # Extract coordinates for this bit length
        for match in bit_length_data.data:
            x, y = match.pos.x, match.pos.y
            if 0 <= x < width and 0 <= y < height:
                matches_grid[y, x] = 1
        
        # Plot this bit length's matches
        current_bit_length = bitMinSearchLength + i
        im = axes[i].imshow(matches_grid, cmap="gray_r", interpolation="nearest", vmin=0, vmax=1)
        axes[i].set_title(f"{current_bit_length}-bit Matches\n({len(bit_length_data.data)} total)")
        axes[i].axis("off")
        
        # Add colorbar for each subplot
        plt.colorbar(im, ax=axes[i], label="Matches", shrink=0.8)
    
    # Create and plot original noise grid
    noise_grid = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            noise_val = getNoise(x, y)  # Get raw hash value
            noise_grid[y, x] = noise_val
    
    # Plot noise in the last subplot
    noise_im = axes[-1].imshow(noise_grid, cmap="viridis", interpolation="nearest")
    axes[-1].set_title(f"Original Noise\n({width}x{height} grid)")
    axes[-1].axis("off")
    plt.colorbar(noise_im, ax=axes[-1], label="Noise Values", shrink=0.8)
    
    plt.tight_layout()
    plt.suptitle(f"Bit Pattern Matches ({bitMinSearchLength}-{bitMaxSearchLength-1} bits) vs Original Noise", y=1.02)
    plt.show()

# Usage after running your analysis:
grid_size = (width, height)
pixel_size = 15  # Smaller since we have multiple subplots

print("=== PLOTTING ALL MATCHES ===")
# Show binary matches (on/off)
plot_all_matches_and_noise(coords, grid_size, pixel_size)

# Print summary statistics
print("\n=== MATCH SUMMARY ===")
for i, bit_length_data in enumerate(coords):
    current_bit_length = bitMinSearchLength + i
    unique_positions = len(set((match.pos.x, match.pos.y) for match in bit_length_data.data))
    total_matches = len(bit_length_data.data)
    print(f"{current_bit_length}-bit: {total_matches} total matches, {unique_positions} unique positions")

