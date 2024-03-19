import cpu
import sys
import sdl2, sdl2.ext

def run():
    sdl2.ext.init()
    window = sdl2.ext.Window("The Pong Game", size=(64, 32))
    window.show()
    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        window.refresh()
    return 0

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

    '''
    for i in range():
        inst = chip8cpu.fetch()
        chip8cpu.decode_and_execute(inst)
    '''

    sys.exit(run())