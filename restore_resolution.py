import torch
from PIL import Image
import torchvision.transforms as T
import matplotlib.pyplot as plt
from model import UNet

def load_image(image_path):
    img = Image.open(image_path).convert('RGB')

    input_transform = T.Compose([
        T.Resize((8, 8), interpolation=T.InterpolationMode.NEAREST),
        T.ToTensor()
    ])

    target_transform = T.Compose([
        T.Resize((128, 128), interpolation=T.InterpolationMode.BICUBIC),
        T.ToTensor()
    ])

    low_res = input_transform(img)
    high_res = target_transform(img)

    return low_res.unsqueeze(0), high_res.unsqueeze(0)

# Load your trained model
model = UNet()
model.load_state_dict(torch.load('best_model.pth'))
model.eval()

image_path = "C:/Users/kelly/Programming/Music-Synthesis/music_images/s001_AJ.jpg"

low_res_img, high_res_img = load_image(image_path)
low_res_img = low_res_img
high_res_img = high_res_img

with torch.no_grad():
    predicted_img = model(low_res_img)  # Output of shape (1, 3, 100, 100)

# Convert the output to numpy arrays for visualization
predicted_img = predicted_img.squeeze().cpu().numpy().transpose(1, 2, 0)
high_res_img = high_res_img.squeeze().cpu().numpy().transpose(1, 2, 0)
low_res_img = low_res_img.squeeze().cpu().numpy().transpose(1, 2, 0)

# Plot the images
plt.figure(figsize=(18, 6))

# Low-res image (8x8)
plt.subplot(1, 3, 1)
plt.imshow(low_res_img)
plt.title("Low-Resolution Image (8x8)")
plt.axis('off')

# Original high-res image (100x100)
plt.subplot(1, 3, 2)
plt.imshow(high_res_img)
plt.title("Original High-Resolution Image (128x128)")
plt.axis('off')

# Predicted high-res image (100x100)
plt.subplot(1, 3, 3)
plt.imshow(predicted_img)
plt.title("Predicted High-Resolution Image (128x128)")
plt.axis('off')

plt.show()