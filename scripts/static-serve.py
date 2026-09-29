import http.server, os, mimetypes

class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = super().translate_path(path)
        if not os.path.exists(path) and not path.endswith('/'):
            for ext in ('.html', '.htm'):
                if os.path.exists(path + ext):
                    return path + ext
        return path

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

os.chdir('/Users/zharris/arcs-v9/public')
http.server.HTTPServer(('127.0.0.1', 3100), Handler).serve_forever()
