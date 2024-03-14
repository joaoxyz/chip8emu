import cpu, sys

if len(sys.argv) != 2:
    print('Usage: python main.py filename')
    sys.exit(1)

chip8cpu = cpu.CPU()

read_index = chip8cpu.program_counter
with open(sys.argv[1], 'rb') as rom:
    while (byte := rom.read(1)):
        chip8cpu.memory[read_index] = byte
        read_index += 1

print(chip8cpu.fetch())