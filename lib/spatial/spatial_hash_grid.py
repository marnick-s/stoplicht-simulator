from lib.collidable_object import Hitbox
from lib.screen import screen, scale_to_display

class SpatialHashGrid:
    """
    A spatial hash grid for efficient collision detection.
    Objects are placed into cells based on their position to reduce the number of collision checks.
    """
    
    def __init__(self, cell_size=40):
        self.cell_size = cell_size
        self.grid = {}  # Dictionary mapping cell coordinates to lists of objects
        
    def _get_cell_coords(self, x, y):
        """Convert world coordinates to grid cell coordinates."""
        cell_x = int(x // self.cell_size)
        cell_y = int(y // self.cell_size)
        return cell_x, cell_y
    
    def _get_cells_for_hitbox(self, hitbox):
        """Get all cells that a hitbox overlaps."""
        min_cell_x, min_cell_y = self._get_cell_coords(hitbox.x, hitbox.y)
        max_cell_x, max_cell_y = self._get_cell_coords(
            hitbox.x + hitbox.width, hitbox.y + hitbox.height
        )
        
        cells = []
        for cell_x in range(min_cell_x, max_cell_x + 1):
            for cell_y in range(min_cell_y, max_cell_y + 1):
                cells.append((cell_x, cell_y))
                
        return cells
    
    def insert(self, obj):
        """Insert an object into the grid."""
        hitboxes = obj.hitboxes()
        for hitbox in hitboxes:
            cells = self._get_cells_for_hitbox(hitbox)
            for cell in cells:
                if cell not in self.grid:
                    self.grid[cell] = []
                # Only add the object once per cell
                if obj not in self.grid[cell]:
                    self.grid[cell].append(obj)
    
    def query(self, hitbox):
        """Find all objects that could potentially collide with the given hitbox."""
        cells = self._get_cells_for_hitbox(hitbox)
        
        # Use a set to avoid duplicates
        result = set()
        for cell in cells:
            if cell in self.grid:
                result.update(self.grid[cell])
        
        return list(result)
    
    def clear(self):
        """Clear the grid."""
        self.grid.clear()
    
    def query_radius(self, x, y, radius):
        """Find all objects within a radius of the given point."""
        # Create a hitbox that encompasses the circle
        search_box = Hitbox(x - radius, y - radius, radius * 2, radius * 2)
        return self.query(search_box)

    def draw(self, color=(150, 150, 150)):
        """Draw grid for debugging purposes."""
        import pygame
        
        # Only draw cells with objects
        for cell_coords, objects in self.grid.items():
            if objects:
                cell_x, cell_y = cell_coords
                x, y = scale_to_display(cell_x * self.cell_size, cell_y * self.cell_size)
                width, height = scale_to_display(self.cell_size, self.cell_size)
                pygame.draw.rect(screen, color, (x, y, width, height), 1)