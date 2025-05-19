import pygame
import numpy as np
from lib.collidable_object import Hitbox
from lib.screen import screen, scale_to_display

class SpatialHashGrid:
    """
    An optimized spatial hash grid for efficient collision detection.
    Uses numpy arrays for fast grid operations and caches object bounds.
    """
   
    def __init__(self, cell_size=40):
        self.cell_size = cell_size
        self.grid = {}  # Dictionary mapping cell coordinates to objects
        self.object_cells = {}  # Maps objects to their cell coordinates
        self.object_bounds = {}  # Cache object bounds for faster queries
        self.reusable_cells_set = set()  # Reusable set to avoid recreating for each query
    
    def _get_cell_coords(self, x, y):
        """Convert world coordinates to grid cell coordinates using efficient integer division."""
        return int(x // self.cell_size), int(y // self.cell_size)
    
    def _get_cells_for_bounds(self, min_x, min_y, max_x, max_y):
        """Get all cells that an object's bounds overlap using vectorized operations."""
        min_cell_x, min_cell_y = self._get_cell_coords(min_x, min_y)
        max_cell_x, max_cell_y = self._get_cell_coords(max_x, max_y)
        
        # Clear and reuse set
        self.reusable_cells_set.clear()
        
        # Use generator expression instead of list comprehension to avoid creating a list
        for cell_x in range(min_cell_x, max_cell_x + 1):
            for cell_y in range(min_cell_y, max_cell_y + 1):
                self.reusable_cells_set.add((cell_x, cell_y))
                
        return self.reusable_cells_set
    
    def insert(self, obj):
        """Insert an object into the grid with bounds caching for repeated lookups."""
        # Calculate and cache the object's overall bounds
        hitboxes = obj.hitboxes()
        if not hitboxes:
            return
            
        # Calculate overall bounds
        min_x = min(hb.x for hb in hitboxes)
        min_y = min(hb.y for hb in hitboxes)
        max_x = max(hb.x + hb.width for hb in hitboxes)
        max_y = max(hb.y + hb.height for hb in hitboxes)
        
        # Store bounds for later queries
        self.object_bounds[obj] = (min_x, min_y, max_x, max_y)
        
        # Get cells this object belongs to
        cells = self._get_cells_for_bounds(min_x, min_y, max_x, max_y)
        
        # If object already in grid, update its cells
        if obj in self.object_cells:
            old_cells = self.object_cells[obj]
            # Remove from cells it's no longer in
            for cell in old_cells:
                if cell in self.grid and obj in self.grid[cell] and cell not in cells:
                    self.grid[cell].remove(obj)
                    # Clean up empty cell entries
                    if not self.grid[cell]:
                        del self.grid[cell]
        
        # Add to new cells
        for cell in cells:
            if cell not in self.grid:
                self.grid[cell] = []
            if obj not in self.grid[cell]:  # Avoid duplicates
                self.grid[cell].append(obj)
        
        # Store updated cell list
        self.object_cells[obj] = set(cells)  # Make a copy of the set
    
    def query(self, hitbox):
        """Find all objects that could potentially collide with the given hitbox."""
        # Use object bounds from hitbox
        cells = self._get_cells_for_bounds(
            hitbox.x, hitbox.y, 
            hitbox.x + hitbox.width, 
            hitbox.y + hitbox.height
        )
        
        # Use a set for faster lookups and to avoid duplicates
        result = set()
        for cell in cells:
            if cell in self.grid:
                result.update(self.grid[cell])
        
        return list(result)
    
    def query_radius(self, x, y, radius):
        """Find all objects within a radius of the given point."""
        # Create a bounds that encompasses the circle
        return self.query(Hitbox(x - radius, y - radius, radius * 2, radius * 2))
    
    def clear(self):
        """Clear the grid and associated caches."""
        self.grid.clear()
        self.object_cells.clear()
        self.object_bounds.clear()
        self.reusable_cells_set.clear()
    
    def bulk_insert(self, objects):
        """Insert multiple objects in a single batch operation."""
        for obj in objects:
            self.insert(obj)
    
    def remove(self, obj):
        """Remove an object from the grid."""
        if obj in self.object_cells:
            for cell in self.object_cells[obj]:
                if cell in self.grid and obj in self.grid[cell]:
                    self.grid[cell].remove(obj)
                    # Clean up empty cells
                    if not self.grid[cell]:
                        del self.grid[cell]
            del self.object_cells[obj]
        
        if obj in self.object_bounds:
            del self.object_bounds[obj]
    
    def draw(self, color=(150, 150, 150)):
        """Draw grid for debugging purposes."""
        # Only draw cells with objects
        for cell_coords, objects in self.grid.items():
            if objects:
                cell_x, cell_y = cell_coords
                x, y = scale_to_display(cell_x * self.cell_size, cell_y * self.cell_size)
                width, height = scale_to_display(self.cell_size, self.cell_size)
                pygame.draw.rect(screen, color, (x, y, width, height), 1)