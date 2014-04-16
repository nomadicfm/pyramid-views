
# It must be possible to import this file with 
# none of the package's dependencies installed

__version__ = "1.0.3"

session = None
def configure_views(session_):
    global session
    if callable(session_):
        session = session_()
    else:
        session = session_