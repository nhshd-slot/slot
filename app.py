from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/new')
def new():
    return render_template('new_procedure.html')

if __name__ == '__main__':
    app.run(debug=True)