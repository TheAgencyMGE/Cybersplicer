from flask import Flask, request, Response, stream_with_context, render_template_string
import requests
import logging
import urllib.parse
import time
import os
from http.client import HTTPResponse
import json

# Import the HTML template from your main file
from proxy import HTML_TEMPLATE

app = Flask(__name__)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('web_proxy')

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'])
def handler(path):
    """
    Serverless handler function for Vercel
    """
    # Get the URL to forward to
    target_url = request.args.get('url')
    
    if not target_url:
        # If no URL provided, show the beautiful interface
        return render_template_string(HTML_TEMPLATE, current_year=time.strftime("%Y"))
    
    # Make sure the URL has a scheme
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url
    
    # Get the full URL including the path
    if path:
        parsed_url = urllib.parse.urlparse(target_url)
        target_url = f"{parsed_url.scheme}://{parsed_url.netloc}/{path}"
    
    # Log the request
    logger.info(f"Proxying request to: {target_url}")
    
    # Copy the request headers
    headers = {key: value for key, value in request.headers.items() if key.lower() not in ['host', 'content-length']}
    
    try:
        # Forward the request to the target server
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            params={k: v for k, v in request.args.items() if k != 'url'},
            allow_redirects=False,
            stream=True,
            verify=True
        )
        
        # Create a response object
        response_headers = {key: value for key, value in resp.headers.items() if key.lower() not in ['transfer-encoding']}
        
        # Function to rewrite links in HTML content
        def generate():
            for chunk in resp.iter_content(chunk_size=4096):
                yield chunk
        
        # Return the response
        return Response(
            stream_with_context(generate()),
            status=resp.status_code,
            headers=response_headers,
            content_type=resp.headers.get('content-type', 'text/html')
        )
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error proxying request: {e}")
        
        # Return error page with the beautiful interface
        error_html = render_template_string(
            HTML_TEMPLATE.replace(
                '<p class="tagline">Neural network infiltration system :: Bypass-level ALPHA</p>',
                f'<p class="tagline" style="color: #e74c3c;">Error: {e}</p>'
            ),
            current_year=time.strftime("%Y")
        )
        return error_html, 500

# For local development
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))