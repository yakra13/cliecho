def clamp(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(max_value, int(value)))

def lerp(a: float, b: float, t: float) -> float:
    t = max(0.0, min(1.0, t))
    return a + (b - a) * t