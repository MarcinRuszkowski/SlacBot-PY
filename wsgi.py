from main import app

def application(environ, start_response):
    return app.wsgi_app(environ, start_response)
