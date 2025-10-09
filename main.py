import sys

import numpy as np
import numpy.typing as npt
import pygame
from pygame.surfarray import blit_array

import cpu

type RGBColor = tuple[int, int, int]

screen_size = (1024, 512)

# Mapping of keyboard keycodes to CHIP-8 keys
keypad_layout = {
    pygame.K_x: 0x0,
    pygame.K_1: 0x1,
    pygame.K_2: 0x2,
    pygame.K_3: 0x3,
    pygame.K_q: 0x4,
    pygame.K_w: 0x5,
    pygame.K_e: 0x6,
    pygame.K_a: 0x7,
    pygame.K_s: 0x8,
    pygame.K_d: 0x9,
    pygame.K_z: 0xA,
    pygame.K_c: 0xB,
    pygame.K_4: 0xC,
    pygame.K_r: 0xD,
    pygame.K_f: 0xE,
    pygame.K_v: 0xF,
}

def draw(screen: pygame.Surface, original_display: pygame.Surface, arr: npt.NDArray[np.uint8], palette: tuple[RGBColor, RGBColor]) -> None:
    colored_arr = np.zeros((*arr.shape, 3), dtype=np.uint8)
    colored_arr[arr == 1] = palette[0]
    colored_arr[arr != 1] = palette[1]

    blit_array(original_display, colored_arr)
    pygame.transform.scale(original_display, screen_size, screen)
    pygame.display.flip()

def run(cpu: cpu.CPU) -> int:
    pygame.init()
    pygame.mixer.init()

    # beep = pygame.mixer.Sound("beep.wav")
    screen = pygame.display.set_mode(screen_size)
    original_display = pygame.Surface((64, 32))
    clock = pygame.time.Clock()
    color_palette = ((139,172,15), (15,56,15))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                key = event.key
                if key in keypad_layout:
                    cpu.keypad_state[keypad_layout[key]] = True
            if event.type == pygame.KEYUP:
                key = event.key
                if key in keypad_layout:
                    cpu.keypad_state[keypad_layout[key]] = False
                    if cpu.wait_input:
                        cpu.variable_registers[cpu.wait_register] = keypad_layout[key]
                        cpu.wait_input = False

        # Emulator logic
        cpu.step()

        draw(screen, original_display, cpu.display, color_palette)
        cpu.draw_interrupt = False

        if cpu.sound_timer > 0:
            # beep.play()
            pass

        clock.tick(60)

    if (cpu.debug):
        cpu.dump_display()

    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python main.py filename')
        sys.exit(1)

    emulator = cpu.CPU()

    with open(sys.argv[1], 'rb') as rom:
        rom_data = bytearray(rom.read())
    emulator.memory[emulator.program_counter:len(rom_data)] = rom_data

    sys.exit(run(emulator))