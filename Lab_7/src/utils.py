import src.models as models
import src.db as db


def get_transaction_by_wallet_id(wallet_id: int) -> dict:
    transaction = db.session.query(models.Transaction).filter(models.Transaction.wallet_id_1 == wallet_id).first()
    if transaction is None:
        return {}
    res = {'wallet_id_1': transaction.wallet_id_1, 'wallet_id_2': transaction.wallet_id_2,
           'amount_of_money': transaction.amount_of_money, "currency": transaction.currency}
    return res
