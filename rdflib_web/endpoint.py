"""
This is a Flask Blueprint for a SPARQL Endpoint
confirming to the SPARQL 1.0 Protocol.

You can add the blueprint `endpoint` object to your own application::

  from rdflib_web.endpoint import endpoint
  app = Flask(__name__)
  ...
  app.config['graph'] = my_rdflib_graph
  app.register_blueprint(endpoint)

Or the application can be started from commandline::

  python -m rdflib_web.endpoint <RDF-file>

and the endpoint will be available at http://localhost:5000

You can also start the server from your application by calling the :py:func:`serve` method
or get the application object yourself by called :py:func:`get` function

"""
try:
    from flask import Blueprint, Flask, current_app, render_template, request, make_response, Markup, g
except:
    raise Exception("Flask not found - install with 'easy_install flask'")

import rdflib

import sys
import time
import traceback

import mimeutils

from rdflib_web import htmlresults
from rdflib_web import __version__

endpoint = Blueprint('sparql_endpoint', __name__)

@endpoint.record
def setup(state):
    """Do a bit of application configuration"""

    state.app.jinja_env.globals["rdflib_version"]=rdflib.__version__
    state.app.jinja_env.globals["rdflib_web_version"]=__version__
    state.app.jinja_env.globals["python_version"]="%d.%d.%d"%(sys.version_info[0], sys.version_info[1], sys.version_info[2])
    state.app.before_first_request(__register_namespaces)


@endpoint.route("/sparql", methods=['GET', 'POST'])
def query():
    try:
        q=request.values["query"]

        a=request.headers["Accept"]

        format="xml" # xml is default
        if mimeutils.HTML_MIME in a:
            format="html"
        if mimeutils.JSON_MIME in a:
            format="json"

        # output parameter overrides header
        format=request.values.get("output", format)

        mimetype=mimeutils.resultformat_to_mime(format)

        # force-accept parameter overrides mimetype
        mimetype=request.values.get("force-accept", mimetype)

        # pretty=None
        # if "force-accept" in request.values:
        #     pretty=True

        # default-graph-uri

        results=g.graph.query(q).serialize(format=format)
        if format=='html':
            response=make_response(render_template("results.html", results=Markup(unicode(results,"utf-8")), q=q))
        else:
            response=make_response(results)

        response.headers["Content-Type"]=mimetype
        return response
    except:
        return "<pre>"+traceback.format_exc()+"</pre>", 400


#@endpoint.route("/") # bound later
def index():
    return render_template("index.html")


def __register_namespaces():
    for p,ns in current_app.config["graph"].namespaces():
        htmlresults.nm.bind(p,ns,override=True)

@endpoint.before_request
def __start():
    g.start=time.time()

@endpoint.after_request
def __end(response):
    diff = time.time() - g.start
    if response.response and response.content_type.startswith("text/html") and response.status_code==200:
        response.response[0]=response.response[0].replace('__EXECUTION_TIME__', "%.3f"%diff)
        response.headers["Content-Length"]=len(response.response[0])
    return response


def serve(graph_,debug=False):
    """Serve the given graph on localhost with the LOD App"""

    a=get(graph_)
    a.run(debug=debug)
    return a

@endpoint.before_app_request
def _set_graph():
    """ This sets the g.graph if we are using a static graph
    set in the configuration"""
    if "graph" in current_app.config and current_app.config["graph"]!=None:
        g.graph=current_app.config["graph"]


def get(graph_):
    """
    Get the LOD Flask App setup to serve the given graph
    """
    app = Flask(__name__)
    app.config["graph"]=graph_

    app.register_blueprint(endpoint)
    app.add_url_rule('/', 'index', index)

    return app


def _main(g, out, opts):
    import rdflib
    import sys
    if len(g)==0:
        import bookdb
        g=bookdb.bookdb

    serve(g, True)

def main():
    from rdflib.extras.cmdlineutils import main as cmdmain
    cmdmain(_main, stdin=False)

if __name__=='__main__':
    main()