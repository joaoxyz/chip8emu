class CPU:
    def __init__(self):
        # 4kb memory
        self.memory = [0] * 4096
        # 64x32 pixels display
        self.display = [[0] * 64 for _ in range(32)]
        self.program_counter = 0x200
        self.index_register = 0
        self.stack = []
        self.delay_timer = 60
        self.sound_timer = 60
        self.variable_registers = [0] * 16

    def fetch(self):
        pass

    def decode(self):
        pass

    def execute(self):
        pass