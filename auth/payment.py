import flask as f
from . import auth

@auth.route('/credit', methods=['GET', 'POST'])
def register_credit():
    if f.g.user.get('uid', -1) != -1: return f.redirect(f.url_for('auth.login'))
   
   
    
    return f.redirect(f.url_for('index')) 