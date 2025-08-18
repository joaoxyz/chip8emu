import sys
from random import randint

import numpy as np

class CPU:
    def __init__(self) -> None:
        # 4kb memory
        self.memory: list[int] = [0] * 4096
        # 64x32 pixels display
        self.display = np.zeros((64, 32), dtype=np.uint8)
        self.program_counter: int = 0x200
        self.index_register: int = 0
        self.stack: list[int] = []
        # Timers initialized as zero
        self.delay_timer = 0
        self.sound_timer = 0
        self.variable_registers: list[int] = [0] * 16

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

        characters = '0123456789abcdef'
        positions = list(range(0x50, 0x50+len(font_arr), 5))
        self.font_positions = dict(zip(characters, positions))

        # TODO: Research how timers work??

    def fetch(self) -> bytes:
        instruction = self.memory[self.program_counter].to_bytes() + self.memory[self.program_counter+1].to_bytes()
        self.program_counter += 2
        return instruction

    def decode_and_execute(self, instruction: bytes) -> None:
        nibble1 = instruction.hex()[0]
        nibble2 = instruction.hex()[1]
        nibble3 = instruction.hex()[2]
        nibble4 = instruction.hex()[3]

        byte2 = instruction.hex()[2:]
        nibbles234 = instruction.hex()[1:]

        match nibble1:
            case '0':
                match byte2:
                    case 'e0':
                        # 00E0: Clear screen
                        self.display[self.display != 0] = 0
                    case 'ee':
                        # 00EE: Return subroutine
                        self.program_counter = self.stack.pop()
                    case _:
                        print(f'Unknown instruction: {instruction.hex()}')
            case '1':
                # 1NNN: Jump
                self.program_counter = int(nibbles234, base=16)
            case '2':
                # 2NNN: Call subroutine
                self.stack.append(self.program_counter)
                self.program_counter = int(nibbles234, base=16)
            case '3':
                # 3XNN: Skip if VX == NN
                if self.variable_registers[int(nibble2, base=16)] == int(byte2, base=16):
                    self.program_counter += 2
            case '4':
                # 4XNN: Skip if VX != NN
                if self.variable_registers[int(nibble2, base=16)] != int(byte2, base=16):
                    self.program_counter += 2
            case '5':
                # 5XY0: Skip if VX == VY
                if self.variable_registers[int(nibble2, base=16)] == self.variable_registers[int(nibble3, base=16)]:
                    self.program_counter += 2
            case '6':
                # 6XNN: Set
                self.variable_registers[int(nibble2, base=16)] = int(byte2, base=16)
            case '7':
                # 7XNN: Add
                self.variable_registers[int(nibble2, base=16)] += int(byte2, base=16)
                # Wrap-around on overflow
                self.variable_registers[int(nibble2, base=16)] &= 255
            case '8':
                match nibble4:
                    case '0':
                        self.variable_registers[int(nibble2, base=16)] = self.variable_registers[int(nibble3, base=16)]
                    case '1':
                        self.variable_registers[int(nibble2, base=16)] |= self.variable_registers[int(nibble3, base=16)]
                    case '2':
                        self.variable_registers[int(nibble2, base=16)] &= self.variable_registers[int(nibble3, base=16)]
                    case '3':
                        self.variable_registers[int(nibble2, base=16)] ^= self.variable_registers[int(nibble3, base=16)]
                    case '4':
                        self.variable_registers[int(nibble2, base=16)] += self.variable_registers[int(nibble3, base=16)]
                        # Wrap-around on overflow and set carry flag
                        if self.variable_registers[int(nibble2, base=16)] > 255:
                            self.variable_registers[int(nibble2, base=16)] &= 255
                            self.variable_registers[-1] = 1
                        else:
                            self.variable_registers[-1] = 0
                    case '5':
                        vx = self.variable_registers[int(nibble2, base=16)]
                        vy = self.variable_registers[int(nibble3, base=16)]
                        # Set carry flag
                        if vx < vy:
                            self.variable_registers[-1] = 0
                        else:
                            self.variable_registers[-1] = 1
                        # x - y
                        self.variable_registers[int(nibble2, base=16)] = (vx - vy) & 255
                    case '7':
                        vx = self.variable_registers[int(nibble2, base=16)]
                        vy = self.variable_registers[int(nibble3, base=16)]
                        # Set carry flag
                        if vy < vx:
                            self.variable_registers[-1] = 0
                        else:
                            self.variable_registers[-1] = 1
                        # x - y
                        self.variable_registers[int(nibble2, base=16)] = (vy - vx) & 255
                    case '6':
                        # TODO: Ambiguous instruction, behavior should be configurable
                        # Set VF to bit shifted out
                        self.variable_registers[-1] = self.variable_registers[int(nibble2, base=16)] & 1
                        self.variable_registers[int(nibble2, base=16)] >>= 1
                    case 'e':
                        # TODO: Ambiguous instruction, behavior should be configurable
                        # Set VF to bit shifted out
                        self.variable_registers[-1] = (self.variable_registers[int(nibble2, base=16)] & 128) >> 7
                        self.variable_registers[int(nibble2, base=16)] <<= 1
                        # Handle overflow
                        self.variable_registers[int(nibble2, base=16)] &= 0xFF
                    case _:
                        print(f'Unknown instruction: {instruction.hex()}')
            case '9':
                # 9XY0: Skip if VX != VY
                if self.variable_registers[int(nibble2, base=16)] != self.variable_registers[int(nibble3, base=16)] :
                    self.program_counter += 2
            case 'a':
                # ANNN: Set index register
                self.index_register = int(nibbles234, base=16)
            case 'b':
                # TODO: Ambiguous instruction, could be made configurable
                self.program_counter = int(nibbles234, base=16) + self.variable_registers[0]
            case 'c':
                self.variable_registers[int(nibble2, base=16)] = randint(0, sys.maxsize) & int(byte2, base=16)
            case 'd':
                # DXYN: Draw to display
                x_cord = self.variable_registers[int(nibble2, base=16)] & 63
                y_cord = self.variable_registers[int(nibble3, base=16)] & 31
                self.variable_registers[-1] = 0
                sprite_height = int(nibble4, base=16)
                sprite_width = 8

                sprite_memory_pos = self.index_register
                for y in range(y_cord, min(len(self.display[0]), y_cord+sprite_height)):
                    #sprite = f'{int(self.memory[sprite_memory_pos].hex(), base=16):08b}'
                    sprite = f'{self.memory[sprite_memory_pos]:08b}'
                    sprite_idx = 0
                    for x in range(x_cord, min(len(self.display), x_cord+sprite_width)):
                        self.display[x][y] ^= int(sprite[sprite_idx], base=2)
                        # Update register VF on pixel turnoff
                        if (self.display[x][y] == 1 and int(sprite[sprite_idx], base=2)):
                            self.variable_registers[-1] = 1
                        sprite_idx += 1
                    sprite_memory_pos += 1
            case 'f':
                match byte2:
                    case '1e':
                        self.index_register += self.variable_registers[int(nibble2, base=16)]
                        # Handle overflow
                        if self.index_register > 0x0FFF:
                            self.variable_registers[-1] = 1
                        if self.index_register > 0xFFFF:
                            self.index_register &= 0xFFFF
                    #case '0a':
                    case '29':
                        # FX29: Set index to font data for character in VX
                        char = self.variable_registers[int(nibble2, base=16)].to_bytes().hex()[1]
                        self.index_register = self.font_positions[char]
                    case '33':
                        num = self.variable_registers[int(nibble2, base=16)]
                        i = 2
                        while i >= 0:
                            digit = num % 10
                            self.memory[self.index_register+i] = digit
                            num //= 10
                            i -= 1
                    case '55':
                        # Ambiguous instruction!
                        upper_bound = int(nibble2, base=16)
                        for i in range(upper_bound+1):
                            self.memory[self.index_register+i] = self.variable_registers[i]
                    case '65':
                        # Ambiguous instruction!
                        upper_bound = int(nibble2, base=16)
                        for i in range(upper_bound+1):
                            self.variable_registers[i] = self.memory[self.index_register+i]
                    case _:
                        print(f'Unknown instruction: {instruction.hex()}')
            case _:
               print(f'Unknown instruction: {instruction.hex()}')

    def dump_display(self) -> None:
        for col in range(len(self.display)):
            for row in range(len(self.display[0])):
                print(self.display[col][row], end='')
            print()
