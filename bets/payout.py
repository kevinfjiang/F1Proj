import flask as f
import sqlalchemy
import psycopg2
def update_payout()->None:
    if f.g.user['uid']==-1: return
    try:
        f.g.conn.execute(f"""
                        WITH recent_complete_bids AS
                        (SELECT Bids.uid AS uid, Bids.betID as betId, Bids.wager AS wager, B.odds AS odds, B.isWon AS isWon
                        FROM Bids
                        INNER JOIN (SELECT * 
                                    FROM Bet
                                    WHERE completed=True) B
                            ON Bids.betId=B.betId
                        WHERE Bids.uid={f.g.user['uid']}
                        AND Bids.wager>0)
                            
                        UPDATE Member
                        SET balance = balance +  (SELECT COALESCE(SUM(CASE WHEN odds>0 THEN (wager*odds)/100 ELSE (wager*100)/odds END ), 0)
                                                  FROM recent_complete_bids
                                                  WHERE isWon=True)
                        WHERE uid={f.g.user['uid']}""")
        f.g.conn.execute(f"""
                        WITH recent_complete_bids AS
                        (SELECT Bids.uid AS uid, Bids.betID as betId, Bids.wager AS wager, B.odds AS odds, B.isWon AS isWon
                        FROM Bids
                        INNER JOIN (SELECT * 
                                    FROM Bet
                                    WHERE completed=True) B
                            ON Bids.betId=B.betId
                        WHERE Bids.uid={f.g.user['uid']}
                        AND Bids.wager>0)
                        
                        UPDATE Bids
                        SET wager=0
                        WHERE (uid, betId) IN (SELECT uid, betID FROM recent_complete_bids)
                        """)

    except (sqlalchemy.exc.ProgrammingError, psycopg2.errors.UniqueViolation) as e:
        print(e)
        print("Failure to update")
    