# Cybersplicer - Web Proxy Server

A stylish HTTP proxy server that can be used to test web filtering systems. This tool provides a sleek interface for browsing websites through a proxy with request history tracking and statistics.

## Features

- Modern, cyberpunk-themed UI
- Request history with success/failure tracking
- Statistics dashboard
- Easy-to-use interface
- Streaming response handling
- Support for all HTTP methods

## Requirements

- Python 3.6+
- Flask
- Requests

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/cybersplicer.git
   cd cybersplicer
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the server:

```
python proxy.py
```

Or with custom host and port:

```
python proxy.py --host 127.0.0.1 --port 8000
```

Then open your browser and navigate to `http://localhost:8080` (or your custom host/port).

## Options

- `--host`: Host address to bind to (default: 0.0.0.0)
- `--port`: Port to listen on (default: 8080)
- `--debug`: Enable Flask debug mode

## How It Works

The server functions as a proxy between the client and the target website. When you enter a URL:

1. The proxy forwards your request to the target server
2. It receives the response and streams it back to your browser
3. All navigation history is stored locally in your browser

## Security Considerations

This tool is designed for testing and educational purposes only. Use responsibly and only on networks you have permission to test.

## License

MIT License - See LICENSE file for details.