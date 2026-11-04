# %% [markdown]
# # Practical 8: Comparative Study of Object Detection Models (Pascal VOC) - CO1, CO2, CO3
# **Aim:** Detect multiple objects in images and videos with **R-CNN, Fast R-CNN, YOLOv8 and SSD MobileNet**
# and compare detection accuracy (mAP), inference speed (FPS) and computational cost.
#
# **How the four models are obtained**
# * **YOLOv8** (Ultralytics) and **SSD MobileNet** (torchvision SSDlite320) are ready-made COCO-pretrained detectors.
# * No maintained *standalone* pre-trained R-CNN / Fast R-CNN exists, so both are built **in their original
#   pipeline style** on top of the COCO-pretrained Faster R-CNN weights (backbone + box head):
#   * **R-CNN style:** Selective Search proposals -> every region is cropped, warped to a fixed size and sent
#     through the CNN **separately** (one CNN pass per region) -> classify + refine box.
#   * **Fast R-CNN style:** Selective Search proposals -> the CNN runs **once** on the whole image -> RoI pooling
#     extracts each region from the shared feature map -> classify + refine box.
#   This reproduces exactly what differs between the two papers (per-region vs shared computation).
# * All models are trained on COCO; predictions are mapped to the 20 Pascal VOC classes before computing mAP.
#
# Install once (Anaconda Prompt):
# `pip install torch torchvision ultralytics torchmetrics pycocotools opencv-contrib-python`
# (use **opencv-contrib-python**, not opencv-python: Selective Search lives in the contrib module)

# %%
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2
import torch
import torchvision
from torchvision import transforms as T
from torchvision.datasets import VOCDetection
from torchvision.ops import batched_nms
from torchmetrics.detection import MeanAveragePrecision
from ultralytics import YOLO

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Device:", device)

N_IMAGES = 30        # VOC images used for evaluation (same images for every model); raise on a GPU
MAX_PROPS = 100      # Selective Search proposals kept per image (R-CNN / Fast R-CNN)
REGION = 224         # R-CNN warps every region to REGION x REGION
SCORE_T = 0.3        # score threshold

# %% [markdown]
# ## 1. Load and pre-process Pascal VOC (VOC2007 val split, ~450 MB download the first time)

# %%
VOC_CLASSES = ["aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
               "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa",
               "train", "tvmonitor"]
VOC_TO_COCO_NAME = {"aeroplane": "airplane", "diningtable": "dining table", "motorbike": "motorcycle",
                    "pottedplant": "potted plant", "sofa": "couch", "tvmonitor": "tv"}
COCO_NAME_TO_VOC = {VOC_TO_COCO_NAME.get(c, c): i for i, c in enumerate(VOC_CLASSES)}

voc = VOCDetection(root="./data", year="2007", image_set="val", download=True)

def parse_target(ann):
    objs = ann["annotation"]["object"]
    objs = objs if isinstance(objs, list) else [objs]
    boxes, labels = [], []
    for o in objs:
        if int(o.get("difficult", 0)):
            continue
        b = o["bndbox"]
        boxes.append([float(b["xmin"]), float(b["ymin"]), float(b["xmax"]), float(b["ymax"])])
        labels.append(VOC_CLASSES.index(o["name"]))
    return dict(boxes=torch.tensor(boxes, dtype=torch.float32).reshape(-1, 4),
                labels=torch.tensor(labels, dtype=torch.int64))

samples = [(voc[i][0].convert("RGB"), parse_target(voc[i][1])) for i in range(N_IMAGES)]
print("Loaded", len(samples), "images")

# %% [markdown]
# ## 2. Load pre-trained networks

# %%
# COCO-pretrained Faster R-CNN: its backbone + RoI box head are reused for the R-CNN / Fast R-CNN pipelines
frcnn_w = torchvision.models.detection.FasterRCNN_ResNet50_FPN_Weights.DEFAULT
frcnn = torchvision.models.detection.fasterrcnn_resnet50_fpn(weights=frcnn_w, box_score_thresh=SCORE_T).to(device).eval()
frcnn_cats = frcnn_w.meta["categories"]

# SSD MobileNet (SSDlite320 + MobileNetV3-Large, COCO)
ssd_w = torchvision.models.detection.SSDLite320_MobileNet_V3_Large_Weights.DEFAULT
ssd = torchvision.models.detection.ssdlite320_mobilenet_v3_large(weights=ssd_w, score_thresh=SCORE_T).to(device).eval()
ssd_cats = ssd_w.meta["categories"]

# YOLOv8 nano (COCO) - weights download automatically
yolo = YOLO("yolov8n.pt")
yolo_cats = [yolo.names[i] for i in range(len(yolo.names))]

# %% [markdown]
# ## 3. Helpers: COCO -> VOC mapping and Selective Search proposals

# %%
to_tensor = T.ToTensor()

def to_voc_pred(boxes, scores, names):
    """Keep only detections whose COCO class exists in VOC and re-label them with VOC ids."""
    kb, ks, kl = [], [], []
    for b, s, n in zip(boxes, scores, names):
        if n in COCO_NAME_TO_VOC:
            kb.append(list(map(float, b))); ks.append(float(s)); kl.append(COCO_NAME_TO_VOC[n])
    if not kb:
        return dict(boxes=torch.zeros((0, 4)), scores=torch.zeros(0), labels=torch.zeros(0, dtype=torch.int64))
    return dict(boxes=torch.tensor(kb), scores=torch.tensor(ks), labels=torch.tensor(kl, dtype=torch.int64))

def selective_search(img, max_props=MAX_PROPS):
    """Region proposals (x1, y1, x2, y2) in original image coordinates."""
    bgr = np.ascontiguousarray(np.array(img)[:, :, ::-1])
    scale = min(1.0, 500.0 / max(bgr.shape[:2]))                # work on a smaller image for speed
    small = cv2.resize(bgr, None, fx=scale, fy=scale) if scale < 1 else bgr
    ss = cv2.ximgproc.segmentation.createSelectiveSearchSegmentation()
    ss.setBaseImage(small)
    ss.switchToSelectiveSearchFast()
    rects = ss.process()
    boxes = np.array([[x, y, x + w, y + h] for x, y, w, h in rects if w >= 20 and h >= 20],
                     dtype=np.float32)[:max_props] / scale
    return boxes

# %% [markdown]
# ## 4. The four detectors (each takes a PIL image and returns boxes / scores / VOC labels)

# %%
# ---- SSD MobileNet and (for reference) end-to-end Faster R-CNN ---------------------------------
@torch.no_grad()
def predict_torchvision(model, cats, img):
    out = model([to_tensor(img).to(device)])[0]
    names = [cats[i] for i in out["labels"].cpu().tolist()]
    return to_voc_pred(out["boxes"].cpu().tolist(), out["scores"].cpu().tolist(), names)

# ---- Fast R-CNN style: ONE CNN pass, RoI pooling on shared features ------------------------------
@torch.no_grad()
def predict_fast_rcnn(img):
    props = selective_search(img)
    x = to_tensor(img).to(device)
    images, _ = frcnn.transform([x])                              # normalize + resize
    feats = frcnn.backbone(images.tensors)                        # <- single CNN forward pass
    rh = images.image_sizes[0][0] / x.shape[1]
    rw = images.image_sizes[0][1] / x.shape[2]
    scaled = torch.from_numpy(props).to(device) * torch.tensor([rw, rh, rw, rh], device=device)
    dets, _ = frcnn.roi_heads(feats, [scaled], images.image_sizes)   # RoI pooling + classify + box regression
    dets = frcnn.transform.postprocess(dets, images.image_sizes, [tuple(x.shape[-2:])])[0]
    names = [frcnn_cats[i] for i in dets["labels"].cpu().tolist()]
    return to_voc_pred(dets["boxes"].cpu().tolist(), dets["scores"].cpu().tolist(), names)

# ---- R-CNN style: one CNN pass PER region --------------------------------------------------------
@torch.no_grad()
def predict_rcnn(img):
    props = selective_search(img)
    mean = torch.tensor(frcnn.transform.image_mean, device=device).view(3, 1, 1)
    std = torch.tensor(frcnn.transform.image_std, device=device).view(3, 1, 1)
    whole = torch.tensor([[0, 0, REGION, REGION]], dtype=torch.float32, device=device)
    boxes, scores, labels = [], [], []
    for x1, y1, x2, y2 in props:
        crop = img.crop((int(x1), int(y1), int(x2), int(y2))).resize((REGION, REGION))   # warp the region
        t = (to_tensor(crop).to(device) - mean) / std
        feats = frcnn.backbone(t[None])                                                   # <- CNN pass for THIS region
        det, _ = frcnn.roi_heads(feats, [whole], [(REGION, REGION)])
        d = det[0]
        if len(d["scores"]) == 0:
            continue
        k = int(d["scores"].argmax())                                                     # best class for the region
        w, h = float(x2 - x1), float(y2 - y1)
        b = d["boxes"][k].cpu() / REGION * torch.tensor([w, h, w, h]) + torch.tensor([x1, y1, x1, y1])
        boxes.append(b); scores.append(d["scores"][k].cpu()); labels.append(d["labels"][k].cpu())
    if not boxes:
        return to_voc_pred([], [], [])
    boxes, scores, labels = torch.stack(boxes), torch.stack(scores), torch.stack(labels)
    keep = batched_nms(boxes, scores, labels, 0.5)                                        # merge duplicate regions
    names = [frcnn_cats[i] for i in labels[keep].tolist()]
    return to_voc_pred(boxes[keep].tolist(), scores[keep].tolist(), names)

# ---- YOLOv8 -------------------------------------------------------------------------------------
def predict_yolo(img):
    r = yolo.predict(img, conf=SCORE_T, verbose=False, device=0 if device.type == "cuda" else "cpu")[0]
    names = [yolo_cats[int(c)] for c in r.boxes.cls.cpu().tolist()]
    return to_voc_pred(r.boxes.xyxy.cpu().tolist(), r.boxes.conf.cpu().tolist(), names)

detectors = {
    "R-CNN (per-region CNN)":     predict_rcnn,
    "Fast R-CNN (shared CNN)":    predict_fast_rcnn,
    "SSD MobileNet (SSDlite)":    lambda img: predict_torchvision(ssd, ssd_cats, img),
    "YOLOv8n":                    predict_yolo,
}

# %% [markdown]
# ## 5. Detection accuracy (mAP) and inference speed (FPS)
# FPS for R-CNN / Fast R-CNN **includes** Selective Search time, because it is part of their pipeline.

# %%
rows, example_preds = [], {}
for name, fn in detectors.items():
    metric = MeanAveragePrecision(iou_type="bbox")
    fn(samples[0][0])                                # warm-up
    t_total = 0.0
    for i, (img, target) in enumerate(samples):
        t0 = time.perf_counter()
        pred = fn(img)
        t_total += time.perf_counter() - t0
        metric.update([pred], [target])
        if i == 0:
            example_preds[name] = pred
    m = metric.compute()
    rows.append([name, float(m["map_50"]), float(m["map"]), len(samples) / t_total, 1000 * t_total / len(samples)])
    print(f"{name:26s} mAP@0.5 = {float(m['map_50']):.3f} | FPS = {len(samples) / t_total:.2f}")

# %% [markdown]
# ## 6. Computational cost (parameters and GFLOPs per image)

# %%
from torch.utils.flop_counter import FlopCounterMode

def measure_gflops(fn, img):
    with FlopCounterMode(display=False) as fc:
        fn(img)
    return fc.get_total_flops() / 1e9

params_frcnn = sum(p.numel() for p in frcnn.parameters()) / 1e6
params_ssd = sum(p.numel() for p in ssd.parameters()) / 1e6
params_yolo = sum(p.numel() for p in yolo.model.parameters()) / 1e6

try:
    from ultralytics.utils.torch_utils import get_flops
    yolo_gflops = get_flops(yolo.model, 640)
except Exception:
    yolo_gflops = float("nan")

test_img = samples[0][0]
cost = {
    "R-CNN (per-region CNN)":  (params_frcnn, measure_gflops(predict_rcnn, test_img)),
    "Fast R-CNN (shared CNN)": (params_frcnn, measure_gflops(predict_fast_rcnn, test_img)),
    "SSD MobileNet (SSDlite)": (params_ssd, measure_gflops(lambda im: predict_torchvision(ssd, ssd_cats, im), test_img)),
    "YOLOv8n":                 (params_yolo, yolo_gflops),
}

summary = pd.DataFrame(rows, columns=["Model", "mAP@0.5", "mAP@[.5:.95]", "FPS", "ms / image"])
summary["Params (M)"] = [cost[m][0] for m in summary["Model"]]
summary["GFLOPs / image"] = [cost[m][1] for m in summary["Model"]]
display(summary.round(3))

fig, ax = plt.subplots(1, 4, figsize=(20, 4))
for a, col, c in zip(ax, ["mAP@0.5", "FPS", "Params (M)", "GFLOPs / image"],
                     ["tab:blue", "tab:green", "tab:orange", "tab:red"]):
    a.bar(summary["Model"], summary[col], color=c); a.set_title(col); a.tick_params(axis="x", rotation=25)
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 7. Multiple-object detection on images (same image, all four models)

# %%
def draw(img, pred, title):
    plt.figure(figsize=(6, 5)); plt.imshow(img)
    for b, s, l in zip(pred["boxes"], pred["scores"], pred["labels"]):
        x1, y1, x2, y2 = b.tolist()
        plt.gca().add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, color="lime", lw=2))
        plt.text(x1, y1 - 3, f"{VOC_CLASSES[int(l)]} {float(s):.2f}", color="white",
                 bbox=dict(facecolor="green", alpha=0.7, pad=1), fontsize=8)
    plt.title(f"{title}  ({len(pred['boxes'])} objects)"); plt.axis("off"); plt.show()

for name, pred in example_preds.items():
    draw(samples[0][0], pred, name)

# %% [markdown]
# ## 8. Detection on a video with all four models
# Put a video next to the notebook and set `VIDEO`. Each model writes its own annotated file and its FPS is reported.
# `MAX_FRAMES` limits the frames processed (R-CNN style is slow: one CNN pass per region).

# %%
from PIL import Image

VIDEO = "input_video.mp4"        # <- change to your video path
MAX_FRAMES = 30

def annotate(frame_bgr, pred):
    for b, s, l in zip(pred["boxes"], pred["scores"], pred["labels"]):
        x1, y1, x2, y2 = map(int, b.tolist())
        cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame_bgr, f"{VOC_CLASSES[int(l)]} {float(s):.2f}", (x1, max(y1 - 5, 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    return frame_bgr

cap = cv2.VideoCapture(VIDEO)
if not cap.isOpened():
    print(f"Video '{VIDEO}' not found - put a video next to the notebook, set VIDEO and rerun this cell.")
else:
    frames = []
    while len(frames) < MAX_FRAMES:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
    fps_in = cap.get(cv2.CAP_PROP_FPS) or 25
    h, w = frames[0].shape[:2]
    cap.release()

    video_rows = []
    for name, fn in detectors.items():
        out_path = "video_" + name.split(" ")[0].lower().replace("-", "") + ".mp4"
        writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*"mp4v"), fps_in, (w, h))
        t0 = time.perf_counter()
        for f in frames:
            pred = fn(Image.fromarray(f[:, :, ::-1]))
            writer.write(annotate(f.copy(), pred))
        elapsed = time.perf_counter() - t0
        writer.release()
        video_rows.append([name, len(frames), len(frames) / elapsed, out_path])
    display(pd.DataFrame(video_rows, columns=["Model", "Frames", "Video FPS", "Output file"]).round(2))

# %% [markdown]
# ## 9. Conclusion - strengths and limitations for real-time detection
# | Model | Strengths | Limitations |
# |---|---|---|
# | **R-CNN** | First to use CNN features on region proposals; good accuracy | One CNN pass per region (about 100 passes/image here): extremely slow and heavy; multi-stage training; Selective Search is slow |
# | **Fast R-CNN** | CNN runs once per image, RoI pooling shares features: much faster than R-CNN, trained end-to-end | Still depends on external Selective Search, so not real-time |
# | **SSD MobileNet** | Single stage, very small and fast, ideal for mobile / edge devices | Lowest accuracy, weak on small objects |
# | **YOLOv8** | Single stage, best accuracy-speed balance, simple video pipeline, real-time | May miss very small or heavily overlapping objects |
#
# * **Accuracy:** region-based models classify each region carefully; YOLOv8 matches or exceeds them on common classes.
# * **Speed / cost:** compare the FPS and GFLOPs columns: R-CNN >> Fast R-CNN >> SSD / YOLO.
# * **Real-time use:** YOLOv8 (GPU or CPU) and SSD MobileNet (edge devices) are suitable; R-CNN and Fast R-CNN are not.
