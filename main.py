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
    pygame.display.flip()

def run(cpu: cpu.CPU) -> int:
    pygame.init()
    screen = pygame.display.set_mode((64, 32), pygame.SCALED)
    clock = pygame.time.Clock()
    running = True
    color_palette = ((139,172,15), (15,56,15))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                key = event.key
                if key in cpu.keypad_layout:
                    cpu.keypad_state[cpu.keypad_layout[key]] = True
            if event.type == pygame.KEYUP:
                key = event.key
                if key in cpu.keypad_layout:
                    cpu.keypad_state[cpu.keypad_layout[key]] = False
                    if cpu.wait:
                        cpu.variable_registers[cpu.wait_register] = cpu.keypad_layout[key]
                        cpu.wait = False

        # Emulator logic
        cpu.step()

        draw(screen, cpu.display, color_palette)

        clock.tick(60)

    if (cpu.debug):
        cpu.dump_display()

    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python main.py filename')
        sys.exit(1)

    chip8cpu = cpu.CPU()

    with open(sys.argv[1], 'rb') as rom:
        rom_data = bytearray(rom.read())
        chip8cpu.memory[chip8cpu.program_counter:len(rom_data)] = rom_data

    sys.exit(run(chip8cpu))