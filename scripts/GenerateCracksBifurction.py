import numpy as np
import matplotlib.pyplot as plt

def draw_crack(ax, start_point, length=10, noise_level_range=(10, 30), 
               num_points_range=(10, 40), min_bifurcations_range=(0, 4), 
               max_bifurcations=5, line_width_range=(0.5, 4)):
    """
    Draws a single crack on the provided axis.

    Parameters:
    - ax: The matplotlib axis to draw on.
    - start_point: The starting point (x, y) of the crack.
    - length: The length of the crack.
    - noise_level_range: Tuple for the range of noise levels.
    - num_points_range: Tuple for the range of number of points.
    - min_bifurcations_range: Tuple for the range of minimum bifurcations.
    - max_bifurcations: Maximum number of bifurcations.
    - line_width_range: Tuple for the range of line widths.
    """
    noise_level = np.random.uniform(*noise_level_range)
    num_points = np.random.randint(*num_points_range)
    min_bifurcations = np.random.randint(*min_bifurcations_range)
    line_width = np.random.uniform(*line_width_range)

    x0, y0 = start_point
    angle = np.random.uniform(np.pi, 2 * np.pi)

    x1 = x0 + length * np.cos(angle)
    y1 = y0 + length * np.sin(angle)

    t = np.linspace(0, 1, num_points)
    x = x0 + (x1 - x0) * t
    y = y0 + (y1 - y0) * t

    noise = np.random.normal(0, noise_level, num_points)
    x += noise

    num_bifurcations = np.random.randint(min_bifurcations, max_bifurcations + 1)
    bifurcation_indices = np.random.choice(range(1, num_points - 1), size=num_bifurcations, replace=False)

    ax.plot(x, y, color='black', alpha=0.8, linewidth=line_width)

    for index in bifurcation_indices:
        bif_angle = np.random.uniform(np.pi, 2 * np.pi)
        bif_length = np.random.uniform(length * 0.1, length * 0.3)
        bx = x[index] + bif_length * np.cos(bif_angle)
        by = y[index] + bif_length * np.sin(bif_angle)

        bt = np.linspace(0, 1, num_points // 5)
        bx_line = x[index] + (bx - x[index]) * bt
        by_line = y[index] + (by - y[index]) * bt

        bx_noise = np.random.normal(0, noise_level / 2, num_points // 5)
        bx_line += bx_noise

        ax.plot(bx_line, by_line, color='black', alpha=0.8, linewidth=line_width * 0.8)

def generate_crack_image(file_path='cracks_image.png', image_size=(2048, 2048), 
                         crack_regions=None, crack_length=1024, 
                         max_bifurcations=5):
    """
    Generates an image with cracks and saves it to the specified file path.

    Parameters:
    - file_path: Path to save the generated image.
    - image_size: Size of the image (width, height).
    - crack_regions: List of x-coordinates for the starting points of cracks.
    - crack_length: Length of each crack.
    - max_bifurcations: Maximum number of bifurcations for each crack.
    """
    if crack_regions is None:
        crack_regions = [image_size[0] * 0.25, image_size[0] * 0.5, image_size[0] * 0.75]

    fig = plt.figure(figsize=(image_size[0] / 102.4, image_size[1] / 102.4), dpi=102.4)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_aspect('equal')

    for region in crack_regions:
        draw_crack(ax, (region, image_size[1]), length=crack_length, max_bifurcations=max_bifurcations)

    ax.set_xlim(0, image_size[0])
    ax.set_ylim(0, image_size[1])
    ax.axis('off')

    plt.savefig(file_path, dpi=102.4, transparent=True)
    plt.close(fig)


# Use of the function
generate_crack_image('Grietas/defect0.png')
