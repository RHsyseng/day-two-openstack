import os
def application(environ, start_response):
        ENVIRONMENT_VARIABLES = ['APIURL']
        for key in ENVIRONMENT_VARIABLES:
                os.environ[key] = environ.get(key)

        from glog_ui import app
        return app(environ, start_response)
