import math


def secs_to_mmss(value: int) -> str:
    return f"{math.floor(value / 60)}:{int(value % 60)}"
