import perlin_noise
import point
import matplotlib.pyplot as plt  # Added for plotting
import numpy as np  # Added for array handling
import math
seed = 0
SCRAMBLER_SEED = 0

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
    content = content[0]
    binaryString = ""
    for i in range(0,len(content), BIT_LENGTH):
        point1 = point.Point(content[i:i+BIT_LENGTH])
        binaryString += content[i:i+BIT_LENGTH]
        points.append(point1)     
    print(binaryString)


def GetNoise(x,y):
    return noise.noise((x,y))

def ChangeNoiseSeed(seed):
    global noise
    noise = perlin_noise.PerlinNoise(OCTAVES, seed)


def GetBinaryAtPoint(x,y):
    xyNoise = GetNoise(x/ZOOM_AMOUNT,y/ZOOM_AMOUNT)
    
    if(str(xyNoise).__contains__("-")):
        xyNoise = int(str(xyNoise)[3:3+BIT_LENGTH])
    else:
        xyNoise = int(str(xyNoise)[2:2+BIT_LENGTH])
    
    fitted_value = xyNoise % (1 << BIT_LENGTH)
    
    binary_formatted = format(fitted_value, f'0{BIT_LENGTH}b')
    
    return binary_formatted, xyNoise, xyNoise

def FillNoiseList():
    for y in range(ySize):
        for x in range(xSize):

            binary_Formatted, _, xyNoise = GetBinaryAtPoint(x,y)
            
            noisePoint = point.Point(binary_Formatted)
            noisePoint.SetXY(x,y)
            noisePoint.rawValue = xyNoise
            
            
            noisePoints.append(noisePoint)


def score(a,b):

    total = 0
    for i in range(len(a)):
        aNum = int(a[i].binaryValue,2)
        bNum = int(b[i].binaryValue,2)
        total += abs(aNum - bNum)
    return total / len(a) if a else 0
    
    # total = 0
    # for i in range(len(a)):
    #     diff = int(a[i].binaryValue,2) - int(b[i].binaryValue,2)
    #     total += diff * diff
    # return total / len(a) if a else 0



def DisplayGrayscalePlots():
    global diff_grid
    """
    Displays the sorted points, noisePoints, difference, and raw Perlin noise side by side.
    Raw Perlin noise is scaled to 0-255 for grayscale, with improved contrast.
    """
    # Create 2D arrays
    points_grid = np.zeros((ySize, xSize))
    noise_grid = np.zeros((ySize, xSize))
    raw_noise_grid = np.zeros((ySize, xSize))  # New: Raw Perlin noise
    identifiers_grid = np.full((ySize, xSize), -1, dtype=int)  # New: Identifiers grid (-1 for empty)
    
    # Fill raw noise grid directly from Perlin
    for y in range(ySize):
        for x in range(xSize):
            raw_noise = GetNoise(x/ZOOM_AMOUNT, y/ZOOM_AMOUNT)
            # Scale Perlin (-1 to 1) to 0-255
            scaled_value = ((raw_noise + 1) / 2) * 255
            raw_noise_grid[y, x] = scaled_value
    
    # Debug: Print min/max of raw noise for contrast check
    print(f"Raw noise min: {np.min(raw_noise_grid)}, max: {np.max(raw_noise_grid)}")
    
    # Fill points grid (sorted points)
    for p in points:
        x, y = int(p.x), int(p.y)
        if 0 <= x < xSize and 0 <= y < ySize:
            value = int(p.binaryValue, 2) / ((1 << BIT_LENGTH) - 1) * 255
            points_grid[y, x] = value
            identifiers_grid[y, x] = p.identifier  # Store identifier
    
    # Fill noisePoints grid
    for npz in noisePoints:
        x, y = int(npz.x), int(npz.y)
        if 0 <= x < xSize and 0 <= y < ySize:
            value = int(npz.binaryValue, 2) / ((1 << BIT_LENGTH) - 1) * 255
            noise_grid[y, x] = value
    
    # Compute difference
    diff_grid = np.abs(points_grid - noise_grid)
    
    # Print unique values in difference grid
    unique_diffs = np.unique(diff_grid)
    print(f"Unique difference values: {len(unique_diffs)} ({unique_diffs})")
    
    # Create individual plots for each unique difference value
    num_unique = len(unique_diffs)
    if num_unique > 0:
        # Calculate grid layout for unique value plots
        cols = min(4, num_unique)  # Max 4 columns
        rows = (num_unique + cols - 1) // cols  # Calculate rows needed
        
        fig_unique, axes_unique = plt.subplots(rows, cols, figsize=(4*cols, 4*rows))
        
        # Handle case where there's only one subplot
        if num_unique == 1:
            axes_unique = [axes_unique]
        elif rows == 1:
            axes_unique = axes_unique if num_unique > 1 else [axes_unique]
        else:
            axes_unique = axes_unique.flatten()
        
        for i, unique_val in enumerate(unique_diffs):
            # Create binary mask: 1 where difference equals unique_val, 0 elsewhere
            mask = (diff_grid == unique_val).astype(int)
            
            # Plot: 1s as black (0), 0s as white (1) - inverted for better visibility
            display_mask = 1 - mask  # Invert so positions with this difference are black
            
            axes_unique[i].imshow(display_mask, cmap='gray', vmin=0, vmax=1)
            axes_unique[i].set_title(f'Diff = {unique_val:.1f}\n({np.sum(mask)} positions)')
            axes_unique[i].set_xlabel('X')
            axes_unique[i].set_ylabel('Y')
        
        # Hide unused subplots if any
        for i in range(num_unique, len(axes_unique)):
            axes_unique[i].axis('off')
        
        plt.tight_layout()
        plt.show()
    
    # Create main 5 subplots (added identifiers plot)
    fig, ((ax1, ax2, ax3), (ax4, ax5, ax_empty)) = plt.subplots(2, 3, figsize=(18, 12))
    
    # Plot sorted points
    im1 = ax1.imshow(points_grid, cmap='gray', vmin=0, vmax=255)
    ax1.set_title('Sorted Points (Linear Due to Sorting)')
    plt.colorbar(im1, ax=ax1, shrink=0.8)
    
    # Plot noisePoints
    im2 = ax2.imshow(noise_grid, cmap='gray', vmin=0, vmax=255)
    ax2.set_title('Noise Points (Processed)')
    plt.colorbar(im2, ax=ax2, shrink=0.8)
    
    # Plot difference
    im3 = ax3.imshow(diff_grid, cmap='hot', vmin=0, vmax=255)
    ax3.set_title('Difference (0-255 scale)')
    plt.colorbar(im3, ax=ax3, shrink=0.8)
    
    # Plot raw Perlin noise with dynamic scaling and better colormap for contrast
    raw_min = np.min(raw_noise_grid)
    raw_max = np.max(raw_noise_grid)
    im4 = ax4.imshow(raw_noise_grid, cmap='plasma', vmin=raw_min, vmax=raw_max)
    ax4.set_title('Raw Perlin Noise (Enhanced Contrast)')
    plt.colorbar(im4, ax=ax4, shrink=0.8)
    
    # Plot identifiers
    # Scale identifiers by 10 to make differences more visible
    identifiers_scaled = identifiers_grid * 10
    # Mask -1 values to make them transparent/white
    identifiers_masked = np.ma.masked_where(identifiers_grid == -1, identifiers_scaled)
    im5 = ax5.imshow(identifiers_masked, cmap='tab20', vmin=0, vmax=(len(points)-1)*10)
    ax5.set_title('Point Identifiers (Reorganized Positions) x10')
    plt.colorbar(im5, ax=ax5, shrink=0.8, label='Identifier x10')
    
    # Hide the empty subplot
    ax_empty.axis('off')
    
    plt.tight_layout()
    plt.show()
    

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
    FillNoiseList()
    
    # points.sort(key=lambda x : x.binaryValue)
    points.sort(key=lambda x : x.binaryValue)
    sortedNoisePoints = sorted(noisePoints, key=lambda x : x.binaryValue)
    
    z = 0
    for y in range(ySize):
        for x in range(xSize):
            noisePoint = GetNoise(x/ZOOM_AMOUNT,y/ZOOM_AMOUNT)
            points[z].SetIdentifier(noisePoint)
            sortedNoisePoints[z].SetIdentifier(noisePoint)
            z += 1

    for i in range(len(points)):
        points[i].SetXY(sortedNoisePoints[i].x, sortedNoisePoints[i].y)
        print(f"{points[i]} : {sortedNoisePoints[i]}")    
        

        

    
def Main():
    global seed
    bestScore = 9999999999999999999999999999999999999
    bestSeed = 0
    i = 0
    try:
        while(True):
            # ReadFile("experiments/Reorg/source.txt")
            ChangeNoiseSeed(seed)
            Generate()
            sumOfGird = score(points, noisePoints)
            if(sumOfGird < bestScore):
                bestScore = sumOfGird
                bestSeed = seed
                print(f"BETTER SCORE AND SEED {bestScore} with seed {bestSeed}")
            
            seed += SEED_INCREMENT
            noisePoints.clear()
            # points.clear()
            i += 1
    except KeyboardInterrupt:
        print("Best Seed was " + str(bestSeed))
        print("Best score was " + str(bestScore))
        print(f"ran for {i}th iterations")
        
        # Regenerate with best seed for display - PROPERLY RESET STATE
        seed = bestSeed
        points.clear()  # Clear the modified points
        noisePoints.clear()  # Clear noise points
        ReadFile("experiments/Reorg/source.txt")  # Reload fresh points from file
        ChangeNoiseSeed(seed)  # Set the best seed
        Generate()  # Generate with clean state
        DisplayGrayscalePlots()
        
        
    
    
    
    # for i in range(len(points)):
    #     print(points[i])
    
    
    




ReadFile("experiments/Reorg/source.txt")
# Main()        
seed = 102602
ChangeNoiseSeed(seed)
finalList = Generate()
# print("RECONSTRUCTED TEXT ==")
# print(ReconstructText(finalList))
DisplayGrayscalePlots()