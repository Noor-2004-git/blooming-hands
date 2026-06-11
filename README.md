# 🌸 Blooming Hands

An augmented reality project that grows animated flowers on your fingertips in real time — controlled entirely by your hand gestures.

Built with Python, OpenCV, and MediaPipe.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue) ![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-green) ![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.35-purple)

---

## ✨ Demo
<img width="827" height="358" alt="image" src="https://github.com/user-attachments/assets/48eeb01b-ce0b-4309-9e16-a0886775dff6" />

> Open your hand → flowers bloom on every fingertip  
> Make a fist → flowers wilt  
> Pinch → petals scatter in a burst

---

## 🧠 How It Works

```
Webcam → MediaPipe (21 hand landmarks) → Gesture Detector → Flower Engine → OpenCV Window
```

1. **MediaPipe** detects 21 keypoints on each hand every frame
2. **Gesture Detector** measures finger distances to classify your hand pose
3. **Flower Engine** animates bloom state (0→100%) and draws petals on each fingertip
4. The whole loop runs ~30 times per second

---

## 🗂️ Project Structure

```
blooming-hands/
├── main.py               # Entry point — webcam loop + OpenCV window
├── gesture_detector.py   # Hand pose classification (OPEN / CLOSED / PINCH / NEUTRAL)
├── flower_engine.py      # Flower drawing, bloom animation, particle burst
├── requirements.txt      # Dependencies
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/blooming-hands.git
cd blooming-hands
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> On first run, the hand landmark model (~8 MB) is downloaded automatically.

### 3. Run

```bash
python main.py
```

---

## 🤚 Gesture Controls

| Gesture | Effect |
|---|---|
| ✋ Open hand | Flowers **bloom** on all fingertips |
| ✊ Fist | Flowers **wilt** back to buds |
| 🤌 Pinch (thumb + index) | **Scatter** petal particles |
| 🤚 Neutral | Bloom level **holds** |

### Keyboard shortcuts

| Key | Action |
|---|---|
| `Q` / `Esc` | Quit |
| `S` | Save screenshot |
| `H` | Toggle gesture HUD |

---

## 📦 Requirements

- Python 3.9–3.13
- Webcam
- Windows / macOS / Linux

```
opencv-python>=4.8.0
mediapipe>=0.10.30
numpy>=1.24.0
Note: !pip install mediapipe (if any error pops in)
```

---

## 🛠️ Built With

- [OpenCV](https://opencv.org/) — webcam capture and drawing
- [MediaPipe](https://mediapipe.dev/) — real-time hand landmark detection
- [NumPy](https://numpy.org/) — pixel math for petal shapes

---

## 📄 License

MIT — do whatever you want with it.
