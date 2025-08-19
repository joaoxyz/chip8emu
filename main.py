import sys
import time

import numpy as np
import numpy.typing as npt
import pygame
from pygame.surfarray import blit_array

import cpu

type RGBColor = tuple[int, int, int]
TIMER_UPDATE = 0.016

def draw(screen: pygame.Surface, arr: npt.NDArray[np.uint8], palette: tuple[RGBColor, RGBColor]) -> None:
    colored_arr = np.zeros((*arr.shape, 3), dtype=np.uint8)
    colored_arr[arr == 1] = palette[0]
    colored_arr[arr != 1] = palette[1]

    blit_array(screen, colored_arr)
    pygame.display.flip()

def run(cpu: cpu.CPU) -> int:
    pygame.init()
    screen = pygame.display.set_mode((64, 32), pygame.SCALED)
    running = True
    color_palette = ((139,172,15), (15,56,15))

    acc = 0.0
    last_time = time.time()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        acc += time.time() - last_time
        if acc > TIMER_UPDATE:
            if cpu.delay_timer > 0:
                cpu.delay_timer -= 1
            if cpu.sound_timer > 0:
                cpu.sound_timer -= 1
            acc = 0.0
        last_time = time.time()

        # Emulator logic
        cpu.decode_and_execute(cpu.fetch())

        draw(screen, cpu.display, color_palette)

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