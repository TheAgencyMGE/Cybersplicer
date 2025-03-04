#!/usr/bin/env python3
"""
Enhanced Web Proxy Server for Testing Filtering Systems
This script creates a stylish HTTP proxy that can be used to test web filtering systems.
"""

from flask import Flask, request, Response, stream_with_context, render_template_string
import requests
import logging
import argparse
import urllib.parse
import time
import os

app = Flask(__name__)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('web_proxy')

# The beautiful HTML template with CSS and JavaScript
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cybersplicer</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary: #1a0933;
            --secondary: #2d0a4e;
            --accent: #00ff9d;
            --accent-hover: #00cc7d;
            --text: #ecf0f1;
            --success: #00ff9d;
            --warning: #ff00ff;
            --danger: #ff0055;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            min-height: 100vh;
            color: var(--text);
            display: flex;
            flex-direction: column;
            position: relative;
            overflow-x: hidden;
        }
        
        /* Matrix-like background effect */
        body::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23ff00ff' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E"), 
                    linear-gradient(135deg, var(--primary), var(--secondary));
            z-index: -1;
        }
        
        /* Scanlines effect */
        body::after {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                rgba(18, 16, 16, 0) 50%, 
                rgba(0, 0, 0, 0.1) 50%
            );
            background-size: 100% 4px;
            z-index: 1000;
            pointer-events: none;
            opacity: 0.15;
        }
        
        .container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            flex: 1;
        }
        
        header {
            margin-bottom: 2rem;
            text-align: center;
            animation: fadeIn 1s ease-in-out;
        }
        
        h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            background: linear-gradient(90deg, var(--accent), #ff00ff);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            text-shadow: 0 0 10px rgba(0, 255, 157, 0.7), 0 0 20px rgba(255, 0, 255, 0.5);
            letter-spacing: 3px;
            font-family: 'Courier New', monospace;
            text-transform: uppercase;
        }
        
        .tagline {
            font-size: 1.2rem;
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 1rem;
        }
        
        .search-container {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(10px);
            animation: slideUp 0.8s ease-out;
            max-width: 800px;
            margin: 0 auto;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .search-form {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .input-group {
            position: relative;
        }
        
        .input-icon {
            position: absolute;
            left: 1.2rem;
            top: 50%;
            transform: translateY(-50%);
            color: rgba(255, 255, 255, 0.6);
            pointer-events: none;
            transition: all 0.3s ease;
        }
        
        input[type="text"] {
            width: 100%;
            padding: 1rem 1rem 1rem 3rem;
            border-radius: 8px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            background: rgba(0, 0, 0, 0.2);
            color: white;
            font-size: 1.1rem;
            transition: all 0.3s ease;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.3);
        }
        
        input[type="text"]:focus + .input-icon {
            color: var(--accent);
        }
        
        .button-group {
            display: flex;
            gap: 1rem;
        }
        
        button {
            background: var(--accent);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        button:hover {
            background: var(--accent-hover);
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .btn-clear {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .btn-clear:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .history-container {
            margin-top: 2rem;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.05);
            padding: 1.5rem;
            animation: fadeIn 1s ease-in-out 0.5s both;
        }
        
        .history-title {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .history-list {
            max-height: 200px;
            overflow-y: auto;
            scrollbar-width: thin;
            scrollbar-color: var(--accent) rgba(0, 0, 0, 0.1);
        }
        
        .history-list::-webkit-scrollbar {
            width: 6px;
        }
        
        .history-list::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.1);
            border-radius: 3px;
        }
        
        .history-list::-webkit-scrollbar-thumb {
            background-color: var(--accent);
            border-radius: 3px;
        }
        
        .history-item {
            padding: 0.8rem;
            margin-bottom: 0.5rem;
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .history-item:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .history-url {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 80%;
        }
        
        .history-time {
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.6);
        }
        
        .badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            margin-left: 0.5rem;
        }
        
        .badge-success {
            background-color: var(--success);
        }
        
        .badge-warning {
            background-color: var(--warning);
        }
        
        .badge-danger {
            background-color: var(--danger);
        }
        
        .stats {
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
        }
        
        .stat-card {
            flex: 1;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
            animation: fadeIn 1s ease-in-out 0.7s both;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-title {
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 0.5rem;
        }
        
        .stat-value {
            font-size: 1.8rem;
            font-weight: 700;
        }
        
        footer {
            text-align: center;
            padding: 2rem;
            margin-top: 2rem;
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.6);
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .notification {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            background: var(--primary);
            color: white;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
            transform: translateX(150%);
            transition: transform 0.5s cubic-bezier(0.68, -0.55, 0.27, 1.55);
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 0.8rem;
        }
        
        .notification.show {
            transform: translateX(0);
        }
        
        .notification-success {
            background: var(--success);
        }
        
        .notification-error {
            background: var(--danger);
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            .button-group {
                flex-direction: column;
            }
            
            .stats {
                flex-direction: column;
            }
        }
        
        .loading {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(5px);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }
        
        .loading.show {
            opacity: 1;
            pointer-events: all;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            border-top-color: var(--accent);
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            to {
                transform: rotate(360deg);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>CYBERSPLICER</h1>
            <p class="tagline">Neural network infiltration system :: Bypass-level ALPHA</p>
        </header>
        
        <div class="search-container">
            <form id="proxy-form" class="search-form" action="" method="get">
                <div class="input-group">
                    <input type="text" name="url" id="url-input" placeholder="Enter URL (e.g., example.com)" required>
                    <i class="fas fa-globe input-icon"></i>
                </div>
                
                <div class="button-group">
                    <button type="submit">
                        <i class="fas fa-rocket"></i> Browse
                    </button>
                    <button type="button" class="btn-clear" id="clear-button">
                        <i class="fas fa-trash"></i> Clear
                    </button>
                </div>
            </form>
        </div>
        
        <div class="history-container">
            <div class="history-title">
                <h3><i class="fas fa-history"></i> Recent Requests</h3>
                <button type="button" class="btn-clear" id="clear-history">
                    <i class="fas fa-eraser"></i> Clear History
                </button>
            </div>
            <div class="history-list" id="history-list">
                <!-- History items will be added here by JavaScript -->
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-title">Total Requests</div>
                <div class="stat-value" id="total-requests">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Successful</div>
                <div class="stat-value" id="successful-requests">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Failed</div>
                <div class="stat-value" id="failed-requests">0</div>
            </div>
        </div>
    </div>
    
    <footer>
        <p>Stealth Proxy &copy; {{ current_year }} | Advanced Web Filtering Test Tool</p>
    </footer>
    
    <div class="notification" id="notification">
        <i class="fas fa-info-circle"></i>
        <span id="notification-message">Notification message</span>
    </div>
    
    <div class="loading" id="loading">
        <div class="spinner"></div>
    </div>
    
    <script>
        // Store browsing history in local storage
        let browsing_history = JSON.parse(localStorage.getItem('proxy_history') || '[]');
        let stats = JSON.parse(localStorage.getItem('proxy_stats') || '{"total": 0, "success": 0, "failed": 0}');
        
        // Update stats display
        function updateStats() {
            document.getElementById('total-requests').textContent = stats.total;
            document.getElementById('successful-requests').textContent = stats.success;
            document.getElementById('failed-requests').textContent = stats.failed;
            localStorage.setItem('proxy_stats', JSON.stringify(stats));
        }
        
        // Display notification
        function showNotification(message, type = 'success') {
            const notification = document.getElementById('notification');
            const msgElement = document.getElementById('notification-message');
            
            notification.className = 'notification';
            notification.classList.add('show');
            
            if (type === 'success') {
                notification.classList.add('notification-success');
            } else {
                notification.classList.add('notification-error');
            }
            
            msgElement.textContent = message;
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        }
        
        // Add URL to history
        function addToHistory(url, success = true) {
            // Limit history to 10 items
            if (browsing_history.length >= 10) {
                browsing_history.pop();
            }
            
            // Add new item to the front
            browsing_history.unshift({
                url: url,
                time: new Date().toISOString(),
                success: success
            });
            
            // Update stats
            stats.total++;
            if (success) {
                stats.success++;
            } else {
                stats.failed++;
            }
            
            // Save to local storage
            localStorage.setItem('proxy_history', JSON.stringify(browsing_history));
            updateStats();
            renderHistory();
        }
        
        // Render history list
        function renderHistory() {
            const historyList = document.getElementById('history-list');
            historyList.innerHTML = '';
            
            if (browsing_history.length === 0) {
                historyList.innerHTML = '<div class="history-item">No browsing history yet</div>';
                return;
            }
            
            browsing_history.forEach((item, index) => {
                const historyItem = document.createElement('div');
                historyItem.className = 'history-item';
                
                const formattedTime = new Date(item.time).toLocaleTimeString();
                const statusBadge = item.success ? 
                    '<span class="badge badge-success">Success</span>' : 
                    '<span class="badge badge-danger">Failed</span>';
                
                historyItem.innerHTML = `
                    <div class="history-url">${item.url} ${statusBadge}</div>
                    <div class="history-time">${formattedTime}</div>
                `;
                
                historyItem.addEventListener('click', () => {
                    document.getElementById('url-input').value = item.url;
                });
                
                historyList.appendChild(historyItem);
            });
        }
        
        // Handle form submission
        document.getElementById('proxy-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const urlInput = document.getElementById('url-input');
            let url = urlInput.value.trim();
            
            // Show loading indicator
            document.getElementById('loading').classList.add('show');
            
            // Make sure the URL has a scheme
            if (!url.startsWith(('http://', 'https://'))) {
                url = 'https://' + url;
            }
            
            // Add to history and redirect
            addToHistory(url);
            window.location.href = `?url=${encodeURIComponent(url)}`;
        });
        
        // Clear input button
        document.getElementById('clear-button').addEventListener('click', function() {
            document.getElementById('url-input').value = '';
        });
        
        // Clear history button
        document.getElementById('clear-history').addEventListener('click', function() {
            browsing_history = [];
            localStorage.setItem('proxy_history', JSON.stringify(browsing_history));
            renderHistory();
            showNotification('History cleared successfully');
        });
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            renderHistory();
            updateStats();
            
            // Check for URL parameter to add to history
            const urlParams = new URLSearchParams(window.location.search);
            const url = urlParams.get('url');
            
            if (url) {
                document.getElementById('url-input').value = url;
            }
        });
    </script>
</body>
</html>
"""

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'])
def proxy(path):
    """
    Main proxy function that handles all incoming requests
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
            verify=True  # You might want to set this to False for testing purposes
        )
        
        # Create a response object
        response_headers = {key: value for key, value in resp.headers.items() if key.lower() not in ['transfer-encoding']}
        
        # Function to rewrite links in HTML content
        def generate():
            for chunk in resp.iter_content(chunk_size=4096):
                # For HTML content, you might want to rewrite links
                # This is a simplified example and could be expanded
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
                '<p class="tagline">Secure, anonymous web browsing with advanced filtering bypass</p>',
                f'<p class="tagline" style="color: #e74c3c;">Error: {e}</p>'
            ),
            current_year=time.strftime("%Y")
        )
        return error_html, 500

def main():
    """
    Main function to parse arguments and start the server
    """
    parser = argparse.ArgumentParser(description='Enhanced Web Proxy Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', default=8080, type=int, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    logger.info(f"Starting proxy server on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()