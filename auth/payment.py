import flask as f
from auth import auth
import helper.helper as helper
import logging
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
                                SET credit_card=%s
                                WHERE uid={f.g.user['uid']}
                                AND PassHash='{f.g.user.get('passhash', -1)}'
                                """, (c,))
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

    
    return helper.render('auth/credit.html', error=error) 

@auth.route('/addfunds', methods=['GET', 'POST'])
def transfer_credit():
    error=None
    if f.g.user.get('uid', -1) == -1: return f.redirect(f.url_for('bets.show_account'))
    if f.request.method == 'POST':
        try:
            c = f.g.conn.execute(f"""
                                SELECT credit_card
                                FROM Member
                                WHERE uid={f.g.user['uid']}
                                AND PassHash='{f.g.user.get('passhash', -1)}'
                                """)
            card = next(c)
            if card[0] and (valid_card := checksum(card[0])):
                c = f.g.conn.execute(f"""
                                UPDATE Member
                                SET balance = balance + {int(f.request.form['addfund'])}
                                WHERE uid={f.g.user['uid']}
                                AND credit_card='{valid_card}'
                                """)
                return f.redirect(f.url_for('bets.show_account'))
            else: error="No card under your user"
        except (sqlalchemy.exc.ProgrammingError, sqlalchemy.exc.OperationalError, StopIteration) as e:
            logging.warn(f"Error in execution, usually because of lack of credit card, {e}")
            error="No card under your user"
        except ValueError:
            error="Please enter a valid amount of funds to transfer with only integers"

    return helper.render('auth/addfunds.html', error=error)