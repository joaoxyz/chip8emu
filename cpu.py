class CPU:
    def __init__(self):
        # 4kb memory
        self.memory = [0] * 4096
        # 64x32 pixels display
        self.display = [[0] * 64 for _ in range(32)]
        self.program_counter = 0x200
        self.index_register = 0
        self.stack = []
        # Timers initialized as zero
        self.delay_timer = 0
        self.sound_timer = 0
        self.variable_registers = [0] * 16

        # TODO: Add font data to memory
        # TODO: Research how timers work??

    def fetch(self):
        instruction = self.memory[self.program_counter] + self.memory[self.program_counter+1]
        self.program_counter += 2
        return instruction

    def decode_and_execute(self, instruction):
        first_nibble = instruction.hex()[0]
        second_nibble = instruction.hex()[1]
        third_nibble = instruction.hex()[2]
        fourth_nibble = instruction.hex()[3]

        second_byte = instruction.hex()[1:3]
        nibbles234 = instruction.hex()[1:]

        match first_nibble:
            case '0':
                match fourth_nibble:
                    case '0':
                        # 00E0: Clear screen
                        self.display = [[0] * 64 for _ in range(32)]
                    case 'e':
                        # 00EE: Return subroutine
                        self.program_counter = self.stack.pop()
            case '1':
                # 1NNN: Jump
                self.program_counter = int(nibbles234, 16)
            case '6':
                # 6XNN: Set
                self.variable_registers[int(second_nibble, 16)] = int(second_byte, 16)
            case '7':
                # 7XNN: Add
                self.variable_registers[int(second_nibble, 16)] += int(second_byte, 16)
                # Wrap-around on overflow
                self.variable_registers[int(second_nibble, 16)] &= 255
            case 'a':
                # ANNN: Set index register
                self.index_register = int(nibbles234, 16)
            case 'd':
                # DXYN: Display draw
                x_cord = self.variable_registers[self.hex_to_int(second_nibble)] & 63
                y_cord = self.variable_registers[self.hex_to_int(third_nibble)] & 63
                self.variable_registers[-1] = 0

    def dump_display(self):
        pass

    def hex_to_int(self, val):
        return int(val, 16)
