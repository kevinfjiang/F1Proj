import flask as f
import hashlib
INVALID_CHAR="Invalid character found in username"
USER_NOT_FOUND="The username or password you are looking for cannot be found"
BAD_REQUEST="Something went wrong..."
INTERNAL_DB_REGISTER_ERROR="Database could not register user. sorry about that \n ERROR:{}"

auth = f.Blueprint('auth', __name__, template_folder='templates/auth')

def sanitize(*args) -> bool: return True
def p_hash(password) -> str: 
    if not isinstance(password, str) or len(password)<4: return None
    return hashlib.sha224(password.encode('UTF-8')).hexdigest()


@auth.route('/login', methods=['GET', 'POST'])
def login(): 
    error = None
    if f.request.method == 'POST':
        if not sanitize(f.request.form['username']): 
            error=INVALID_CHAR
        if not (h := p_hash(f.request.form['password'])):
            error=USER_NOT_FOUND
        if not error:
            c = f.g.conn.execute(f"""
                            SELECT uid
                            FROM Member
                            WHERE Email='{f.request.form['username']}'
                            AND PassHash='{h}'
                            """)
            if (uid := list(c)):
                f.session['uid']=str(uid[0][0])
                f.session['passhash']=h
                return f.redirect(f.url_for('index'))
            else:
                error=USER_NOT_FOUND
    return f.render_template('auth/login.html',name="dog", error=error)

@auth.route('/logout')
def logout():
   # remove the username from the session if it is there
   f.session.pop('uid', None)
   f.session.pop('passhash', None)
   return f.redirect(f.url_for('index')) 

@auth.route('/signup', methods=['GET', 'POST']) # TODO prevent signed in from getting here
def signup():
    error = None
    if f.request.method == 'GET': return f.render_template('auth/signup.html')
    if f.request.method == 'POST': 
        #TODO Lots of checking here will be necessary
        # if not sanitize(f.request.form['email']): 
        #     error=INVALID_CHAR
        if not (h := p_hash(f.request.form['password'])):
            error=USER_NOT_FOUND
        if not error:
            try:
                f.g.conn.execute(f"""
                                INSERT INTO Member 
                                (email, PassHash, name, address)
                                Values
                                ('{f.request.form["email"]}', '{h}', '{f.request.form["name"]}', '{f.request.form["address"]}')
                                """) # Make a create
                c = f.g.conn.execute(f"""
                                    SELECT uid
                                    FROM Member
                                    WHERE Email='{f.request.form['email']}'
                                    AND PassHash='{h}'
                                    """)
                if (uid := list(c)):
                    f.session['uid']=str(uid[0][0])
                    f.session['passhash']=h
                    return f.redirect(f.url_for('index'))
                else:
                    error=USER_NOT_FOUND
            except Exception as e: # Have better error handling
                error=INTERNAL_DB_REGISTER_ERROR.format(str(e))  
        return f.render_template('auth/signup.html', error=error) 

@auth.route('/another')
def another():
    return f.render_template('anotherfile.html', auth=f.g.user['passhash'])
            
