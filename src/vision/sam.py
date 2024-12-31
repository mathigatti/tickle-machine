import sys

import numpy as np
from PIL import Image
from ultralytics import FastSAM, SAM

def multiply(mask, image_path):
    image = Image.open(image_path).convert("RGB")  # Ensure the image is in RGB

    image_array = np.array(image)
    mask_array = np.array(mask)

    mask_normalized = mask_array / 255.0

    # Multiply the image by the mask
    result_array = (image_array * mask_normalized[:, :, np.newaxis]).astype(np.uint8)

    # Convert the result back to an image
    return Image.fromarray(result_array)


# Define an inference source
image_path = sys.argv[1]

# Create a FastSAM model
#model = FastSAM("FastSAM-s.pt")  # or FastSAM-x.pt
#model = SAM("mobile_sam.pt")
model = SAM("sam2_b.pt")

# Run inference with texts prompt
results = model(image_path, points=[[600, 337], [339,339]], classes=0)
#results = model(image_path, texts="a person resting in the floor", points=[[600, 337], [339,339]], classes=0)

masks = results[0].masks.data

# Iterate over each object (batch dimension)
for i in range(masks.shape[0]):
    # Extract the mask for the current object
    single_mask = masks[i]

    # Normalize the tensor values to the range 0-255
    normalized_array = (single_mask.numpy() * 255).astype(np.uint8)

    # Convert the array to an image
    image = Image.fromarray(normalized_array, mode='L')  # 'L' mode is for grayscale

    # Save the image for the current mask
    output_path = f'mask_object_{i + 1}.png'
    orig_shape = results[0].masks.orig_shape
    image = image.resize(orig_shape[::-1], resample=Image.NEAREST)
    image = multiply(image, image_path)
    image.save(output_path)
    print(f"Saved image for object {i + 1} at {output_path}")
    
    break