class Ledger:
    """Simple in-memory ledger for recording transactions."""
    def __init__(self):
        self.transactions = []

    def add_transaction(self, amount: float, description: str = ""):
        """
        Add a transaction to the ledger.

        :param amount: Positive for credit, negative for debit.
        :param description: Brief description of the transaction.
        """
        self.transactions.append({
            'amount': amount,
            'description': description
        })

    def get_balance(self) -> float:
        """Return the sum of all transaction amounts."""
        return sum(t['amount'] for t in self.transactions)

    def list_transactions(self) -> list:
        """Return all recorded transactions."""
        return self.transactions

def main():
    """Demo usage of Ledger."""
    ledger = Ledger()
    ledger.add_transaction(100, "Deposit")
    ledger.add_transaction(-50, "Withdrawal")
    ledger.add_transaction(200, "Deposit")
    print("Transactions:")
    for t in ledger.list_transactions():
        print(f"Amount: {t['amount']}, Description: {t['description']}")
    print("\nCurrent Balance:", ledger.get_balance())

if __name__ == "__main__":
    main()
