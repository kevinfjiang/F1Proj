import flask as f
import sqlalchemy
def update_payout()->None:
    if f.g.conn['uid']==-1: return
    try:
        f.g.conn.execute(f"""
                        WITH recent_complete_bids AS
                        (SELECT Bids.uid AS uid, Bids.betID as betId, Bids.wager AS wager, B.odds AS odds, B.isWon AS isWon
                        FROM Bids
                        INNER JOIN (SELECT * 
                                    FROM Bet
                                    WHERE completed=True) B
                            ON Bids.betId=B.betId
                        WHERE Bids.uid={f.g.conn['uid']}
                        AND Bids.wager>0)
                            
                        UPDATE Member
                        SET balance = balance + (SELECT SUM(CASE WHEN odds>0 THEN (wager*odds)/100 ELSE (wager*100)/odds END )
                                                FROM recent_complete_bids
                                                WHERE isWon=True)
                        WHERE uid={f.g.user['uid']};
                        
                        UPDATE Bids
                        SET wager=-1
                        WHERE (uid, betId) IN (SELECT uid, betID FROM recent_complete_bids)
                        """)
    except (sqlalchemy.exc.ProgrammingError) as e:
        print(e)
        print("Failure to update")
    