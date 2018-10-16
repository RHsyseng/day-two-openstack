import os, requests, json, logging
from flask import Flask, render_template, request, redirect, url_for, Response, make_response
## matplotlib example
from datetime import datetime
import StringIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
  SECRET_KEY='foobar69'
))

app.config.from_envvar('REC_SETTINGS', silent=True)

apiurl = os.environ['APIURL']

def get_stats():
    r = None
    stats = {}
    url = apiurl + "/stats/"
    r = requests.get(url)
    if r is not None:
        stats = r.json()
        stats['host'] = os.uname()[1]
    return stats

@app.route("/")
def hello():
    stats = get_stats()
    return render_template('index.html', stats=stats)

@app.route("/about/")
def about():
    return render_template('about.html')

@app.route("/_nuke/")
def nuke():
    r = None
    url = apiurl + "/_nuke"
    r = requests.get(url)
    if r is not None:
        return redirect('/')
    else:
        return "failed to nuke database"

@app.route("/fillups/")
def get_fillups():
    stats = get_stats()
    r = None
    url = apiurl + "/fillups/"
    r = requests.get(url)
    if r is not None:
        fillups = r.json()
        return render_template('fillups.html', fillups=fillups, stats=stats)
    else:
        return "failed to retrieve fillups"

@app.route("/fillups/<string:fillup_id>/")
def get_fillup(fillup_id):
    stats = get_stats()
    r = None
    url = apiurl + "/fillups/" + fillup_id
    r = requests.get(url)
    if r is not None:
        fillup = r.json()
        return render_template('fillup.html', fillup=fillup, stats=stats)
    else:
        return "failed to retrieve fillup"

@app.route("/mkfillup/", methods=['GET','POST'])
def mkfillup():
    if request.method == 'POST':
        fillup = {}
        fillup['date'] = request.form['date']
        fillup['distance'] = request.form['distance']
        fillup['volume'] = request.form['volume']
        fillup['cost'] = request.form['cost']
        url = apiurl + "/fillups/"
        logging.warning(request.form)
        logging.warning(fillup)
        r = requests.post(url, data=json.dumps(fillup))
        new_uid = r.json()
        re_url = '/fillups/' + new_uid
        return redirect(re_url)
    else:
        stats = get_stats()
        return render_template('mkfillup.html', stats=stats)

@app.route("/graph/<string:g_type>.png")
def mkgraph(g_type):
    if 'big' in request.args:
      graph = Figure(figsize=(12, 4))
    else:
      graph = Figure(figsize=(6, 2))
    ax = graph.add_subplot(111)
    x = []
    y = []
    url = apiurl + "/months/"
    r = requests.get(url)
    ylabels = {'total_distance':'distance (km)','total_gas':'gas (L)','lper100k':'efficiency (L/100km)','perlitre': '$/L'}
    if r is not None:
      stats = r.json()
      for date in sorted(stats):
        month = datetime.strptime(date, '%Y-%m') 
        x.append(month)
        y.append(stats[date][g_type])
    ax.plot_date(x, y, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    ax.set_ylabel(ylabels[g_type])
    graph.autofmt_xdate(bottom=0.2, rotation=15, ha='right')
    canvas = FigureCanvas(graph)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response

@app.route("/graph/<string:g_type>/")
def get_graph(g_type):
    stats = get_stats()
    return render_template('graph.html', g_type=g_type, big=True, stats=stats)
