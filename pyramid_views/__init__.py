
# It must be possible to import this file with 
# none of the package's dependencies installed

__version__ = "1.2.8"

session = None
def configure_views(session_):
    global session
    session = session_