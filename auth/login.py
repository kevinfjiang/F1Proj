import flask as f
import hashlib
from auth import auth
import sqlalchemy
import psycopg2

INVALID_CHAR="Invalid character found in username"
USER_NOT_FOUND="The username or password you are looking for cannot be found"
BAD_REQUEST="Something went wrong..."
INTERNAL_DB_REGISTER_ERROR="Database could not register user. sorry about that \n ERROR:{}"


def p_hash(password) -> str: 
    if not isinstance(password, str) or len(password)<4: return None
    return hashlib.sha224(password.encode('UTF-8')).hexdigest()


@auth.route('/login', methods=['GET', 'POST'])
def login(error=None): 
    error = None
    if f.g.user.get('uid', -1) != -1: return f.redirect(f.url_for('index'))
    if f.request.method == 'POST':
        if not (h := p_hash(f.request.form['password'])):
            error=USER_NOT_FOUND
        if not error:
            try:
                c = f.g.conn.execute("""
                                    SELECT uid
                                    FROM Member
                                    WHERE Email=%(email)s
                                    AND PassHash=%(hash)s
                                    """, {'email': f.request.form['username'],
                                        'hash': h})
                if (uid := list(c)):
                    f.session['uid']=str(uid[0][0])
                    f.session['passhash']=h
                    return f.redirect(f.url_for('index'))
                else:
                    error=USER_NOT_FOUND
            except(TypeError, sqlalchemy.exc.ProgrammingError, sqlalchemy.exc.OperationalError, StopIteration)  as e:
                error=INTERNAL_DB_REGISTER_ERROR.format(e)
            
    return f.render_template('auth/login.html', error=error)

@auth.route('/logout')
def logout():
   # remove the username from the session if it is there
   f.session.pop('uid', None)
   f.session.pop('passhash', None)
   return f.redirect(f.url_for('index')) 

@auth.route('/signup', methods=['GET', 'POST']) 
def signup():
    if f.g.user.get('uid', -1) != -1: return f.redirect(f.url_for('index'))
    error = None
    if f.request.method == 'GET': return f.render_template('auth/signup.html')
    if f.request.method == 'POST': 
        if f.request.form.get("password") != f.request.form.get("confirm_password"):
            error="Password and Confirm Password do not match"
        elif not (h := p_hash(f.request.form['password'])):
            error=USER_NOT_FOUND
        if not error:
            try:
                f.g.conn.execute("""
                                INSERT INTO Member 
                                (email, PassHash, name, address)
                                Values
                                (%(email)s, %(password)s, %(name)s, %(address)s)
                                """, {'password': h,
                                      **f.request.form}) # Make a create
                c = f.g.conn.execute("""
                                SELECT uid
                                FROM Member
                                WHERE Email=%(email)s
                                AND PassHash=%(hash)s
                                """, {'email': f.request.form['username'],
                                        'hash': h})
                if (uid := list(c)):
                    f.session['uid']=str(uid[0][0])
                    f.session['passhash']=h
                    return f.redirect(f.url_for('index'))
                else:
                    error=USER_NOT_FOUND
            except psycopg2.errors.UniqueViolation as e: # Have better error handling
                error="Duplicate user, try logging in"
            except Exception as e: # Have better error handling
                error=INTERNAL_DB_REGISTER_ERROR.format(e)
        return f.render_template('auth/signup.html', error=error) 


