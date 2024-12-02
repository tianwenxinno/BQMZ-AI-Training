from flask import Flask, request, jsonify,render_template

app = Flask(__name__, template_folder='template', static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/greet', methods=['POST'])
def greet():
    data = request.get_json()
    name = data.get('name')
    if name:
        response = {'message': f'你好, {name}!'}
    else:
        response = {'message': '你没有提供名字哦！'}

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
