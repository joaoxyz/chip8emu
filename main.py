import sys

import numpy as np
import pygame
from pygame.surfarray import blit_array

import cpu

def run(cpu_instance: cpu.CPU) -> int:
    pygame.init()
    screen = pygame.display.set_mode((64, 32), pygame.SCALED)
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        blit_array(screen, cpu_instance.display * 255)

        # Game logic
        inst = cpu_instance.fetch()
        cpu_instance.decode_and_execute(inst)

        pygame.display.flip()

        clock.tick(60)

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

    sys.exit(run(chip8cpu))