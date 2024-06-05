import cpu
import time
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python main.py filename')
        sys.exit(1)

    chip8cpu = cpu.CPU()

    read_index = chip8cpu.program_counter
    with open(sys.argv[1], 'rb') as rom:
        while (byte := rom.read(1)):
            chip8cpu.memory[read_index] = byte
            read_index += 1

    try:
        while True:
            inst = chip8cpu.fetch()
            chip8cpu.decode_and_execute(inst)
    except KeyboardInterrupt:
        chip8cpu.dump_display()

    #sys.exit(run(chip8cpu))