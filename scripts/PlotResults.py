# Import all necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read the results from the training procedure
results_df=pd.read_csv("train_yolov8_nano_backbone/results.csv")
# Get the names of the different columns
col_names=results_df.columns.to_list()

# Remove all spaces on the name of the dataframe headers
rename_mapping=[name.strip() for name in col_names]

# Assign each new name to the original name
rename_dict={}

# Ease the naming of the columns removing excessive words
for idx,name in enumerate(rename_mapping):
    if (rename_mapping[idx].startswith("metrics/")):
        rename_dict[col_names[idx]]=name[8:]
    elif ("cls" in rename_mapping[idx]):
        results_df=results_df.drop([col_names[idx]],axis=1)
    elif ("dfl" in rename_mapping[idx]):
        results_df=results_df.drop([col_names[idx]],axis=1)
    elif (rename_mapping[idx].startswith("train/")):
        rename_dict[col_names[idx]]=name[6:]
    elif (rename_mapping[idx].startswith("lr/")):
        results_df=results_df.drop([col_names[idx]],axis=1)
    else:
        rename_dict[col_names[idx]]=name

# Change the name of the columns of the dataframe
results_df.rename(rename_dict,axis=1,inplace=True)

# Obtain the f1 score for each epoch
results_df['f1_score(B)']=(2*results_df['recall(B)']*results_df['precision(B)'])/(results_df['recall(B)']+results_df['precision(B)'])
results_df['f1_score(M)']=(2*results_df['recall(M)']*results_df['precision(M)'])/(results_df['recall(M)']+results_df['precision(M)'])
print(results_df.columns.tolist())

# Create subplots for all
fig, axes = plt.subplots(nrows=4, ncols=4, figsize=(20, 12),constrained_layout=True,sharey=False)

# Flatten the axes array for easy iteration
axes = axes.flatten()

# Plot all the losses together with the same y axis
axes[0].plot(results_df['epoch'], results_df['box_loss'], label="box_loss", color="red")
#axes[0].set_title("box_loss")
axes[0].legend()
axes[0].set_ylim([0,1.5])

axes[1].plot(results_df['epoch'], results_df['seg_loss'], label="seg_loss", color="red")
#axes[1].set_title("seg_loss")
axes[1].legend()
axes[1].set_ylim([0,1.5])

axes[2].plot(results_df['epoch'], results_df['val/box_loss'], label="val/box_loss", color="red")
#axes[2].set_title("val/box_loss")
axes[2].legend()
axes[2].set_ylim([0,1.5])

axes[3].plot(results_df['epoch'], results_df['val/seg_loss'], label="val/seg_loss", color="red")
#axes[3].set_title("val/seg_loss")
axes[3].legend()
axes[3].set_ylim([0,1.5])

# Plot all the metrics together with the same y axis
axes[4].plot(results_df['epoch'], results_df['precision(B)'], label='precision(B)', color="blue")
#axes[0].set_title("box_loss")
axes[4].legend()
axes[4].set_ylim([0,1])

axes[5].plot(results_df['epoch'], results_df['precision(M)'], label='precision(M)', color="blue")
#axes[1].set_title("seg_loss")
axes[5].legend()
axes[5].set_ylim([0,1])

axes[6].plot(results_df['epoch'], results_df['recall(B)'], label='recall(B)', color="blue")
#axes[2].set_title("val/box_loss")
axes[6].legend()
axes[6].set_ylim([0,1])

axes[7].plot(results_df['epoch'], results_df['recall(M)'], label='recall(M)', color="blue")
#axes[3].set_title("val/seg_loss")
axes[7].legend()
axes[7].set_ylim([0,1])

axes[8].plot(results_df['epoch'], results_df['mAP50(B)'], label='mAP50(B)', color="blue")
#axes[0].set_title("box_loss")
axes[8].legend()
axes[8].set_ylim([0,1])

axes[9].plot(results_df['epoch'], results_df['mAP50(M)'], label='mAP50(M)', color="blue")
#axes[1].set_title("seg_loss")
axes[9].legend()
axes[9].set_ylim([0,1])

axes[10].plot(results_df['epoch'], results_df['mAP50-95(B)'], label='mAP50-95(B)', color="blue")
#axes[2].set_title("val/box_loss")
axes[10].legend()
axes[10].set_ylim([0,1])

axes[11].plot(results_df['epoch'], results_df['mAP50-95(M)'], label='mAP50-95(M)', color="blue")
#axes[3].set_title("val/seg_loss")
axes[11].legend()
axes[11].set_ylim([0,1])

# Generate plot for the f1score for the prediction and data obtained
axes[13].plot(results_df['epoch'], results_df['f1_score(B)'], label='f1_score(B)', color="black")
#axes[2].set_title("val/box_loss")
axes[13].legend()
axes[13].set_ylim([0,1])

axes[14].plot(results_df['epoch'], results_df['f1_score(M)'], label='f1_score(M)', color="black")
#axes[3].set_title("val/seg_loss")
axes[14].legend()
axes[14].set_ylim([0,1])

# Set to off those axis not used from last row
axes[12].set_axis_off()
axes[15].set_axis_off()

# Insert a title to the overall figure
fig.suptitle("YoloV8 medium results evaluation")

# Adjust layout
plt.tight_layout()

# Save the ordered plot with colors
plt.savefig(r"results_filtered.png")

# Show results obtained
plt.show()