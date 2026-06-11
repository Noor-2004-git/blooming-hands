"""
flower_engine.py
Draws animated blooming flowers anchored to fingertip positions.

Each Flower object has a bloom state (0.0 → 1.0) that drives:
  • petal size / spread angle
  • centre glow radius
  • opacity
  • falling-petal particle burst (PINCH gesture)
"""

import cv2
import numpy as np
import math
import random


# ── colour palette (BGR) ─────────────────────────────────────────────────────
PETAL_COLORS = [
    (80,  120, 255),   # rose-pink
    (100, 200, 255),   # warm yellow
    (200, 100, 255),   # lavender
    (80,  220, 160),   # mint
    (50,  160, 255),   # amber-orange
]
CENTRE_COLOR   = (60,  220, 240)   # golden yellow
STEM_COLOR     = (60,  160,  60)   # green
PARTICLE_COLOR = (120, 180, 255)


# ── easing ────────────────────────────────────────────────────────────────────
def _ease_out_cubic(t):
    return 1 - (1 - t) ** 3


def _ease_in_cubic(t):
    return t ** 3


# ── Particle ──────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, cx, cy):
        angle  = random.uniform(0, 2 * math.pi)
        speed  = random.uniform(2, 6)
        self.x = float(cx)
        self.y = float(cy)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - random.uniform(1, 3)
        self.life  = 1.0
        self.decay = random.uniform(0.03, 0.07)
        self.size  = random.randint(2, 5)
        self.color = random.choice(PETAL_COLORS)

    def update(self):
        self.x   += self.vx
        self.y   += self.vy
        self.vy  += 0.2          # gravity
        self.life -= self.decay
        return self.life > 0

    def draw(self, frame):
        alpha  = max(0.0, self.life)
        color  = tuple(int(c * alpha) for c in self.color)
        pos    = (int(self.x), int(self.y))
        cv2.circle(frame, pos, self.size, color, -1, cv2.LINE_AA)


# ── Flower ────────────────────────────────────────────────────────────────────
class Flower:
    NUM_PETALS    = 6
    MAX_PETAL_LEN = 32      # px when fully bloomed
    MAX_PETAL_W   = 10
    BLOOM_SPEED   = 0.06    # per frame when opening
    WILT_SPEED    = 0.04    # per frame when closing

    def __init__(self, color_idx: int = 0):
        self.bloom     = 0.0          # 0 = bud, 1 = fully open
        self.color     = PETAL_COLORS[color_idx % len(PETAL_COLORS)]
        self.particles : list[Particle] = []
        self._wobble   = random.uniform(0, 2 * math.pi)   # phase offset

    # ── state transitions ────────────────────────────────────────────────────
    def open(self):
        self.bloom = min(1.0, self.bloom + self.BLOOM_SPEED)

    def close(self):
        self.bloom = max(0.0, self.bloom - self.WILT_SPEED)

    def burst(self, cx, cy):
        """Scatter petals outward (PINCH gesture)."""
        for _ in range(18):
            self.particles.append(Particle(cx, cy))

    # ── draw ─────────────────────────────────────────────────────────────────
    def draw(self, frame, cx: int, cy: int, t: int):
        """Draw flower centred at (cx, cy). t = frame counter for animation."""
        b = _ease_out_cubic(self.bloom)

        # Update + draw particles
        self.particles = [p for p in self.particles if p.update()]
        for p in self.particles:
            p.draw(frame)

        if b < 0.02:
            # Draw tiny bud dot
            cv2.circle(frame, (cx, cy), 3, self.color, -1, cv2.LINE_AA)
            return

        # Wobble sway
        wobble = math.sin(t * 0.05 + self._wobble) * 3 * b

        # Draw stem
        stem_len = int(20 * b)
        cv2.line(frame,
                 (cx, cy + stem_len),
                 (cx + int(wobble), cy),
                 STEM_COLOR, 1, cv2.LINE_AA)

        # Draw petals
        petal_len = int(self.MAX_PETAL_LEN * b)
        petal_w   = int(self.MAX_PETAL_W   * b)

        overlay = frame.copy()
        for i in range(self.NUM_PETALS):
            base_angle = (2 * math.pi / self.NUM_PETALS) * i
            # gentle animation: petals sway slightly
            angle = base_angle + math.sin(t * 0.04 + i) * 0.08 * b + math.radians(wobble)

            # petal tip
            tx = cx + int(math.cos(angle) * petal_len)
            ty = cy + int(math.sin(angle) * petal_len)

            # control points for ellipse-like petal using fillPoly
            perp = angle + math.pi / 2
            pts  = []
            for frac in np.linspace(0, 1, 8):
                ease    = math.sin(frac * math.pi)        # 0→1→0 envelope
                spread  = ease * petal_w
                mid_x   = cx + int(math.cos(angle) * petal_len * frac)
                mid_y   = cy + int(math.sin(angle) * petal_len * frac)
                side_x  = int(math.cos(perp) * spread)
                side_y  = int(math.sin(perp) * spread)
                pts.append([mid_x + side_x, mid_y + side_y])
            for frac in np.linspace(1, 0, 8):
                ease    = math.sin(frac * math.pi)
                spread  = ease * petal_w
                mid_x   = cx + int(math.cos(angle) * petal_len * frac)
                mid_y   = cy + int(math.sin(angle) * petal_len * frac)
                side_x  = int(math.cos(perp) * spread)
                side_y  = int(math.sin(perp) * spread)
                pts.append([mid_x - side_x, mid_y - side_y])

            petal_pts = np.array(pts, dtype=np.int32)
            cv2.fillPoly(overlay, [petal_pts], self.color, cv2.LINE_AA)

        # Blend petals with transparency
        alpha = min(0.85, 0.4 + 0.45 * b)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Centre glow
        glow_r = max(1, int(7 * b))
        cv2.circle(frame, (cx, cy), glow_r + 2, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(frame, (cx, cy), glow_r,     CENTRE_COLOR,    -1, cv2.LINE_AA)

        # Bloom % label (small, above flower)
        if b > 0.2:
            label     = f"{int(b * 100)}%"
            font      = cv2.FONT_HERSHEY_SIMPLEX
            scale     = 0.35
            thickness = 1
            (tw, th), _ = cv2.getTextSize(label, font, scale, thickness)
            cv2.putText(frame, label,
                        (cx - tw // 2, cy - petal_len - 6),
                        font, scale, (220, 220, 220), thickness, cv2.LINE_AA)


# ── FlowerManager ─────────────────────────────────────────────────────────────
class FlowerManager:
    """
    Manages one Flower per fingertip (up to 10 across both hands).
    Call update() each frame with gesture + positions.
    """

    def __init__(self):
        # key: (hand_idx, tip_idx) → Flower
        self._flowers: dict[tuple, Flower] = {}
        self._frame_t = 0

    def _get_flower(self, hand_idx: int, tip_idx: int) -> "Flower":
        key = (hand_idx, tip_idx)
        if key not in self._flowers:
            color_idx = (hand_idx * 5 + tip_idx) % len(PETAL_COLORS)
            self._flowers[key] = Flower(color_idx)
        return self._flowers[key]

    def update(self, frame,
               all_tips:     list,   # list of lists: [[5 tips per hand], ...]
               all_gestures: list):  # gesture string per hand
        """
        frame        : BGR numpy array (modified in place)
        all_tips     : [[(x,y)×5], [(x,y)×5], ...]   one list per detected hand
        all_gestures : ['OPEN'|'CLOSED'|'PINCH'|'NEUTRAL', ...]
        """
        self._frame_t += 1

        active_keys = set()
        for hand_idx, (tips, gesture) in enumerate(zip(all_tips, all_gestures)):
            for tip_idx, (cx, cy) in enumerate(tips):
                key    = (hand_idx, tip_idx)
                flower = self._get_flower(hand_idx, tip_idx)
                active_keys.add(key)

                if gesture == "OPEN":
                    flower.open()
                elif gesture == "CLOSED":
                    flower.close()
                elif gesture == "PINCH" and tip_idx == 0:   # only thumb tip bursts
                    flower.burst(cx, cy)
                    flower.close()
                # NEUTRAL → hold current bloom level

                flower.draw(frame, cx, cy, self._frame_t)

        # Wilt flowers whose hands disappeared
        for key, flower in self._flowers.items():
            if key not in active_keys:
                flower.close()

        # Prune fully closed & particle-less flowers
        self._flowers = {
            k: f for k, f in self._flowers.items()
            if f.bloom > 0.01 or f.particles
        }