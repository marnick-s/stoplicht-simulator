class Region:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains(self, hitbox):
        return (
            self.x <= hitbox.x and
            hitbox.x + hitbox.width <= self.x + self.width and
            self.y <= hitbox.y and
            hitbox.y + hitbox.height <= self.y + self.height
        )

    def intersects(self, hitbox):
        return (
            self.x < hitbox.x + hitbox.width and
            self.x + self.width > hitbox.x and
            self.y < hitbox.y + hitbox.height and
            self.y + self.height > hitbox.y
        )
