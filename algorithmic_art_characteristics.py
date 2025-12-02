"""
Fine-grained texture generation functions to create visual patterns based on music features.

Functions:
    - blob_texture(): Generates a blobby/splatter texture pattern.
    - wavy_texture(): Generates a wavy line texture pattern.
    - scratchy_texture(): Generates a scratchy line texture pattern.
"""

import numpy as np
import cv2
import noise
from scipy.ndimage import gaussian_filter, rotate
from scipy.interpolate import interp1d
import random

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
        if not centers or np.all(np.linalg.norm(np.array(centers) - new_center, axis=1) >= 180):
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

def get_color_range(weights=None):
    ranges = [
        (0, 60),
        (60, 120),
        (120, 180),
        (180, 240),
        (240, 300),
        (300, 360)
    ]
    
    chosen_item = random.choices(ranges, weights=weights, k=1)[0]
    return chosen_item


def generate_hsv(h=512, w=512, centroid=None, texture=None, saturation=None, warp_scale=360.0):
    hsv = np.zeros((h, w, 3), dtype=np.float32)
    
    c = (centroid - centroid.min()) / (centroid.max() - centroid.min())
    c = c.flatten()
    
    x_original = np.linspace(0, 1, c.shape[0])
    x_target   = np.linspace(0, 1, w)
    
    interp = interp1d(x_original, c, kind='cubic')
    centroid_curve = interp(x_target)
    mean_c = centroid_curve.mean()
    warp = (centroid_curve - mean_c) * warp_scale
    base_hue = np.tile(np.linspace(0, 1, h)[:, None], (1, w))
    
    warped_hue = np.zeros_like(base_hue)
    
    for x in range(w):
        shift = int(warp[x])
        warped_hue[:, x] = np.roll(base_hue[:, x], shift)

    hue_min, hue_max = get_color_range()
    hsv[:, :, 0] = hue_min + warped_hue * (hue_max - hue_min)
    hsv[:,:,1] = saturation
    hsv[:,:,2] = texture
    return hsv


def color_art_pixel(texture, background, texture_hsv, target_brightness=None):
    mask = (texture >= 0.1).astype(np.float32)

    H_out = background[:,:,0] * (1-mask) + texture_hsv[:,:,0] * mask
    S_out = background[:,:,1] * (1-mask) + texture_hsv[:,:,1] * mask
    V_bg = background[:,:,2]
    V_tex = texture_hsv[:,:,2]
    V_out = V_bg*(1-mask) + V_tex*mask
    V_out = np.maximum(V_out, 0.25)

    if target_brightness is None:
        target_brightness = V_out.mean()

    current_mean = V_out.mean()
    if current_mean > 0:
        V_out *= (target_brightness / current_mean)

    V_out = np.clip(V_out, 0, 1)

    hsv = np.stack([H_out, S_out, V_out], axis=-1)
    hsv[:,:,0] = hsv[:,:,0] / 360 * 179
    hsv[:,:,1:] *= 255
    hsv = hsv.astype(np.uint8)
    rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    return rgb