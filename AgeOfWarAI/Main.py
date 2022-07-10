s = 'saihfhawa'
a = 10
b = 5
print(f"{a:1}")
print(f"{b:1}")

from typing import Literal

def accepts_only_four(x: Literal[4]) -> None:
    print("ceva")

accepts_only_four(6)