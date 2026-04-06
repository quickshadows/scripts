from flask import Flask, request, Response, jsonify

app = Flask(__name__)

STATUS_FILE = '/app/status.txt'


@app.route('/')
def status():
    try:
        with open(STATUS_FILE) as f:
            code = int(f.read().strip())
    except:
        code = 200
    return Response(f'Status {code}', status=code)


@app.route('/set', methods=['POST'])
def set_status():
    data = request.get_json(silent=True)

    if not data or 'code' not in data:
        return jsonify({"error": "code is required"}), 400

    try:
        code = int(data['code'])
    except ValueError:
        return jsonify({"error": "code must be integer"}), 400

    # запись статуса
    try:
        with open(STATUS_FILE, 'w') as f:
            f.write(str(code))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "status updated",
        "code": code
    })


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8443,
        ssl_context=('cert-365days.pem', 'key.pem')
    )


#   curl -k -X POST https://localhost:8443/set -H "Content-Type: application/json"    -d '{"code":500}'

#   curl -k https://localhost:8443/