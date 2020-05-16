from flask import Flask, request
from flask import render_template

app = Flask(__name__)
data = {}


@app.route("/")
def get_chart_page():
    return render_template('chart.html')


@app.route('/update', methods=['POST'])
def update():
    global data
    data = request.json
    print("Data:", data)
    return "success", 201


@app.route('/ajax')
def ajax():
    return data


if __name__ == "__main__":
    app.run(host='localhost', port=3000)
