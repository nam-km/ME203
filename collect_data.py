#!/usr/bin/env python3
# collect_data.py
# Capture Pi Camera frames into data-MMDD-HHMM/<label>/frame_XXXX.png
#   f: forward   l: left   r: right   q: quit
# Hold a key to save frames continuously.
import argparse, os, re, time
from picamera2 import Picamera2
import cv2

KEYS = {"f": "forward", "l": "left", "r": "right"}

ap = argparse.ArgumentParser()
ap.add_argument("--out", default=time.strftime("data-%m%d-%H%M"),
                help="output root (default: data-MMDD-HHMM)")
args = ap.parse_args()

for label in KEYS.values():
    os.makedirs(os.path.join(args.out, label), exist_ok=True)

# Continue numbering after the largest existing frame_N.png
pat = re.compile(r"frame_(\d+)\.png$")
counter = 0
for root, _, files in os.walk(args.out):
    for f in files:
        m = pat.match(f)
        if m:
            counter = max(counter, int(m.group(1)) + 1)

counts = {label: len(os.listdir(os.path.join(args.out, label))) for label in KEYS.values()}

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
picam2.start()

try:
    while True:
        frame = picam2.capture_array()  # BGR order, ready for OpenCV

        view = frame.copy()
        info = "  ".join("%s(%s):%d" % (label, k, counts[label]) for k, label in KEYS.items())
        cv2.putText(view, info, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.imshow("Collect data (q: quit)", view)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        ch = chr(key) if key != 255 else ""
        if ch in KEYS:
            label = KEYS[ch]
            path = os.path.join(args.out, label, "frame_%04d.png" % counter)
            cv2.imwrite(path, frame)
            counter += 1
            counts[label] += 1
            print("[SAVE] %s" % path)
finally:
    picam2.stop()
    cv2.destroyAllWindows()
    print("[DONE] " + ", ".join("%s=%d" % (k, v) for k, v in counts.items()))
