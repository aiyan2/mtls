import threading
from flask import Flask, send_file, request, jsonify, Response
import os
import io
import ssl

app = Flask(__name__)

# Certificate paths (adjust these paths to your certificates)
server_cert = './certs/mutual-tls/server/server.crt'  # Server certificate
server_key = './certs/mutual-tls/server/server.key'    # Server private key
ca_cert = './certs/mutual-tls/ca/ca.crt'              # CA certificate to verify client certs
client_cert = './certs/mutual-tls/client/client.crt'   # Client certificate
client_key = './certs/mutual-tls/client/client.key'    # Client private key



# curl -v --cert client.crt --key client.key https://127.0.0.1:4443/ --insecure

# Routes
@app.route('/')
def hello():
    return "Hello Mars!"

@app.route('/index.html')
def hello2():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <body>
        <h1>Hello Mars!</h1>       
    </body>
    </html>
    """
    return html_content

@app.route('/eicar')
@app.route('/eicar.com')
def eicar():
    eicar_content = "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    return eicar_content, 200, {'Content-Type': 'text/plain'}

@app.route('/file')
def file():
    size_kb = int(request.args.get('size', 1024))
    data = os.urandom(size_kb * 1024)
    return send_file(io.BytesIO(data), as_attachment=True, download_name="dummyfile.bin")

@app.route('/proxy.pac')
def pac_file():
    proxy = request.args.get('proxy', 'fortiproxycloud-test.com')
    port = request.args.get('port', '10445')
    pac_content = f"""
    function FindProxyForURL(url, host) {{
        return "HTTPS {proxy}:{port};";
    }}
    """
    return Response(pac_content, content_type='application/x-ns-proxy-autoconfig')

@app.route('/file', methods=['POST'])
def upload_file():
    file = request.files['file']
    file.save("/tmp/uploaded_file")
    return jsonify(message="File uploaded successfully")

# mTLS-specific routes (e.g., secure API)
@app.route('/headers')
def headers():
    """Return the headers sent in the request."""
    return jsonify(dict(request.headers))

@app.route('/ip')
def ip():
    """Return the client's IP address."""
    return jsonify(origin=request.remote_addr)

@app.route('/status/<int:code>')
def status_code(code):
    """Return a specific status code."""
    return ('', code)

@app.route('/redirect/<int:count>')
def redirect_n_times(count):
    """Redirect the client a specified number of times."""
    if count > 0:
        return redirect(url_for('redirect_n_times', count=count - 1))
    return "Final destination!", 200

@app.route('/get')
def get_request():
    """Return the request data for GET."""
    return jsonify(args=request.args, headers=dict(request.headers), origin=request.remote_addr)

@app.route('/post', methods=['POST'])
def post_request():
    """Return the request data for POST."""
    return jsonify(data=request.data.decode('utf-8'), json=request.json, headers=dict(request.headers), origin=request.remote_addr)

@app.route('/delay/<int:seconds>')
def delay(seconds):
    """Simulate a delay before responding."""
    import time
    time.sleep(seconds)
    return jsonify(message=f"Response delayed by {seconds} seconds")

# HTTPS mTLS server logic
def run_https(port):
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)  # Enforce TLS 1.2
    context.load_cert_chain(certfile=server_cert, keyfile=server_key)
    context.load_verify_locations(cafile=ca_cert)
    context.verify_mode = ssl.CERT_REQUIRED  # Require a valid client certificate

    app.run(host='0.0.0.0', port=port, ssl_context=context)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Run Flask app with HTTPS (mTLS).")
    parser.add_argument('--https-port', type=int, default=4443, help="Port for HTTPS server (default: 4443)")
    args = parser.parse_args()

    # Start HTTPS server in a separate thread
    https_thread = threading.Thread(target=run_https, args=(args.https_port,))
    https_thread.start()
    https_thread.join()
