from ultralytics import YOLO

def train_model():
    model = YOLO('yolov8m-seg.pt')  # load a pretrained model
    model.train(data='config.yaml', epochs=100, imgsz=512, batch=4, device=0)

if __name__ == '__main__':
    train_model()
