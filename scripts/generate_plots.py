import pandas as pd
import matplotlib.pyplot as plt

# Load the data
main_path = r'image_segmentation_yolov8\runs\segment\train_only_REAL_dataset_v8medium'
file_path = main_path + r'\results.csv'
data = pd.read_csv(file_path)

# Strip whitespace from column names
data.columns = data.columns.str.strip()

# List of columns to plot in the specified order
ordered_columns = [
    "train/box_loss", "train/seg_loss", 
    "val/box_loss", "val/seg_loss",
    "metrics/precision(B)", "metrics/recall(B)", 
    "metrics/precision(M)", "metrics/recall(M)", 
    "metrics/mAP50(B)", "metrics/mAP50-95(B)", 
    "metrics/mAP50(M)", "metrics/mAP50-95(M)"
]

# Create subplots
fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(25, 15), sharey=False)

# Flatten the axes array for easy iteration
axes = axes.flatten()

# Colors for different metrics
color_map = {
    "(B)": "red",
    "(M)": "blue"
}

# Plot each column in the specified order
for idx, column in enumerate(ordered_columns):
    color = "black"  # Default color
    for key, col in color_map.items():
        if key in column:
            color = col
            break
    axes[idx].plot(data['epoch'], data[column], label=column, color=color)
    axes[idx].set_title(column)
    axes[idx].legend()

# Adjust layout
plt.tight_layout()

# Save the ordered plot with colors
plt.savefig(main_path+ r"\results_filtered.png")

plt.show()
