from bokeh.plotting import figure
from bokeh.embed import file_html
import json
fig = figure()
fig.line([1,2,3,4,5], [3,4,5,2,3])
item_text = json.dumps(json_item(fig, "myplot"))

item = JSON.parse(item_text);
Bokeh.embed.embed_item(item);

from bokeh.embed import server_document
script = server_document("http://localhost:5006/sliders")