# CHIP-8 Interpreter

This project is an interpreter/"emulator" for the CHIP-8 fantasy console written in Python using [pygame](https://www.pygame.org/).
I plan to add support to the SUPER-CHIP and XO-CHIP extensions the future.

## Controls

QWERTY keyboard key / Hexadecimal CHIP-8 keypad

| 1 / 1 | 2 / 2 | 3 / 3 | 4 / C |
|-------|-------|-------|-------|
| Q / 4 | W / 5 | E / 6 | R / D |
| A / 7 | S / 8 | D / 9 | F / E |
| Z / A | X / 0 | C / B | V / F |

# How to run

Clone the repo and use [uv](https://docs.astral.sh/uv/) or pip to install the dependecies.

With uv:
```
uv sync
uv run main.py <your-rom>
```

With pip:
```
pip install -r requirements.txt
python main.py <your-rom>
```

You can increase or decrease the resolution by editing the ```scale_factor``` variable in ```main.py```.