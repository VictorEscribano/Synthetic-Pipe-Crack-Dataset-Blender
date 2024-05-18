from PIL import Image
import numpy as np

def random_scratches(template_path, output_size=(2048, 2048), num_scratches=50):
    # Load the template scratch image
    scratch_template = Image.open(template_path).convert("RGBA")
    
    # Create a new image with a transparent background
    new_image = Image.new("RGBA", output_size, (0, 0, 0, 0))
    
    # Define the region for the center-top part of the image
    # Assuming center-top refers to the top half, centered horizontally
    region_width = output_size[0] // 2
    region_height = output_size[1] // 2
    region_start_x = 0
    region_start_y = 0  # Start at the top of the image
    
    # Generate random scratches in the center-top region
    for _ in range(num_scratches):
        # Randomly transform the scratch
        angle = np.random.uniform(0, 180)
        scale = np.random.uniform(3, 6)
        transformed_scratch = scratch_template.rotate(angle, expand=True).resize(
            (int(scratch_template.width * scale), int(scratch_template.height * scale)),
            Image.ANTIALIAS,
        )
        
        # Choose a random position within the center-top region
        max_x = region_start_x + region_width - transformed_scratch.width
        max_y = region_start_y + region_height - transformed_scratch.height
        pos_x = np.random.randint(region_start_x, max(max_x, region_start_x + 1))
        pos_y = np.random.randint(region_start_y, max(max_y, region_start_y + 1))
        
        # Paste the transformed scratch onto the background
        new_image.paste(transformed_scratch, (pos_x, pos_y), transformed_scratch)

    # Save the result
    new_image.save("Grietas/random_scratches_output.png", "PNG")

# Path to your scratch template
template_path = 'brushes/alpha_scratch_1.png'


# Run the function
random_scratches(template_path, num_scratches=20)
