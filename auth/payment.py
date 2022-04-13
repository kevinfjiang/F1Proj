import flask as f
from auth import auth
import sqlalchemy

def checksum(cardNo: str)->str:
    if cardNo=="-1": return False
    card_number = ''.join(filter(lambda l: l.isdecimal(), cardNo))
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    if checksum % 10==0: return ''.join(card_number)
    else: return False
    

@auth.route('/credit', methods=['GET', 'POST'])
def register_credit():
    error=None
    if f.g.user.get('uid', -1) == -1: return f.redirect(f.url_for('auth.login'))
    if f.request.method == 'POST':
        if (c := checksum(str(f.request.form.get('credit_card', -1)))):
            try:
                f.g.conn.execute(f"""
                                UPDATE Member
                                SET credit_card='{c}'
                                WHERE uid={f.g.user['uid']}
                                AND PassHash='{f.g.user.get('passhash', -1)}'
                                """)
                c = f.g.conn.execute(f"""
                                SELECT credit_card
                                FROM Member
                                WHERE credit_card='{c}'
                                """)
                return f.redirect(f.url_for('index'))
            except sqlalchemy.exc.ProgrammingError:
                error="Invalid credentials error"
        else:
            error="Invalid credit card number"

    
    return f.render_template('auth/credit.html', error=error) 

@auth.route('/addfunds', methods=['GET', 'POST'])
def transfer_credit():
    error=None
    if f.g.user.get('uid', -1) == -1: return f.redirect(f.url_for('auth.login'))
    if f.request.method == 'POST':
        try:
            c = f.g.conn.execute(f"""
                                SELECT credit_card
                                FROM Member
                                WHERE uid='{f.g.user['uid']}'
                                AND PassHash='{f.g.user.get('passhash', -1)}'
                                """)
            if (valid_card := checksum(next(c)[0])):
                f.g.conn.execute(f"""
                                UPDATE Member
                                SET balance = balance + {int(f.request.form['addfund'])}
                                WHERE uid={f.g.user['uid']}
                                AND PassHash='{f.g.user.get('passhash', -1)}'
                                AND credit_card='{valid_card}'
                                """)
                return f.redirect(f.url_for('index'))
        except (sqlalchemy.exc.ProgrammingError, StopIteration):
            error="No card under your user"
        except ValueError:
            error="Please enter a valid amount of funds to transfer with only integers"
    
    return f.render_template('auth/addfunds.html', error=error)