import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from shapely.geometry import Point, Polygon
import math

# --- Constants ---
TILE_SIZE = 600  # mm
SPRINKLER_RADIUS = 1500  # mm
SPRINKLER_WALL_CLEARANCE = 500  # mm
SPRINKLER_MIN_SPACING = 1200  # mm

# --- Visualization Colors ---
COLOR_LIGHT_SOURCE = '#FFC300'  # A bright yellow for the light panel itself
COLOR_ILLUMINATED = '#FFFACD'   # A lighter yellow for illuminated tiles
COLOR_SPRINKLER_DOT = 'red'
COLOR_SPRINKLER_COVERAGE = 'blue'
COLOR_GRID_LINES = '#CCCCCC'
COLOR_ROOM_BOUNDARY = 'black'
COLOR_OUTSIDE_ROOM = 'white'
COLOR_UNLIT_TILE = '#F0F0F0'  # A very light grey for valid but unlit tiles


class RoomLayoutGenerator:
    def __init__(self, room_name, room_vertices):
        self.room_name = room_name
        self.room_polygon = Polygon(room_vertices)
        
        min_x, min_y, max_x, max_y = self.room_polygon.bounds
        self.cols = math.ceil(max_x / TILE_SIZE)
        self.rows = math.ceil(max_y / TILE_SIZE)
        
        self.grid = np.zeros((self.rows, self.cols), dtype=int)
        self.sprinklers = []
        self.lights = []
        
        self._initialize_grid()

    def _get_tile_center(self, r, c):
        x = c * TILE_SIZE + TILE_SIZE / 2
        y = r * TILE_SIZE + TILE_SIZE / 2
        return (x, y)

    def _initialize_grid(self):
        for r in range(self.rows):
            for c in range(self.cols):
                center_x, center_y = self._get_tile_center(r, c)
                if self.room_polygon.contains(Point(center_x, center_y)):
                    self.grid[r, c] = 1  # Inside

    def place_sprinklers(self):
        candidates = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r, c] == 1:
                    center_x, center_y = self._get_tile_center(r, c)
                    center_point = Point(center_x, center_y)
                    if self.room_polygon.boundary.distance(center_point) >= SPRINKLER_WALL_CLEARANCE:
                        candidates.append(((r, c), (center_x, center_y)))

        placed_sprinklers_coords = []
        for (r, c), (cx, cy) in candidates:
            is_valid_placement = True
            for _, (pcx, pcy) in placed_sprinklers_coords:
                if math.hypot(cx - pcx, cy - pcy) < SPRINKLER_MIN_SPACING:
                    is_valid_placement = False
                    break
            if is_valid_placement:
                self.grid[r, c] = 2
                self.sprinklers.append(((r, c), (cx, cy)))
                placed_sprinklers_coords.append(((r, c), (cx, cy)))
        
        print(f"[{self.room_name}] Placed {len(self.sprinklers)} sprinklers.")

    def place_lights(self):
        unlit_cells = set(tuple(coord) for coord in np.argwhere(self.grid == 1))
        
        while unlit_cells:
            best_candidate = None
            max_newly_covered = -1
            
            for r in range(self.rows):
                for c in range(self.cols):
                    if self.grid[r, c] == 1:
                        is_adjacent_to_light = False
                        for dr in [-1, 0, 1]:
                            for dc in [-1, 0, 1]:
                                if dr == 0 and dc == 0:
                                    continue
                                nr, nc = r + dr, c + dc
                                if 0 <= nr < self.rows and 0 <= nc < self.cols and self.grid[nr, nc] == 3:
                                    is_adjacent_to_light = True
                                    break
                            if is_adjacent_to_light:
                                break
                        if is_adjacent_to_light:
                            continue

                        newly_covered_count = 0
                        for dr in [-1, 0, 1]:
                            for dc in [-1, 0, 1]:
                                nr, nc = r + dr, c + dc
                                if (nr, nc) in unlit_cells:
                                    newly_covered_count += 1
                        
                        if newly_covered_count > max_newly_covered:
                            max_newly_covered = newly_covered_count
                            best_candidate = (r, c)
            
            if best_candidate is None:
                print(f"[{self.room_name}] Could not place more lights. {len(unlit_cells)} cells remain unlit.")
                break

            r, c = best_candidate
            self.grid[r, c] = 3
            self.lights.append(((r, c), self._get_tile_center(r, c)))

            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if (nr, nc) in unlit_cells:
                        unlit_cells.remove((nr, nc))

        print(f"[{self.room_name}] Placed {len(self.lights)} lights.")

    def visualize(self):
        fig, ax = plt.subplots(figsize=(self.cols / 1.5, self.rows / 1.5))
        ax.set_aspect('equal')

        illumination_grid = np.zeros_like(self.grid, dtype=bool)
        for (r, c), _ in self.lights:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols and self.grid[nr, nc] != 0:
                        illumination_grid[nr, nc] = True

        for r in range(self.rows):
            for c in range(self.cols):
                tile_state = self.grid[r, c]
                face_color = COLOR_OUTSIDE_ROOM
                if tile_state != 0:
                    if illumination_grid[r, c]:
                        face_color = COLOR_ILLUMINATED
                    else:
                        face_color = COLOR_UNLIT_TILE
                if tile_state == 3:
                    face_color = COLOR_LIGHT_SOURCE

                rect = patches.Rectangle(
                    (c * TILE_SIZE, r * TILE_SIZE), TILE_SIZE, TILE_SIZE,
                    linewidth=0.5, edgecolor=COLOR_GRID_LINES, facecolor=face_color
                )
                ax.add_patch(rect)

        room_x, room_y = self.room_polygon.exterior.xy
        ax.plot(room_x, room_y, color=COLOR_ROOM_BOUNDARY, linewidth=2.5, solid_capstyle='round')

        for (r, c), (cx, cy) in self.sprinklers:
            sprinkler_dot = patches.Circle((cx, cy), radius=60, color=COLOR_SPRINKLER_DOT, zorder=5)
            ax.add_patch(sprinkler_dot)

            coverage_circle = patches.Circle((cx, cy), radius=SPRINKLER_RADIUS,
                                             edgecolor=COLOR_SPRINKLER_COVERAGE,
                                             facecolor='none', linewidth=1.5, zorder=4)
            ax.add_patch(coverage_circle)

        ax.set_xlim(-TILE_SIZE, (self.cols + 1) * TILE_SIZE)
        ax.set_ylim(-TILE_SIZE, (self.rows + 1) * TILE_SIZE)
        ax.set_title(f'Sprinkler and Light Layout for {self.room_name}')
        ax.set_xlabel('Dimension (mm)')
        ax.set_ylabel('Dimension (mm)')
        plt.gca().invert_yaxis()
        plt.tight_layout()

        # ✅ Save to file (instead of showing, which doesn't work in WSL)
        filename = f"{self.room_name.replace(' ', '_')}_layout.png"
        plt.savefig(filename, dpi=300)
        print(f"[{self.room_name}] Layout saved as '{filename}'.")


# --- Main Execution Block ---
if __name__ == '__main__':
    room1_vertices = [
        (0, 0), (6000, 0), (6000, 3000), 
        (3600, 3000), (3600, 4800), (0, 4800), (0, 0)
    ]

    room2_vertices = [
        (0, 0), (3000, 0), (3000, 4800), (0, 4800), (0, 0)
    ]

    layout1 = RoomLayoutGenerator("Room 1", room1_vertices)
    layout1.place_sprinklers()
    layout1.place_lights()
    layout1.visualize()

    layout2 = RoomLayoutGenerator("Room 2", room2_vertices)
    layout2.place_sprinklers()
    layout2.place_lights()
    layout2.visualize()
