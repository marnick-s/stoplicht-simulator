from lib.spatial.region import Region
from lib.screen import screen, scale_to_display
import pygame

class QuadNode:
    def __init__(self, boundary, capacity=10):
        self.boundary = boundary  # Region
        self.capacity = capacity
        self.objects = []  # List of tuples (Hitbox, object)
        self.divided = False
        self.northeast = None
        self.northwest = None
        self.southeast = None
        self.southwest = None
    
    def subdivide(self):
        x, y, w, h = self.boundary.x, self.boundary.y, self.boundary.width, self.boundary.height
        hw, hh = w / 2, h / 2
        self.northeast = QuadNode(Region(x + hw, y, hw, hh), self.capacity)
        self.northwest = QuadNode(Region(x, y, hw, hh), self.capacity)
        self.southeast = QuadNode(Region(x + hw, y + hh, hw, hh), self.capacity)
        self.southwest = QuadNode(Region(x, y + hh, hw, hh), self.capacity)
        self.divided = True
        
        # Redistribute objects to children
        for hitbox, obj in self.objects[:]:
            # Try to insert in child nodes
            inserted = False
            for child in [self.northeast, self.northwest, self.southeast, self.southwest]:
                if child.boundary.contains(hitbox):
                    child.insert(hitbox, obj)
                    inserted = True
                    break
            
            # Keep object in this node if it couldn't be fully contained by any child
            if not inserted:
                continue  # Keep it in the current node
    
    def insert(self, hitbox, obj):
        # If hitbox doesn't intersect boundary, don't insert
        if not self.boundary.intersects(hitbox):
            return False
        
        # If we have space or aren't divided yet, add the object
        if len(self.objects) < self.capacity and not self.divided:
            self.objects.append((hitbox, obj))
            return True
        
        # If we don't have space and aren't divided, subdivide
        if not self.divided:
            self.subdivide()
        
        # Find a child that completely contains the hitbox
        for child in [self.northeast, self.northwest, self.southeast, self.southwest]:
            if child.boundary.contains(hitbox):
                return child.insert(hitbox, obj)
        
        # No child fully contains it, so keep it at this level
        self.objects.append((hitbox, obj))
        return True
    
    def query(self, search_range, found=None):
        if found is None:
            found = []
        
        # Early exit if no possible intersection
        if not self.boundary.intersects(search_range):
            return found
        
        # Check objects at this level
        for hitbox, obj in self.objects:
            if search_range.collides_with(hitbox):
                found.append((hitbox, obj))
        
        # If divided, check children
        if self.divided:
            self.northeast.query(search_range, found)
            self.northwest.query(search_range, found)
            self.southeast.query(search_range, found)
            self.southwest.query(search_range, found)
        
        return found
    
    def draw(self):
        x, y = scale_to_display(self.boundary.x, self.boundary.y)
        width, height = scale_to_display(self.boundary.width, self.boundary.height)
        pygame.draw.rect(screen, (50, 50, 50), pygame.Rect(x, y, width, height), 1)
        if self.divided:
            self.northeast.draw()
            self.northwest.draw()
            self.southeast.draw()
            self.southwest.draw()