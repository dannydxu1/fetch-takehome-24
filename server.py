"""
A simple Flask application to manage points transactions for different payers.

This application provides API endpoints to add transactions, spend points, and check the balance for a user.
"""

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transactions.db'
db = SQLAlchemy(app)


class Transaction(db.Model):
    """
    Model for storing transaction data.

    Attributes:
        id (int): Primary key for the transaction.
        payer (str): The name of the payer.
        points (int): The total points in the transaction.
        current_points (int): The points currently available from this transaction.
        timestamp (datetime): The timestamp of the transaction.
    """
    id = db.Column(db.Integer, primary_key=True)
    payer = db.Column(db.String(75), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    current_points = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    """
    Home endpoint that returns a welcome message.

    Returns:
        Response: JSON response with a welcome message.
    """
    return jsonify(message="Hello World!")

@app.route('/add', methods=['POST'])
def create_transaction():
    """
    Endpoint to add a new transaction.

    Expects:
        JSON data with 'payer', 'points', and 'timestamp' keys.

    Returns:
        Response: JSON response with a success message and the new transaction ID,
        or an error message with an appropriate HTTP status code.
    """
    data = request.get_json()

    if not data or 'payer' not in data or 'points' not in data or 'timestamp' not in data:
        return jsonify({"error": "Invalid Request. Please provide 'payer', 'points', and 'timestamp' in the JSON body."}), 400

    payer = data['payer']
    points = data.get('points', 0)
    try:
        timestamp = datetime.fromisoformat(data['timestamp'])
    except ValueError:
        return jsonify({"error": "Invalid Request. 'timestamp' must be in 'YYYY-MM-DDTHH:MM:SS' format."}), 400

    if points < 0:
        # Handle negative point transactions by adding them from the oldest transactions with same payer, in order, until debt is satisfied.
        transactions = Transaction.query.filter(Transaction.payer == payer, Transaction.current_points>0).order_by(Transaction.timestamp).all()
        remaining_points = points

        for transaction in transactions:
            if remaining_points < 0:
                if transaction.current_points >= abs(remaining_points):
                    transaction.current_points += remaining_points
                    remaining_points = 0
                else:
                    remaining_points += transaction.current_points
                    transaction.current_points = 0

                db.session.commit()

            if remaining_points == 0:
                break

        if remaining_points != 0:
            return jsonify({"error": "Not enough points to complete the transaction."}), 400

        new_transaction = Transaction(payer=payer, points=points, current_points=0, timestamp=timestamp)
    else:
        new_transaction = Transaction(payer=payer, points=points, current_points=points, timestamp=timestamp)
    db.session.add(new_transaction)
    db.session.commit()

    return jsonify({"message": "Transaction created successfully.", "id": new_transaction.id}), 200

@app.route('/spend', methods=['POST'])
def spend_points():
    """
    Endpoint to spend points.

    Expects:
        JSON data with 'points' key indicating the total points to spend.

    Returns:
        Response (200 OK): JSON response with a list of deductions per payer, sorted by the oldest transaction.
            Example response:
            ```json
                [
                    {
                      "payer": "DANNON",
                      "points": -100
                    },
                    {
                      "payer": "UNILEVER",
                      "points": -200
                    },
                    {
                      "payer": "MILLER COORS",
                      "points": -4700
                    }
                ]
            ```
    """
    data = request.get_json()
    if not data or 'points' not in data:
        return jsonify({"error": "Invalid Request. Please provide 'points' in the JSON body."}), 400
    
    points_to_spend = data.get('points', 0)
    if points_to_spend <= 0:
        return jsonify({"error": "Invalid Request. 'points' cannot be non-positive."}), 400
    
    total_points_available = db.session.query(db.func.sum(Transaction.current_points)).scalar()
    if total_points_available is None or total_points_available < points_to_spend:
        return jsonify({"error": "Invalid request. Not enough points available to spend."}), 400
    
    transactions = db.session.query(Transaction).order_by(Transaction.timestamp.asc()).all()
    spending_transactions = {}

    for transaction in transactions:
        if points_to_spend == 0:
            break
        
        transaction_points_remaining = transaction.current_points
        if transaction_points_remaining <= 0:
            continue

        transaction_payer = transaction.payer
        points_spent = min(transaction_points_remaining, points_to_spend)

        if transaction_payer not in spending_transactions:
            spending_transactions[transaction_payer] = 0

        spending_transactions[transaction_payer] -= points_spent
        points_to_spend -= points_spent
        transaction.current_points -= points_spent # Keep track of used/consumed points using 'current_points' field while preserving transaction history with 'points' field.
        db.session.commit()

    if points_to_spend == 0:
        spending_response = [{"payer": payer, "points": points} for payer, points in spending_transactions.items()]
        return jsonify(spending_response), 200
    else:
        return jsonify({"error": "Unexpected error occurred."}), 400

@app.route('/balance', methods=['GET'])
def get_balance():
    """
    Endpoint to get the current point balance per payer.

    Returns:
        Response: JSON response with the balance per payer, sorted by oldest inital transaction.
            Example response:
            ```json
            {
                "DANNON": 1000,
                "UNILEVER": 0,
                "MILLER COORS": 5300,
            }
            ```
    """
    balances = db.session.query(
        Transaction.payer,
        db.func.sum(Transaction.current_points).label('total_points')
    ).group_by(Transaction.payer).order_by(db.func.min(Transaction.timestamp).asc()).all()

    balance_response = {}
    for payer, points in balances: 
        balance_response[payer] = points

    response = app.response_class(
        response=json.dumps(balance_response, indent=4),
        status=200,
        mimetype='application/json'
    )

    return response

if __name__ == '__main__':
    app.run(debug=True, port=8000)
