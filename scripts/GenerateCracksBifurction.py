import numpy as np
import matplotlib.pyplot as plt

def generate_crack_image(file_path='cracks_image.png'):
    def draw_crack(ax, a, length=10, vertical_offset=512, max_bifurcations=3):
        # Randomizing parameters
        noise_level = np.random.uniform(10, 50)
        num_points = np.random.randint(20, 41)
        min_bifurcations = np.random.randint(0, 4)
        line_width = np.random.uniform(0.5, 3)  # Random line thickness

        x0, y0 = a
        # Adjust angle to make the crack go downwards
        angle = np.random.uniform(np.pi, 2 * np.pi)  # Angle between 180 to 360 degrees

        x1 = x0 + length * np.cos(angle)
        y1 = y0 + length * np.sin(angle)

        t = np.linspace(0, 1, num_points)
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t

        noise = np.random.normal(0, noise_level, num_points)
        x += noise

        num_bifurcations = np.random.randint(min_bifurcations, max_bifurcations + 1)
        bifurcation_indices = np.random.choice(range(1, num_points - 1), size=num_bifurcations, replace=False)

        ax.plot(x, y, color='black', alpha=0.8, linewidth=line_width)  # Use random line width

        for index in bifurcation_indices:
            bif_angle = np.random.uniform(np.pi, 2 * np.pi)
            bif_length = np.random.uniform(length*0.1, length*0.3)
            bx = x[index] + bif_length * np.cos(bif_angle)
            by = y[index] + bif_length * np.sin(bif_angle)

            bt = np.linspace(0, 1, num_points // 5)
            bx_line = x[index] + (bx - x[index]) * bt
            by_line = y[index] + (by - y[index]) * bt

            bx_noise = np.random.normal(0, noise_level / 2, num_points // 5)
            bx_line += bx_noise

            ax.plot(bx_line, by_line, color='black', alpha=0.8, linewidth=line_width * 0.8)  # Slightly thinner for bifurcations

    # Create the figure with fixed dimensions
    fig = plt.figure(figsize=(20, 20), dpi=102.4)
    ax = fig.add_axes([0, 0, 1, 1])  # This should ensure there are no margins
    ax.set_aspect('equal')

    regions = [682/2, 2048/2, 2048 - 682/2]
    crack_length = 1024  # Set a fixed crack length

    for region in regions:
        # Adjust y starting position to be from the top
        draw_crack(ax, (region, 2048), length=crack_length, vertical_offset=-1024, max_bifurcations=5)

    ax.set_xlim(0, 2048)
    ax.set_ylim(0, 2048)
    ax.axis('off')

    # Save the figure
    plt.savefig(file_path, dpi=102.4, transparent=True)
    plt.close(fig)  # Close the figure to free memory

# Use of the function
generate_crack_image('Grietas/defect0.png')
