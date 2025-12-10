"""
Fine-grained texture generation functions to create visual patterns based on music features.

Functions:
    - blob_texture(): Generates a blobby/splatter texture pattern.
    - wavy_texture(): Generates a wavy line texture pattern.
    - scratchy_texture(): Generates a scratchy line texture pattern.
    - get_color(): Determines color based on music features.
    - color_art_pixel(): Colors a grayscale texture based on provided colors.
"""

import numpy as np
import cv2
import noise
import random
from colorsys import hsv_to_rgb
from scipy.ndimage import gaussian_filter, rotate
from models import MusicFeatures

# blob=7 for blobs or blob=2 for splatter
def blob_texture(h=512, w=512, n_main=5, blobiness=2):
    Y, X = np.mgrid[0:h, 0:w]
    sdf = np.full((h, w), np.inf, dtype=np.float32)
    
    shape = (h // 48, w // 48)
    scale_x, scale_y = shape
    perlin_noise = np.array([[noise.pnoise2(i/scale_y, j/scale_x, octaves=6, persistence=0.5, lacunarity=2.0) 
                              for j in range(w)] for i in range(h)], dtype=np.float32)
    perlin_noise = (perlin_noise - perlin_noise.min()) / (perlin_noise.max() - perlin_noise.min())
    perlin_noise = (perlin_noise * 2) - 1

    def blobby_sdf(cx, cy, r, noise_field):
        dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2) - r
        noise_field_normalized = noise_field / (np.max(np.abs(noise_field)) if np.max(np.abs(noise_field)) != 0 else 1.0)
        dist += noise_field_normalized * r * blobiness * 0.5
        return dist
    
    centers = []
    radii = []
    while len(centers) < n_main:
        new_center = np.random.uniform([0, 0], [w, h])
        min_distance = min(h, w) / max(5, n_main) 
        if not centers or np.all(np.linalg.norm(np.array(centers) - new_center, axis=1) >= min_distance):
            centers.append(new_center)
            radii.append(np.random.uniform(20, 70))

    base_noise_field = gaussian_filter(np.random.randn(h, w).astype(np.float32), sigma=2)
    base_noise_field /= np.max(np.abs(base_noise_field)) if np.max(np.abs(base_noise_field)) != 0 else 1.0

    for (cx, cy), r in zip(centers, radii):
        blob_noise = gaussian_filter(np.random.randn(h, w).astype(np.float32), sigma=r * blobiness * 0.05)
        blob_noise /= np.max(np.abs(blob_noise)) if np.max(np.abs(blob_noise)) != 0 else 1.0
        sdf = np.minimum(sdf, blobby_sdf(cx, cy, r, blob_noise))

    for _ in range(n_main * 5):
        mx, my = np.random.uniform(0, w), np.random.uniform(0, h)
        mr = np.random.uniform(0.5, 2)
        blob_noise = gaussian_filter(np.random.randn(h, w).astype(np.float32), sigma=mr * blobiness * 0.05)
        blob_noise /= np.max(np.abs(blob_noise)) if np.max(np.abs(blob_noise)) != 0 else 1.0
        sdf = np.minimum(sdf, blobby_sdf(mx, my, mr, blob_noise))

    sdf += base_noise_field * 1.5

    blur_sigma = np.random.uniform(0.5, 1.5)
    img = np.clip((-sdf / (blur_sigma * 10)) + 0.5, 0, 1)
    img = gaussian_filter(img, sigma=blur_sigma)
    return img


# freq=0.25 for wide waves, freq=1.0 for tight waves, layers=5 for complexity
def wavy_texture(h=512, w=512, freq=0.25, layers=1):
    x = np.linspace(0, 8 * np.pi, w)
    y = np.linspace(0, 9 * np.pi, h)
    X, Y = np.meshgrid(x, y)

    pattern = np.zeros_like(X)

    for i in range(layers):
        phase = i + np.random.uniform(0, 2*np.pi)
        fx = freq * (1 + 0.2 * i + 0.1*np.sin(Y * 0.3))
        fy = freq * (1 + 0.2 * i + 0.1*np.cos(X * 0.3))
        pattern += np.sin(fx * X + np.sin(fy * Y + phase))

    pattern = np.tanh(pattern)
    return rotate(pattern, angle=90)


# separation=1.25 means strong separation, separation=0 means no separation, line_length=(100,1000) means long lines, line_length=(1,10) means dotted
def scratchy_texture(h=512, w=512, n_lines=100, separation=0, line_length=(10,100)):
    img = np.zeros((h, w))
    num_groups = max(1, int(n_lines * 0.1))
    group_info = [(np.array([np.random.randint(0, w), np.random.randint(0, h)]), np.random.uniform(0, 2*np.pi)) for _ in range(num_groups)]

    for _ in range(n_lines):
      group_center, preferred_angle = group_info[np.random.randint(0, len(group_info))]
      x1 = np.random.randint(0, w)
      y1 = np.random.randint(0, h)
      dx = x1 - group_center[0]
      dy = y1 - group_center[1]

      if separation < 1:
          strength = (1 - separation) * 30
          x1 = int(group_center[0] + np.random.normal(0, strength))
          y1 = int(group_center[1] + np.random.normal(0, strength))

          angle_randomness = (1 - separation) * np.pi/2
          angle = preferred_angle + np.random.uniform(-angle_randomness, angle_randomness)
      else:
          strength = (separation - 1) * 40
          x1 = int(np.clip(x1 + dx * (separation - 1) + np.random.randn() * strength,
                            0, w - 1))
          y1 = int(np.clip(y1 + dy * (separation - 1) + np.random.randn() * strength,
                            0, h - 1))
          angle_randomness = min((separation - 1) * np.pi, np.pi)
          angle = preferred_angle + np.random.uniform(-angle_randomness, angle_randomness)
      length = np.random.uniform(line_length[0], line_length[1])
      x2 = x1 + int(length * np.cos(angle))
      y2 = y1 + int(length * np.sin(angle))

      thickness = np.random.randint(1, 3)
      x1 = np.clip(x1, 0, w - 1)
      y1 = np.clip(y1, 0, h - 1)
      x2 = np.clip(x2, 0, w - 1)
      y2 = np.clip(y2, 0, h - 1)

      cv2.line(img, (x1, y1), (x2, y2), color=np.random.uniform(0.5, 1.0), thickness=thickness)

    img = gaussian_filter(img, sigma=0.8)
    img = (img - img.min()) / (img.max() - img.min()) if img.max() > img.min() else img
    return img

def get_color(features: MusicFeatures, centroid_threshold=3000, flatness_threshold=0.25):
    notes=features.notes
    loudness=features.loudness
    centroid=features.centroid
    flatness=features.flatness
    source=features.instrument_sources
    bright=features.quality[0][0]
    dark=features.quality[0][1]

    # higher value for higher pitch
    mean_pitch = np.mean(notes)
    value = np.clip(mean_pitch / 90, 0, 1)
    
    # higher saturation for louder sounds
    min_loudness = -35
    max_loudness = -5
    mean_loudness = np.mean(loudness)
    saturation = (mean_loudness - min_loudness) / (max_loudness - min_loudness)
    if bright:
        saturation += 0.8
    elif dark:
        saturation -= 0.5
    saturation = np.clip(saturation, 0, 1)

    # warm colors for low centroid, cool colors for high centroid
    if np.mean(centroid) > centroid_threshold:
        # smooth sounds - green to blue
        if np.max(flatness) < flatness_threshold:
            if source == 0:
                hue = random.uniform(201, 240)
            elif source == 1 or source == 2:
                hue = random.uniform(110, 169)
        # harsh sounds - cyan, purple, magenta
        else:
            # acoustic - magenta
            if source == 0:
                hue = random.uniform(321, 330)
            # electronic - purple
            elif source == 1:
                hue = random.uniform(241, 320)
            # synthetic - cyan
            else:
                hue = random.choice([random.uniform(170, 200)])
    else:
        # smooth sounds - pink, orange-brown/yellow
        if np.max(flatness) < flatness_threshold:
            # acoustic - orange-brown
            if source == 0:
                hue = random.uniform(21, 40)
            # electronic - pink
            elif source == 1:
                hue = random.uniform(331, 354)
            # synthetic - yellow
            else:
                hue = random.uniform(41, 50)
        # harsh sounds - yellow to yellow-green, red to red-orange
        else:
            # acoustic - red-orange
            if source == 0:
                hue = random.uniform(0, 20)
            # electronic - yellow/yellow-green
            elif source == 1:
                hue = random.uniform(51, 109)
            # synthetic - red
            else:
                hue = random.uniform(355, 360)
    color = hsv_to_rgb(h=(hue/360.0), s=saturation, v=value)
    return np.array([int(c * 255) for c in color])


def color_art_pixel(texture, colors):
    num_colors = len(colors)

    if num_colors == 1:
        color = np.array(colors[0], dtype=np.uint8)
        # add black or white to blend colors
        if np.linalg.norm(color) < 128:
            colors = [colors[0], [255, 255, 255]]
        else:
            colors = [colors[0], [0,0,0]]
        num_colors = 2

    colors = np.array(colors, dtype=np.uint8)
    segment_length = 256 // (num_colors - 1)
    remainder = 256 % (num_colors - 1)

    points = [i * segment_length for i in range(num_colors - 1)]
    points.append(256)

    LUT = np.zeros((256, 3), dtype=np.uint8)

    for i in range(len(points) - 1):
        start = points[i]
        end = points[i + 1]
        if i == len(points) - 2:
            end += remainder
        LUT[start:end] = np.linspace(colors[i], colors[i + 1], num=end - start, dtype=np.uint8)

    texture = (texture * 255.0).astype(np.uint8)
    colored_array = LUT[texture]
    return colored_array
