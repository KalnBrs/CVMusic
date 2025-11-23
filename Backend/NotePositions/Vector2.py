class Vector2:
    x: float
    y: float
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    @staticmethod
    def magnitude(a: "Vector2", b: "Vector2") -> float:
        return ((b.x - a.x) ** 2 + (b.y - a.y) ** 2) ** 0.5