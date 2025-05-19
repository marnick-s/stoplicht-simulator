import pygame
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
        self.object_cells = {}  # Track which cells an object is in to avoid duplication
        
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
        
        # Faster cell coordinate generation using list comprehension
        return [(cell_x, cell_y) 
                for cell_x in range(min_cell_x, max_cell_x + 1)
                for cell_y in range(min_cell_y, max_cell_y + 1)]
    
    def insert(self, obj):
        """Insert an object into the grid."""
        # If object already in grid, remove it first to avoid processing it twice
        if obj in self.object_cells:
            for cell in self.object_cells[obj]:
                if cell in self.grid and obj in self.grid[cell]:
                    self.grid[cell].remove(obj)
            
        # Track which cells this object is inserted into
        cells = set()
        hitboxes = obj.hitboxes()
        
        for hitbox in hitboxes:
            for cell in self._get_cells_for_hitbox(hitbox):
                if cell not in self.grid:
                    self.grid[cell] = []
                self.grid[cell].append(obj)
                cells.add(cell)
        
        # Store the cells this object is in
        self.object_cells[obj] = cells
    
    def query(self, hitbox):
        """Find all objects that could potentially collide with the given hitbox."""
        cells = self._get_cells_for_hitbox(hitbox)
        
        # Use a set for faster lookups and to avoid duplicates
        result = set()
        for cell in cells:
            if cell in self.grid:
                result.update(self.grid[cell])
        
        return list(result)
    
    def clear(self):
        """Clear the grid."""
        self.grid.clear()
        self.object_cells.clear()
    
    def query_radius(self, x, y, radius):
        """Find all objects within a radius of the given point."""
        # Create a hitbox that encompasses the circle
        search_box = Hitbox(x - radius, y - radius, radius * 2, radius * 2)
        return self.query(search_box)

    def draw(self, color=(150, 150, 150)):
        """Draw grid for debugging purposes."""
        # Only draw cells with objects
        for cell_coords, objects in self.grid.items():
            if objects:
                cell_x, cell_y = cell_coords
                x, y = scale_to_display(cell_x * self.cell_size, cell_y * self.cell_size)
                width, height = scale_to_display(self.cell_size, self.cell_size)
                pygame.draw.rect(screen, color, (x, y, width, height), 1)