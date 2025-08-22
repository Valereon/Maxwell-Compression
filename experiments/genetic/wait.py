import dahuffman

with open("whatthefuck.max", "rb") as file:
    line = file.readlines()
    print(line)
    print(dahuffman.HuffmanCodec.load(line[0]))