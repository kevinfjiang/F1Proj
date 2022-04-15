
"""
Columbia W4111 Intro to databases
Example webserver
To run locally
    python server.py
Go to http://localhost:8111 in your browser
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
import sqlalchemy
from flask import Flask, request, url_for, render_template, g, redirect, Response, session


from auth import auth
from bets import bets, payout
from leaderboard.leaderboard import leaderboard
from leaderboard.stats import stats 

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.register_blueprint(auth)
app.register_blueprint(leaderboard)
app.register_blueprint(bets)
app.register_blueprint(stats)
app.secret_key=os.getenv('secret_key')

# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = os.getenvenv('user')
DB_PASSWORD = os.getenvenv('password')

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

# This line creates a database engine that knows how to connect to the URI above
engine = sqlalchemy.create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/proj1part2")

@app.before_request
def start_connect():
    """
    This function is run at the beginning of every web request 
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request
    The variable g is globally accessible
    """
    g.user={'uid': -1,
          'passhash': -1}
    try:
        g.conn = engine.connect()
        load_user()
        payout.update_payout()
    except:
        print ("uh oh, problem connecting to database")
        import traceback; traceback.print_exc()
        

def load_user():
    g.user={'uid': -1,
          'passhash': -1}
    if bool(uid := session.get("uid")) & bool(h := session.get("passhash")): # non shortcurcuit or
        try:
            raw_return = g.conn.execute("""
                                        SELECT *
                                        FROM Member
                                        WHERE uid=%(uid)s
                                        AND PassHash=%(hash)s
                                        """, {'uid': uid,
                                              'hash': h})
            g.user = dict(zip(raw_return.keys(), next(raw_return)))
        except (TypeError, sqlalchemy.exc.ProgrammingError, sqlalchemy.exc.OperationalError, StopIteration) as e:
            print(e)
            g.user={'uid': -1,
                    'passhash': -1}
            session.pop('uid')
            session.pop('passhash') # Definitely log this
            # If we get here, we go to the else and clean session

@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't the database could run out of memory!
    """
    try:
        g.user=None
        if hasattr(g, "conn"):
            g.conn.close()
    except Exception as e:
        print(e)
        pass


@app.route('/')
def index():
    """
    request is a special object that Flask provides to access web request information:
    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2
    See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
    """

    # DEBUG: this is debugging code to see what request looks like
    print(request.args)
    #
    # render_template looks in the templates/ folder for files.
    #
    return redirect(url_for("stats.display_stat"))


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using
            python server.py
        Show the help text using
            python server.py --help
        """

        HOST, PORT = host, port
        print ("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


    run()
