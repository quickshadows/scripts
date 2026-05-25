from flask import Flask, request, Response
app = Flask(__name__)

@app.route('/')
def status():
    try:
        with open('/app/status.txt') as f:
            code = int(f.read().strip())
    except:
        code = 200
    return Response(f'Status {code}', status=code)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8443, ssl_context=('cert-365days.pem', 'key.pem'))


# from flask import Flask, request, Response
# app = Flask(__name__)

# @app.route('/')
# def status():
#     code = int(request.args.get('status', 500))
#     return Response(f'Test HTTPS response {code}', status=code)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8443, ssl_context=('cert-365days.pem', 'key.pem'))
#     curl -k -X POST https://localhost:8443/set-H "Content-Type: application/json" -d '{"code":500}'

#   curl -k https://localhost:8443/
