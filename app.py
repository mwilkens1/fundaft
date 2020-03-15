import json
import plotly
from flask import render_template, request, url_for, jsonify, Flask
from scripts.return_figures import return_figures

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():

    figuresJSON = return_figures("any","any")

    return render_template('index.html',
                           figuresJSON=figuresJSON)


@app.route('/change_selection', methods=['GET', 'POST'])
def change_selection():
    
    bedrooms = request.args.get('bedrooms')
    proptype = request.args.get('proptype')

    figuresJSON = return_figures(bedrooms, proptype)

    return figuresJSON

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3001, debug=True)
