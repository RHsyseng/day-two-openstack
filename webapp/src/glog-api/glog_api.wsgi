import os
def application(environ, start_response):
        ENVIRONMENT_VARIABLES = ['MONGODB','MONGODB_USER','MONGODB_PASSWORD','MONGODB_DATABASE','MONGODB_HOST']
        for key in ENVIRONMENT_VARIABLES:
                os.environ[key] = environ.get(key)

        from glog_api import app
        return app(environ, start_response)
