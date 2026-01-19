import matplotlib.pyplot as plt

def draw_kolam(rows, cols):
    """
    Generates and displays a symmetric Kolam design based on a dot grid.

    Args:
        rows (int): The number of rows in the dot grid.
        cols (int): The number of columns in the dot grid.
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    # --- 1. The Design Principle: The Dot Grid (Pulli) ---
    # We represent the dots as points on a Cartesian plane.
    dots_x = [j for i in range(rows) for j in range(cols)]
    dots_y = [i for i in range(rows) for j in range(cols)]
    ax.scatter(dots_x, dots_y, color='black', s=100) # s is size

    # --- 2. The Design Principle: The Path ---
    # This base path defines the curve for one quadrant of the design.
    # The coordinates are carefully chosen to loop around the dots.
    # It starts from the center and moves outwards.
    base_path_x = [2, 1.5, 1, 1, 1.5, 2, 2.5, 3, 3, 3.5, 4, 4, 3.5, 3, 2.5, 2]
    base_path_y = [2, 2.5, 3, 3.5, 4, 4, 3.5, 3, 2.5, 2, 1.5, 1, 1, 0.5, 0, 0]

    # --- 3. The Design Principle: Symmetry and Repetition ---
    # We generate the full design by rotating the base path 4 times.
    center_x, center_y = (cols - 1) / 2.0, (rows - 1) / 2.0

    for i in range(4):
        # Rotation formula:
        # x' = x_c + (x - x_c) * cos(a) - (y - y_c) * sin(a)
        # y' = y_c + (x - x_c) * sin(a) + (y - y_c) * cos(a)
        # For 0, 90, 180, 270 degrees, this simplifies greatly.
        
        # Ensure variables are always defined (linters can flag possibly unbound variables)
        rotated_x = []
        rotated_y = []
        
        if i == 0: # 0 degrees
            rotated_x = base_path_x
            rotated_y = base_path_y
        elif i == 1: # 90 degrees
            rotated_x = [center_x - (y - center_y) for y in base_path_y]
            rotated_y = [center_y + (x - center_x) for x in base_path_x]
        elif i == 2: # 180 degrees
            rotated_x = [center_x - (x - center_x) for x in base_path_x]
            rotated_y = [center_y - (y - center_y) for y in base_path_y]
        elif i == 3: # 270 degrees
            rotated_x = [center_x + (y - center_y) for y in base_path_y]
            rotated_y = [center_y - (x - center_x) for x in base_path_x]

        # Draw the transformed path
        ax.plot(rotated_x, rotated_y, color='#d9534f', linewidth=3)


    # --- Final Polish of the Visuals ---
    ax.set_aspect('equal', adjustable='box')
    plt.title('Generated 5x5 Pulli Kolam', fontsize=16)
    plt.gca().invert_yaxis() # Invert y-axis to match common grid representations
    plt.axis('off') # Hide the axes for a cleaner look
    plt.show()

# --- Run the generator ---
if __name__ == "__main__":
    # The Kolam is designed for an odd-numbered grid to have a clear center
    draw_kolam(rows=5, cols=5)