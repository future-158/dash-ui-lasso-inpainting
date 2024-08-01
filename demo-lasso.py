import numpy as np
import cv2
import base64
from io import BytesIO

import dash
import plotly.express as px

# from dash.dependencies import Input, Output, State
from dash import Input, Output, dcc, html
from PIL import Image
from types import SimpleNamespace


def figure_to_pil(figure_data) -> Image.Image:
    # Decode plotly figure to an pillow image
    url = figure_data["data"][0]["source"]
    encoded_image = url.split(";base64,")[-1]
    return Image.open(BytesIO(base64.b64decode(encoded_image)))


st = SimpleNamespace()
st.session_state = {}

st.session_state["source"] = Image.new("RGB", (500, 500), (0, 255, 0))
st.session_state["edit"] = Image.new("RGB", (500, 500), (0, 0, 255))


# def update():
#     st.session_state["source"] = Image.new("RGB", (500, 500), (0, 255, 0))
#     st.session_state["edit"] = Image.new("RGB", (500, 500), (0, 0, 255))


fig_source = px.imshow(st.session_state["source"]).update_layout(dragmode="lasso")
fig_edit = px.imshow(st.session_state["edit"]).update_layout(dragmode="lasso")

# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.Graph(id="graph-source", figure=fig_source),
        dcc.Graph(id="graph-edit", figure=fig_edit),
        dcc.Store(id="selected-data"),
    ]
)


@app.callback(
    Output("graph-edit", "figure"),
    Input("graph-source", "selectedData"),
    Input("graph-source", "figure"),
    Input("graph-edit", "figure"),
)
def update_graph(selectedData, figure_data_source, figure_data_edit):

    # Check if there is new selected data
    if selectedData and "lassoPoints" in selectedData:
        xs = selectedData["lassoPoints"]["x"]
        ys = selectedData["lassoPoints"]["y"]

        # print(list(zip(xs,ys)))
        pts = np.array([[x, y] for x, y in zip(xs, ys)]).astype(int)
        print(pts)

        pts = pts.reshape(-1, 1, 2)

        image_src = figure_to_pil(figure_data_source)
        image_edit = figure_to_pil(figure_data_edit)
        copy_mask = np.zeros(image_edit.size[::-1], dtype=np.uint8)
        cv2.fillPoly(copy_mask, [pts], (255,))

        copy_mask = copy_mask > 0

        copy_mask = Image.fromarray(copy_mask)
        image_edit.paste(image_src, mask=copy_mask)
        # st.session_state["edit"] = image_edit
        # return px.imshow(st.session_state["edit"]).update_layout(dragmode="lasso")
        return px.imshow(image_edit).update_layout(dragmode="lasso")
    else:
        raise dash.exceptions.PreventUpdate
        # return px.imshow(st.session_state["edit"]).update_layout(dragmode="lasso")


if __name__ == "__main__":
    app.run_server(debug=True)
