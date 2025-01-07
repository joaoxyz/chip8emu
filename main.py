import sys

import numpy as np
import numpy.typing as npt
import pygame
from pygame.surfarray import blit_array

import cpu

type RGBColor = tuple[int, int, int]

def draw(screen: pygame.Surface, arr: npt.NDArray[np.uint8], palette: tuple[RGBColor, RGBColor]) -> None:
    colored_arr = np.zeros((*arr.shape, 3), dtype=np.uint8)
    colored_arr[arr == 1] = palette[0]
    colored_arr[arr != 1] = palette[1]

    blit_array(screen, colored_arr)

def run(cpu_instance: cpu.CPU) -> int:
    pygame.init()
    screen = pygame.display.set_mode((64, 32), pygame.SCALED)
    clock = pygame.time.Clock()
    running = True
    color_palette = ((15,56,15), (139,172,15))
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw(screen, cpu_instance.display, color_palette)

        # Emulator logic
        inst = cpu_instance.fetch()
        cpu_instance.decode_and_execute(inst)

        pygame.display.flip()
        #clock.tick(60)

    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python main.py filename')
        sys.exit(1)

    chip8cpu = cpu.CPU()

    read_index = chip8cpu.program_counter
    with open(sys.argv[1], 'rb') as rom:
        while (byte := rom.read(1)):
            chip8cpu.memory[read_index] = int.from_bytes(byte)
            read_index += 1

    sys.exit(run(chip8cpu))