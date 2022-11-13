from flask import Flask
from src.views import user
from src.views import wallet
from src.views import transactions

app = Flask(__name__)

app.register_blueprint(user.user_bp)
app.register_blueprint(wallet.wallet_bp)
app.register_blueprint(transactions.transaction_bp)
