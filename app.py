import random
from pathlib import Path
from types import SimpleNamespace

import cv2
import dash
import numpy as np
import plotly.express as px

from dash import Input, Output, State, dcc, html
from diffusers.utils import load_image
from gradio_client import Client, handle_file
from PIL import Image
from custom_func import export_image, figure_to_pil


client = Client("http://127.0.0.1:7860")


# i can use dcc.Store  element. but st.session_state is more convenient cause i'm somewhat familiar with streamlit
# it still better than use `global` keyword
st = SimpleNamespace()
st.session_state = {}


def draw_next_image() -> Image.Image:
    """update image. currently, randomly load one of image from predefined urls"""
    urls = [
        "https://images.pexels.com/photos/1590051/pexels-photo-1590051.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/868677/pexels-photo-868677.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
        "https://images.pexels.com/photos/371578/pexels-photo-371578.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
    ]
    url = random.choice(urls)
    image = load_image(url)
    image.thumbnail((1024, 1024))
    return image


# populate initial image. from now on, callback handle it when button clicked.
st.session_state["image"] = draw_next_image()

fig_image = px.imshow(st.session_state["image"]).update_layout(
    dragmode="lasso",
    width=st.session_state["image"].width,
    height=st.session_state["image"].height,
)

# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        # it load next image. (currently it draw randomly. you can modify it handle batch image sequentially)
        html.Button(id="button-update_image", n_clicks=0, children="Update Image"),
        # for prompt
        html.H1("prompt"),
        dcc.Textarea(
            id="textarea-prompt",
            value="a pothole in a road",
            style={"width": "100%", "height": 100},
        ),
        # for negative prompt
        html.H1("negative prompt"),
        dcc.Textarea(
            id="textarea-negative_prompt",
            value="",
            style={"width": "100%", "height": 100},
        ),
        # for num_inference_steps
        dcc.Slider(10, 50, 10, value=20, id="slider-num_inference_steps"),
        # store image
        dcc.Graph(
            id="graph-image",
            figure=fig_image,
            style={"width": "90vh", "height": "90vh"},
        ),
        dcc.Store(id="selected-data"),
        # save
        html.Button(id="button-save_image", n_clicks=0, children="Save Image"),
    ]
)


@app.callback(
    Output("graph-image", "figure", allow_duplicate=True),
    Input("button-update_image", "n_clicks"),
    prevent_initial_call=True,
)
def update_image(n_clicks):
    if n_clicks > 0:
        # update session_state cause other callback need to access this
        st.session_state["image"] = draw_next_image()
        fig_image = px.imshow(st.session_state["image"]).update_layout(
            dragmode="lasso",
            width=st.session_state["image"].width,
            height=st.session_state["image"].height,
        )
        return fig_image
    return dash.no_update


@app.callback(
    Input("button-save_image", "n_clicks"),
    State("graph-image", "figure"),
    prevent_initial_call=True,
)
def save_image(n_clicks, figure):
    if n_clicks > 0:
        image = figure_to_pil(figure)
        out_dir = Path("./artifact")

        out_dir.mkdir(parents=True, exist_ok=True)
        export_image(image, bucket=out_dir)

    return dash.no_update


@app.callback(
    Output("graph-image", "figure"),
    Input("graph-image", "selectedData"),
    State("graph-image", "figure"),
    State("textarea-prompt", "value"),
    State("textarea-negative_prompt", "value"),
    State("slider-num_inference_steps", "value"),
    prevent_initial_call=True,
)
def update_graph(
    selectedData, figure_data, prompt, negative_prompt, num_inference_steps
):
    # global rgb

    # Check if there is new selected data
    if selectedData and "lassoPoints" in selectedData:
        xs = selectedData["lassoPoints"]["x"]
        ys = selectedData["lassoPoints"]["y"]

        pts = np.array([[x, y] for x, y in zip(xs, ys)]).astype(int)

        # print(pts)
        # pts = pts.reshape((-1, 1, 2))
        image_edit = figure_to_pil(figure_data)
        copy_mask = np.zeros(image_edit.size[::-1], dtype=np.uint8)
        cv2.fillPoly(copy_mask, [pts], (255,))

        mask_image = Image.fromarray(copy_mask > 0)
        mask_image = mask_image.convert("RGB")

        result_file = client.predict(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps,
            image=handle_file(export_image(image_edit)),
            mask_image=handle_file(export_image(mask_image)),
        )

        image_edit = Image.open(result_file)
        st.session_state["image"] = image_edit
        return px.imshow(st.session_state["image"]).update_layout(dragmode="lasso")
    else:
        """here i thouhg dash.exceptions.PreventUpdate would work. but it would reset image. i dont know how this works actually"""
        # dash.exceptions.PreventUpdate
        return px.imshow(st.session_state["image"]).update_layout(dragmode="lasso")


if __name__ == "__main__":
    app.run_server(debug=True, port=7862)
