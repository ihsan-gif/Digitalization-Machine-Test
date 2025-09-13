# Ceiling Layout Generator

This Python script automates the process of generating a ceiling layout for **sprinklers** and **lights**, based on a specific set of architectural and safety constraints. It calculates the optimal placement for these fixtures and visualizes the final layout using `matplotlib`.



---

## ✨ Features

### 🧱 Custom Room Geometry
- Supports complex room shapes (e.g., L-shaped rooms) using vertex coordinates.
- Uses the `shapely` library for precise geometric calculations.

### 🔥 Rule-Based Sprinkler Placement
- Places sprinklers at the center of **600x600 mm** ceiling tiles.
- Ensures:
  - **Minimum wall clearance** of **500 mm**
  - **Minimum spacing** of **1200 mm** between any two sprinklers
  - **Maximum spacing** of **1500 mm** between connected sprinklers (to ensure networked coverage)
- Prevents isolated sprinkler placements.

### 💡 Optimized Light Placement
- Ensures **all valid tiles** in the room are illuminated.
- No two lights are adjacent (horizontal, vertical, or diagonal).
- Ensures **no light shares a tile with a sprinkler**.

### 📊 Detailed Visualization
- Generates a 2D plot with the following:
  - Room boundary (black)
  - Illuminated tiles (light yellow)
  - Lights (solid yellow squares)
  - Sprinklers (red dots)
  - Sprinkler coverage (blue circle with 1.5m radius)

---

## 📦 Requirements

Install the required Python libraries:

```bash
pip install numpy matplotlib shapely
