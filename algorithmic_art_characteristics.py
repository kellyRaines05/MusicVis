import numpy as np
import matplotlib.pyplot as plt
import cv2
import noise
from scipy.ndimage import gaussian_filter, rotate

def show(img, title=None):
    plt.imshow(img, cmap='gray', vmin=0, vmax=1)
    if title: plt.title(title)
    plt.axis('off')
    plt.show()

# blob=7 for blobs or blob=2-3 for splatter
def blob_texture(h=512, w=512, n_main=5, n_scattered=30, scattered_radius=(0.5, 2), main_radius=(20, 70),
                 blobiness=7, noise_strength=7, perlin_scale=48, perlin_strength=7, min_main_distance=180, blur=(0.5, 1.5)):
    Y, X = np.mgrid[0:h, 0:w]
    sdf = np.full((h, w), np.inf, dtype=np.float32)

    perlin_noise = np.zeros((h, w), dtype=np.float32)
    shape = (h // perlin_scale, w // perlin_scale)
    scale_x, scale_y = shape
    for i in range(h):
        for j in range(w):
            perlin_noise[i][j] = noise.pnoise2(i/scale_y, j/scale_x, octaves=6, persistence=0.5, lacunarity=2.0)
    perlin_noise = (perlin_noise - perlin_noise.min()) / (perlin_noise.max() - perlin_noise.min())
    perlin_noise = (perlin_noise * 2) - 1

    def blobby_sdf(cx, cy, r):
        dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2) - r

        noise_field = gaussian_filter(np.random.randn(h, w).astype(np.float32), sigma=r * blobiness * 0.05)
        noise_field /= np.max(np.abs(noise_field)) if np.max(np.abs(noise_field)) != 0 else 1.0
        dist += noise_field * r * blobiness * 0.5

        return dist
    
    centers = []
    radii = []
    while len(centers) < n_main:
        new_center = np.array([np.random.uniform(0, w), np.random.uniform(0, h)])
        is_too_close = False
        for center in centers:
            if np.linalg.norm(new_center - center) < min_main_distance:
                is_too_close = True
                break
        if not is_too_close:
            centers.append(new_center)
            radii.append(np.random.uniform(main_radius[0], main_radius[1]))

    for (cx, cy), r in zip(centers, radii):
        sdf = np.minimum(sdf, blobby_sdf(cx, cy, r))

    for _ in range(n_scattered):
      mx = np.random.uniform(0, w)
      my = np.random.uniform(0, h)
      mr = np.random.uniform(scattered_radius[0], scattered_radius[1])
      sdf = np.minimum(sdf, blobby_sdf(mx, my, mr))

    sdf += perlin_noise * perlin_strength

    edge_noise = gaussian_filter(np.random.randn(h, w).astype(np.float32), sigma=2)
    edge_noise /= np.max(np.abs(edge_noise)) if np.max(np.abs(edge_noise)) != 0 else 1.0
    sdf += edge_noise * noise_strength * 0.7

    img = np.clip((-sdf / (np.random.uniform(blur[0], blur[1]) * 10)) + 0.5, 0, 1)
    img = gaussian_filter(img, sigma=np.random.uniform(blur[0], blur[1]))
    return img

def wavy_texture(h=512, w=512, freq=0.2, layers=5, phase_shift=0.7, amplitude_decay=0.7, rotate_angle=0):
    x = np.linspace(0, 8.3 * np.pi, w)
    y = np.linspace(0, 9.1 * np.pi, h)
    X, Y = np.meshgrid(x, y)

    pattern = np.zeros_like(X)
    amp = 1.0

    for i in range(layers):
        phase = phase_shift * i + np.random.uniform(0, 2*np.pi)
        fx = freq * (1 + 0.2 * i + 0.1*np.sin(Y * 0.3))
        fy = freq * (1 + 0.2 * i + 0.1*np.cos(X * 0.3))
        pattern += amp * np.sin(fx * X + np.sin(fy * Y + phase))
        amp *= amplitude_decay

    pattern = np.tanh(pattern)
    return rotate(pattern, angle=rotate_angle)


# grouping=1.25 means strong grouping, grouping=0 means no grouping, line_length=(100,1000) means long lines, line_length=(1,10) means dotted
def scratchy_texture(h=512, w=512, n_lines=100, grouping=0, line_length=(10,100)):
    img = np.zeros((h, w))
    group_info = []
    if grouping > 0:
        num_groups = max(1, int(n_lines * grouping * 0.1))
        group_info = [(np.array([np.random.randint(0, w), np.random.randint(0, h)]), np.random.uniform(0, 2 * np.pi)) for _ in range(num_groups)] # Store center and a preferred angle

    for _ in range(n_lines):
        if grouping > 0 and group_info:
            group_center, preferred_angle = group_info[np.random.randint(0, len(group_info))]
            x1 = int(np.clip(group_center[0] + np.random.normal(0, grouping * 20), 0, w - 1))
            y1 = int(np.clip(group_center[1] + np.random.normal(0, grouping * 20), 0, h - 1))

            angle_randomness = (1 - grouping) * np.pi / 2
            angle = preferred_angle + np.random.uniform(-angle_randomness, angle_randomness)

        else:
            x1, y1 = np.random.randint(0, w), np.random.randint(0, h)
            angle = np.random.uniform(0, 2 * np.pi)

        length = np.random.uniform(line_length[0], line_length[1])
        x2 = x1 + int(length * np.cos(angle))
        y2 = y1 + int(length * np.sin(angle))

        thickness = np.random.randint(1, 3)
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        x1 = np.clip(x1, 0, w - 1)
        y1 = np.clip(y1, 0, h - 1)
        x2 = np.clip(x2, 0, w - 1)
        y2 = np.clip(y2, 0, h - 1)


        cv2.line(img, (x1, y1), (x2, y2), color=np.random.uniform(0.5, 1.0), thickness=thickness)

    img = gaussian_filter(img, sigma=0.8)
    img = (img - img.min()) / (img.max() - img.min()) if img.max() > img.min() else img
    return img