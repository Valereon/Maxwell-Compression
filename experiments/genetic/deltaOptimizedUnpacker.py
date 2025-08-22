import numpy as np
import dahuffman
import json

def decompress_file():
    # Load metadata
    with open("metadata.json", "r") as f:
        metadata = json.load(f)
    
    seed = metadata["seed"]
    bit_length = metadata["bit_length"]
    original_length = metadata["original_length"]
    max_delta = metadata["max_delta"]
    
    print(f"Decompressing with seed: {seed}, bit_length: {bit_length}")
    
    # Load Huffman codec and compressed data
    codec = dahuffman.HuffmanCodec.load("table_lossless.tmax")
    
    with open("compressed_lossless.max", "rb") as f:
        compressed_data = f.read()
    
    # Decompress from Huffman
    capped_differential_deltas = codec.decode(compressed_data)
    print(f"Decompressed {len(capped_differential_deltas)} capped differential deltas")
    
    # Uncap the differential deltas (reverse of cap_deltas)
    differential_deltas = uncap_deltas(capped_differential_deltas, max_delta)
    print(f"Uncapped to {len(differential_deltas)} differential deltas")
    
    # Reverse differential encoding (reverse of multi_pass_delta_encode)
    deltas = reverse_differential_encode(differential_deltas, passes=1)
    print(f"Reversed differential encoding to {len(deltas)} deltas")
    
    # Convert deltas back to positions
    positions = deltas_to_positions(deltas)
    print(f"Converted to {len(positions)} positions")
    
    # Decode the original data using positions and seed
    original_data = decode_with_seed_from_positions(positions, seed, bit_length)
    
    return original_data

def uncap_deltas(capped_deltas, max_delta):
    """Reverse the capping operation - FIXED TO HANDLE NEGATIVE DELTAS"""
    result = []
    current_accumulator = 0
    
    for delta in capped_deltas:
        current_accumulator += delta
        if abs(delta) < max_delta:  # Check absolute value
            result.append(current_accumulator)
            current_accumulator = 0
    
    # Handle case where sequence ends with max_delta values
    if current_accumulator != 0:
        result.append(current_accumulator)
    
    return result

def reverse_differential_encode(diff_deltas, passes=1):
    """Reverse the differential encoding"""
    current = diff_deltas[:]
    
    for pass_num in range(passes):
        if len(current) < 2:
            break
            
        # Reconstruct original from differences
        reconstructed = [current[0]]  # First element stays the same
        for i in range(1, len(current)):
            original_value = reconstructed[i-1] + current[i]
            reconstructed.append(original_value)
        current = reconstructed
        
        print(f"Reverse pass {pass_num + 1}: reconstructed {len(current)} values")
    
    return current

def deltas_to_positions(deltas):
    """Convert deltas back to absolute positions"""
    if not deltas:
        return []
    
    positions = [deltas[0]]  # First position
    for i in range(1, len(deltas)):
        position = positions[i-1] + deltas[i]
        positions.append(position)
    
    return positions

def decode_with_seed_from_positions(positions, seed, bit_length):
    """Decode the original data using positions and seed - CORRECTLY FIXED"""
    rng = np.random.Generator(np.random.PCG64(seed))
    
    original_data = ""
    position_set = set(positions)  # For O(1) lookup
    
    # The positions represent tape positions where matches occurred
    # We need to generate the RNG sequence and extract data at those positions
    max_position = max(positions) if positions else 0
    
    for tape_pos in range(max_position + 1):
        # Generate the random number for this tape position
        num = rng.random()
        scaled = int(abs(num) * (10 ** bit_length))
        chunkInNoise = scaled % (10 ** bit_length)
        bitNumber = chunkInNoise % (2**bit_length)
        binaryBits = bin(bitNumber)[2:].zfill(bit_length)
        
        # If this tape position had a match, extract the bits
        if tape_pos in position_set:
            original_data += binaryBits
    
    return original_data

def binary_to_text(binary_string):
    """Convert binary string to readable text"""
    text = ""
    for i in range(0, len(binary_string), 8):
        byte = binary_string[i:i+8]
        if len(byte) == 8:
            try:
                char = chr(int(byte, 2))
                if 32 <= ord(char) <= 126 or char in '\n\r\t':
                    text += char
                else:
                    text += '.'
            except ValueError:
                text += '?'
    return text

# Main decompression
if __name__ == "__main__":
    try:
        print("Starting decompression...")
        
        # Decompress to binary
        decompressed_binary = decompress_file()
        print(f"Decompressed binary length: {len(decompressed_binary)}")
        print(f"First 100 bits: {decompressed_binary[:100]}")
        
        # Convert to text
        decompressed_text = binary_to_text(decompressed_binary)
        print(f"Decompressed text length: {len(decompressed_text)}")
        print(f"First 200 characters:")
        print(repr(decompressed_text[:200]))
        
        # Save decompressed data
        with open("decompressed.txt", "w", encoding='utf-8', errors='replace') as f:
            f.write(decompressed_text)
        
        with open("decompressed_binary.txt", "w") as f:
            f.write(decompressed_binary)
            
        print("Decompression complete! Check 'decompressed.txt' and 'decompressed_binary.txt'")
        
    except Exception as e:
        print(f"Decompression failed: {e}")
        import traceback
        traceback.print_exc()