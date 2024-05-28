from ultralytics import YOLO
import cv2
import numpy as np

def process_image(img, model):
    H, W = img.shape[:2]
    results = model(img)
    output = img.copy()
    for result in results:
        if result.masks is not None:  # Check if masks are not None
            for mask in result.masks.data:
                mask = mask.cpu().numpy()
                mask = cv2.resize(mask, (W, H))
                colored_mask = np.zeros_like(img, dtype=np.uint8)
                colored_mask[mask > 0.5] = [0, 0, 255]  # Red mask
                output = cv2.addWeighted(output, 1, colored_mask, 0.7, 0)  # Blend with alpha=0.7
    return output


def process_video(video_path, model):
    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('image_segmentation_yolov8/test_data/test_video_good_labels.avi', fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        processed_frame = process_image(frame, model)
        out.write(processed_frame)
    cap.release()
    out.release()

model_path = r'image_segmentation_yolov8\runs\segment\train_Good_labels_yolov8_medium_backbone\weights\best.pt'
file_path = r'image_segmentation_yolov8\test_data\test_video.mp4'  # Change this to 'input.mp4' for video or another image name

model = YOLO(model_path)

if file_path.endswith('.png'):
    img = cv2.imread(file_path)
    processed_img = process_image(img, model)
    cv2.imshow('Processed Image', processed_img)
    cv2.imwrite('test_data/demo_video/processed_output.png', processed_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
elif file_path.split('.')[-1] in ['mp4', 'avi', 'mov', 'mkv']:  # add other video formats as needed
    process_video(file_path, model)
else:
    print("Unsupported file format")