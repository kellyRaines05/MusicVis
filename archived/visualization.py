""" OLD VISUALIZATION CODE using matplotlib

Visualization of music features as art with interactive sliders to adjust component weights.

Functions:
    - show(img): Displays a static image using matplotlib.
    - update(val): Updates the blended image based on slider values.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from algorithmic_art_characteristics import color_art_pixel
from music_feature_extraction import get_features
from musicVis import map_features

images = []
colors = []
tempos = []
input_music="separated/htdemucs_6s/s001/bass.wav"
features = get_features(input_music, time_chunk=4)
for f in features:
    img1, color, tempo = map_features(f)
    colors.append(color)
    images.append(img1)
    tempos.append(tempo)
    break

input_music="separated/htdemucs_6s/s001/drums.wav"
features = get_features(input_music, time_chunk=4)
for f in features:
    img2, color, tempo = map_features(f)
    colors.append(color)
    images.append(img2)
    tempos.append(tempo)
    break

input_music="separated/htdemucs_6s/s001/guitar.wav"
features = get_features(input_music, time_chunk=4)
for f in features:
    img3, color, tempo = map_features(f)
    colors.append(color)
    images.append(img3)
    tempos.append(tempo)
    break

input_music="separated/htdemucs_6s/s001/other.wav"
features = get_features(input_music, time_chunk=4)
for f in features:
    img4, color, tempo = map_features(f)
    colors.append(color)
    images.append(img4)
    tempos.append(tempo)
    break

input_music="separated/htdemucs_6s/s001/vocals.wav"
features = get_features(input_music, time_chunk=4)
for f in features:
    img5, color, tempo = map_features(f)
    colors.append(color)
    images.append(img5)
    tempos.append(tempo)
    break

full_image = np.clip(0.2 * img1 + 0.1 * img2 + 0.1 * img3 + 0.05 * img4 + 0.5 * img5, 0, 1)
colored_image = color_art_pixel(full_image, colors=colors)

def show(img):
    plt.imshow(img, cmap='gray', vmin=0, vmax=1)
    plt.axis('off')
    plt.show(block=True)

#############################################
#                                           #
#  ALTERNATIVE VISUALIZATIONS WITH SLIDERS  #
#                                           #
#############################################

# Define a function to update the blended image dynamically
def update(val):
    w1 = slider1.val
    w2 = slider2.val
    w3 = slider3.val
    w4 = slider4.val
    w5 = slider5.val

    # Recalculate the blended image based on slider values
    blended_image = np.clip(w1 * img1 + w2 * img2 + w3 * img3 + w4 * img4 + w5 * img5, 0, 1)
    colored_image = color_art_pixel(blended_image, colors=colors)

    # Update the displayed image
    ax.imshow(colored_image, cmap='gray', vmin=0, vmax=1)
    fig.canvas.draw_idle()

# Create the figure and axis for the plot
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.35)

# Display the initial image
ax.imshow(colored_image, cmap='gray', vmin=0, vmax=1)
ax.axis('off')

# Define sliders for each weight
ax_slider1 = plt.axes([0.25, 0.25, 0.65, 0.03])
ax_slider2 = plt.axes([0.25, 0.2, 0.65, 0.03])
ax_slider3 = plt.axes([0.25, 0.15, 0.65, 0.03])
ax_slider4 = plt.axes([0.25, 0.1, 0.65, 0.03])
ax_slider5 = plt.axes([0.25, 0.05, 0.65, 0.03])

slider1 = Slider(ax_slider1, 'Weight 1', 0.0, 1.0, valinit=0.2)
slider2 = Slider(ax_slider2, 'Weight 2', 0.0, 1.0, valinit=0.1)
slider3 = Slider(ax_slider3, 'Weight 3', 0.0, 1.0, valinit=0.1)
slider4 = Slider(ax_slider4, 'Weight 4', 0.0, 1.0, valinit=0.05)
slider5 = Slider(ax_slider5, 'Weight 5', 0.0, 1.0, valinit=0.5)

# Attach the update function to the sliders
slider1.on_changed(update)
slider2.on_changed(update)
slider3.on_changed(update)
slider4.on_changed(update)
slider5.on_changed(update)

plt.show()