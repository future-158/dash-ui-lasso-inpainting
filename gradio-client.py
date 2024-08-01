from diffusers.utils import load_image
from gradio_client import Client, handle_file
from PIL import Image
from custom_func import export_image

client = Client("http://127.0.0.1:7860")


image = load_image(
    "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/inpaint.png"
)
mask_image = load_image(
    "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/inpaint_mask.png"
)
prompt = (
    "a black cat with glowing eyes, cute, adorable, disney, pixar, highly detailed, 8k"
)
negative_prompt = "bad anatomy, deformed, ugly, disfigured"
num_inference_steps = 20

result_file = client.predict(
    prompt=prompt,
    negative_prompt=negative_prompt,
    num_inference_steps=num_inference_steps,
    image=handle_file(export_image(image)),
    mask_image=handle_file(export_image(mask_image)),
)
Image.open(result_file)
