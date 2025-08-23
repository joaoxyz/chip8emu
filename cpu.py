from random import randint

import numpy as np
import pygame

class CPU:
    def __init__(self, debug: bool = False) -> None:
        self.debug = debug
        # 4kb memory
        self.memory: bytearray = bytearray(4096)
        # 64x32 pixels display
        self.display = np.zeros((64, 32), dtype=np.uint8)
        self.program_counter: int = 0x200
        self.index_register: int = 0
        self.stack: list[int] = []
        self.delay_timer = 0xFF
        self.sound_timer = 0xFF
        self.variable_registers: list[int] = [0] * 16

        # Mapping of keyboard keycodes to CHIP-8 keys
        self.keypad_layout = {
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


        self.keypad_state = [False] * 16

        # Add font data to memory
        font_arr: list[int] = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]

        for i in range(0x50, 0x50+len(font_arr)):
            self.memory[i] = font_arr[i-0x50]

        self.wait = False
        self.wait_register: int = 0
        self.instructions_per_cycle = 15

    def fetch(self) -> int:
        byte1 = self.memory[self.program_counter]
        byte2 = self.memory[self.program_counter+1]
        instruction = (byte1 << 8) | byte2

        if (self.debug):
            print(hex(instruction))

        self.program_counter += 2
        return instruction

    def decode_and_execute(self, instruction: int) -> None:
        nibble1 = (instruction & 0xF000) >> 12
        nibble2 = (instruction & 0x0F00) >> 8
        nibble3 = (instruction & 0x00F0) >> 4
        nibble4 = (instruction & 0x000F)

        x = nibble2
        y = nibble3
        n = nibble4
        nn = instruction & 0x00FF
        nnn = instruction & 0x0FFF

        match nibble1:
            case 0x0:
                match nn:
                    case 0xE0:
                        # 00E0: Clear screen
                        self.display.fill(0)
                    case 0xEE:
                        # 00EE: Return subroutine
                        self.program_counter = self.stack.pop()
                    case _:
                        print(f'Unknown instruction: {hex(instruction)}')
            case 0x1:
                # 1NNN: Jump
                self.program_counter = nnn
            case 0x2:
                # 2NNN: Call subroutine
                self.stack.append(self.program_counter)
                self.program_counter = nnn
            case 0x3:
                # 3XNN: Skip if VX == NN
                if self.variable_registers[x] == nn:
                    self.program_counter += 2
            case 0x4:
                # 4XNN: Skip if VX != NN
                if self.variable_registers[x] != nn:
                    self.program_counter += 2
            case 0x5:
                # 5XY0: Skip if VX == VY
                if self.variable_registers[x] == self.variable_registers[y]:
                    self.program_counter += 2
            case 0x6:
                # 6XNN: Set
                self.variable_registers[x] = nn
            case 0x7:
                # 7XNN: Add
                self.variable_registers[x] += nn
                # Wrap-around on overflow
                self.variable_registers[x] &= 255
            case 0x8:
                # Logical and arithmetic instructions
                match nibble4:
                    case 0x0:
                        # 8XY0: Set
                        self.variable_registers[x] = self.variable_registers[y]
                    case 0x1:
                        # 8XY1: Binary OR
                        self.variable_registers[x] |= self.variable_registers[y]
                    case 0x2:
                        # 8XY2: Binary AND
                        self.variable_registers[x] &= self.variable_registers[y]
                    case 0x3:
                        # 8XY3: Bitwise XOR
                        self.variable_registers[x] ^= self.variable_registers[y]
                    case 0x4:
                        # 8XY4: Add
                        self.variable_registers[x] += self.variable_registers[y]
                        # Wrap-around on overflow and set carry flag
                        if self.variable_registers[x] > 255:
                            self.variable_registers[x] &= 255
                            self.variable_registers[0xF] = 1
                        else:
                            self.variable_registers[0xF] = 0
                    case 0x5:
                        # 8XY5: Subtract VX - VY
                        vx = self.variable_registers[x]
                        vy = self.variable_registers[y]
                        self.variable_registers[x] = (vx - vy) & 255
                        # Set carry flag
                        if vx < vy:
                            self.variable_registers[0xF] = 0
                        else:
                            self.variable_registers[0xF] = 1
                    case 0x7:
                        # 8XY7: Subtract VY - VX
                        vx = self.variable_registers[x]
                        vy = self.variable_registers[y]
                        self.variable_registers[x] = (vy - vx) & 255
                        # Set carry flag
                        if vy < vx:
                            self.variable_registers[0xF] = 0
                        else:
                            self.variable_registers[0xF] = 1
                    case 0x6:
                        # 8XY6: Shift right
                        # TODO: Ambiguous instruction, behavior should be configurable
                        vx = self.variable_registers[x]
                        self.variable_registers[x] >>= 1
                        # Set VF to bit shifted out
                        self.variable_registers[0xF] = vx & 1
                    case 0xE:
                        # 8XY6: Shift left
                        # TODO: Ambiguous instruction, behavior should be configurable
                        vx = self.variable_registers[x]
                        self.variable_registers[x] <<= 1
                        # Handle overflow
                        self.variable_registers[x] &= 0xFF
                        # Set VF to bit shifted out
                        self.variable_registers[0xF] = (vx & 128) >> 7
                    case _:
                        print(f'Unknown instruction: {hex(instruction)}')
            case 0x9:
                # 9XY0: Skip if VX != VY
                if self.variable_registers[x] != self.variable_registers[y] :
                    self.program_counter += 2
            case 0xA:
                # ANNN: Set index register
                self.index_register = nnn
            case 0xB:
                # BNNN: Jump with offset
                # TODO: Ambiguous instruction, could be made configurable
                self.program_counter = nnn + self.variable_registers[0]
            case 0xC:
                # CXNN: Random number generation
                self.variable_registers[x] = randint(0, 255) & nn
            case 0xD:
                # DXYN: Draw to display
                x_start_pos = self.variable_registers[x] & 63
                y_start_pos = self.variable_registers[y] & 31
                self.variable_registers[0xF] = 0
                sprite_height = n
                sprite_width = 8

                for y_pos in range(sprite_height):
                    sprite = self.memory[self.index_register+y_pos]
                    y_screen = (y_start_pos + y_pos)# & 31
                    if y_screen >= len(self.display[0]):
                        break
                    for x_pos in range(sprite_width):
                        sprite_pixel = (sprite >> (7 - x_pos)) & 1
                        if sprite_pixel == 1:
                            x_screen = (x_start_pos + x_pos) & 63
                            if x_screen >= len(self.display):
                                break
                            # Update register VF on pixel turnoff
                            if self.display[x_screen][y_screen] == 1:
                                self.variable_registers[0xF] = 1
                            self.display[x_screen][y_screen] ^= 1
            case 0xE:
                match nn:
                    case 0x9E:
                        # EX9E: Skip if key pressed
                        key = self.variable_registers[x] & 0xF
                        if self.keypad_state[key]:
                            self.program_counter += 2
                    case 0xA1:
                        # EXA1: Skip if key not pressed
                        key = self.variable_registers[x] & 0xF
                        if not self.keypad_state[key]:
                            self.program_counter += 2
                    case _:
                        print(f'Unknown instruction: {hex(instruction)}')
            case 0xF:
                match nn:
                    case 0x07:
                        # FX07: Set VX to delay timer
                        self.variable_registers[x] = self.delay_timer
                    case 0x15:
                        # FX15: Set delay timer to VX
                        self.delay_timer = self.variable_registers[x]
                    case 0x18:
                        # FX18: Set sound timer to VX
                        self.sound_timer = self.variable_registers[x]
                    case 0x1E:
                        # FX1E: Add to index
                        self.index_register += self.variable_registers[x]
                        # Handle overflow
                        if self.index_register > 0x0FFF:
                            self.variable_registers[0xF] = 1
                        if self.index_register > 0xFFFF:
                            self.index_register &= 0xFFFF
                    case 0x0A:
                        # FX0A: Get key
                        self.wait = True
                        self.wait_register = x
                    case 0x29:
                        # FX29: Set index to font data for character in VX
                        char = self.variable_registers[x] & 15
                        self.index_register = 0x50 + (char * 5)
                    case 0x33:
                        # FX33: Binary-coded decimal conversion
                        num = self.variable_registers[x]
                        i = 2
                        while i >= 0:
                            digit = num % 10
                            self.memory[self.index_register+i] = digit
                            num //= 10
                            i -= 1
                    case 0x55:
                        # FX55: Store
                        # Ambiguous instruction!
                        upper_bound = x
                        for i in range(upper_bound+1):
                            self.memory[self.index_register+i] = self.variable_registers[i]
                    case 0x65:
                        # FX65: Load
                        # Ambiguous instruction!
                        upper_bound = x
                        for i in range(upper_bound+1):
                            self.variable_registers[i] = self.memory[self.index_register+i]
                    case _:
                        print(f'Unknown instruction: {hex(instruction)}')
            case _:
               print(f'Unknown instruction: {hex(instruction)}')

    def step(self) -> None:
        for _ in range(self.instructions_per_cycle):
            if not self.wait:
                self.decode_and_execute(self.fetch())

        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

    def dump_display(self) -> None:
        for y in range(len(self.display[0])):
            for x in range(len(self.display)):
                char = '*' if self.display[x][y] else ' '
                print(char, end='')
            print()
