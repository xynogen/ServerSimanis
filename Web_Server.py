from bokeh.layouts import layout
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.tile_providers import OSM
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import AjaxDataSource, HoverTool, TapTool, OpenURL
from flask import Flask, render_template
from flask_cors import CORS
import pandas as pd


app = Flask(__name__)
CORS(app, support_credentials=True)

host = '127.0.0.1'
port = '8081'
data_url = f'http://{host}:{port}/api/status'

hoverRectangle = AjaxDataSource(
    data_url = data_url,
    polling_interval = 1000,
    method = 'GET',
    mode = 'replace'
)

titik_kamera = ColumnDataSource(data=dict(
        x=[11660422.33186175],
        y=[-331930.0131737783]
    )
)

aliran_sungai = pd.read_csv('aliran_sungai.csv')
aliran_sungai['x'] = aliran_sungai['x'].apply(lambda x: list(x[1:-1].split(',')))
aliran_sungai['y'] = aliran_sungai['y'].apply(lambda x: list(x[1:-1].split(',')))
aliran_sungai = ColumnDataSource(aliran_sungai)

TOOLTIPS = [
    ('Keadaan', '@keadaan')
]

p = figure(width=1366, height=670)
p.sizing_mode = 'scale_width'
p.match_aspect = True
p.xgrid.visible = False
p.ygrid.visible = False
p.xaxis.major_tick_line_color = None
p.xaxis.minor_tick_line_color = None
p.yaxis.major_tick_line_color = None
p.yaxis.minor_tick_line_color = None
p.xaxis.major_label_text_font_size = '0pt'
p.yaxis.major_label_text_font_size = '0pt'

p.add_tile(OSM)
p.circle('x', 'y', color='green', source=titik_kamera, name='circle', size=5)
p.multi_line('x', 'y', source=aliran_sungai, line_color='green', line_width=1, name='line')
mockupHover = p.square('x', 'y', alpha = 0, source=hoverRectangle, size = 1100)

p.add_tools(HoverTool(renderers=[mockupHover], tooltips=TOOLTIPS, line_policy='interp', description = "Hover Sungai"))
p.add_tools(TapTool(renderers=[mockupHover], callback=OpenURL(url="/cctv"), description = "TapTool Sungai"))

p.legend.title = 'Level Ketinggian Air'
p.circle('x', 'y', source=titik_kamera, size=0, color='green', legend_label="Normal")
p.circle('x', 'y', source=titik_kamera, size=0, color='blue', legend_label="Waspada")
p.circle('x', 'y', source=titik_kamera, size=0, color='orange', legend_label="Siaga")
p.circle('x', 'y', source=titik_kamera, size=0, color='red', legend_label="Awas")
p.circle('x', 'y', source=titik_kamera, size=0, color='black', legend_label="Berbahaya")

script, div = components(p)

@app.route('/')
def index():
    return render_template(
        'index.html',
        plot_script = script,
        plot_div = div,
        js_resources = INLINE.render_js(),
        css_resources = INLINE.render_css(),
        host = host,
        port = port
        ).encode(encoding='UTF-8')

if __name__ == "__main__":
    app.run("0.0.0.0", port=8080, debug=True)