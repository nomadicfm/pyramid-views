
# It must be possible to import this file with 
# none of the package's dependencies installed

__version__ = "1.0.0"

session = None
def configure_views(scoped_session):
    global session
    session = scoped_session()