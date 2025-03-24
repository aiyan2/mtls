import os
import io
import threading, subprocess, sys

app = Flask(__name__)

def install_if_not(module_name):
    try:
        __import__(module_name)
    except ImportError:
        print(f"{module_name} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])

# Ensure Flask is installed
install_if_not('flask')
from flask import Flask, send_file, request, jsonify, Response, redirect, url_for

# Existing routes
@app.route('/')
def hello():
    return "Hello Fortinet!"

@app.route('/index.html')
def hello2():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <body>
        <h1>Hello Fortinet!</h1>       
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

# httpbin-like routes
@app.route('/headers')
def headers():
    """Return the headers sent in the request."""
    return jsonify(dict(request.headers))

@app.route('/ip')
def ip():
    """Return the client's IP address."""
    return jsonify(morigin=request.remote_addr)

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


# pip install opencv-python
# sudo apt install -y libgl1

@app.route('/video')
def video():    
    VIDEO_PATH = "sample.mp4"  #  

    def generate_frames():
        cap = cv2.VideoCapture(VIDEO_PATH)
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break  # Stop when video ends            
            _, buffer = cv2.imencode('.jpg', frame)

            # Yield as a multipart HTTP response
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        
        cap.release()
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# HTTP and HTTPS server logic
def run_http(port):
    app.run(host='0.0.0.0', port=port)

def run_https(port):
    app.run(host='0.0.0.0', port=port, ssl_context='adhoc')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Run Flask app with HTTP and HTTPS.")
    parser.add_argument('--http-port', type=int, default=80, help="Port for HTTP server (default: 8001)")
    parser.add_argument('--https-port', type=int, default=443, help="Port for HTTPS server (default: 4443)")
    args = parser.parse_args()

    # Start HTTP and HTTPS servers in separate threads
    http_thread = threading.Thread(target=run_http, args=(args.http_port,))
    https_thread = threading.Thread(target=run_https, args=(args.https_port,))
    http_thread.start()
    https_thread.start()
    http_thread.join()
    https_thread.join()
