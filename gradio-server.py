from diffusers.utils import load_image
from PIL import Image
import torch

from diffusers import (
    AutoencoderKL,
    DPMSolverMultistepScheduler,
    AutoPipelineForInpainting,
)


import gradio as gr


model_id = "SG161222/Realistic_Vision_V6.0_B1_noVAE"
vae = AutoencoderKL.from_pretrained(
    "stabilityai/sd-vae-ft-mse", torch_dtype=torch.float16
).to("cuda")
pipe = AutoPipelineForInpainting.from_pretrained(
    model_id, torch_dtype=torch.float16, vae=vae
).to("cuda")
pipe.scheduler = DPMSolverMultistepScheduler.from_config(
    pipe.scheduler.config, use_karras_sigmas=True
)


def img2img(
    image: Image.Image,
    mask_image: Image.Image,
    prompt: str = "",
    negative_prompt: str = "",
    num_inference_steps: int = 20,
) -> Image.Image:
    # Generate the result image

    assert image.size == mask_image.size
    assert image.mode == mask_image.mode == "RGB"

    result_img = pipe(
        image=image,
        mask_image=mask_image,
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=num_inference_steps,
        width=image.width - image.width % 8,
        height=image.height - image.height % 8,
    ).images[0]
    return result_img.resize(image.size, Image.BICUBIC)


image = gr.Image(type="pil", label="image")
mask_image = gr.Image(type="pil", label="control image")
prompt = gr.Textbox(label="prompt")
negative_prompt = gr.Textbox(label="negative prompt")
num_inference_steps = gr.Number(
    label="num inference steps",
    value=20,
    step=10,
    minimum=10,
    maximum=50,
)

examples = [
    [
        load_image(
            "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/inpaint.png"
        ),
        load_image(
            "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/inpaint_mask.png"
        ),
        "a black cat with glowing eyes, cute, adorable, disney, pixar, highly detailed, 8k",
        "bad anatomy, deformed, ugly, disfigured",
        20,
    ]
]

demo = gr.Interface(
    img2img,
    inputs=[
        image,
        mask_image,
        prompt,
        negative_prompt,
        num_inference_steps,
    ],
    outputs=[gr.Image(type="pil", label="output image")],
    examples=examples,
)


demo.launch(debug=True)
