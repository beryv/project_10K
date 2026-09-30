from database import SessionLocal
from models import Account, Branch, Client, Employee, Transaction


def seed_database():
  db = SessionLocal()
  try:
    if not db.query(Branch).first():
      print("Seeding database with 100 entries per table...")

      # Branches
      branches = []
      cities = [
          "New York",
          "Chicago",
          "Los Angeles",
          "Houston",
          "Phoenix",
          "Philadelphia",
          "San Antonio",
          "San Diego",
          "Dallas",
          "San Jose",
      ]
      for i in range(1, 101):
        branch = Branch(name=f"Branch #{i}", city=cities[i % len(cities)])
        branches.append(branch)
      db.add_all(branches)
      db.commit()
      all_branches = db.query(Branch).all()

      # Employees
      employees = []
      roles = [
          "Teller",
          "Branch Manager",
          "Loan Officer",
          "Financial Advisor",
          "Customer Service",
      ]
      for i in range(1, 101):
        emp = Employee(
            name=f"Employee Name {i}",
            role=roles[i % len(roles)],
            branch_id=all_branches[i % len(all_branches)].id,
        )
        employees.append(emp)
      db.add_all(employees)
      db.commit()

      # Clients
      clients = []
      for i in range(1, 101):
        client = Client(
            name=f"Client User {i}", email=f"client.user{i}@example.com"
        )
        clients.append(client)
      db.add_all(clients)
      db.commit()
      all_clients = db.query(Client).all()

      # Accounts
      accounts = []
      acc_types = ["Checking", "Savings"]
      for i in range(1, 101):
        account = Account(
            account_number=f"ACC-{1000 + i}",
            balance=float(500 + (i * 137) % 20000),
            account_type=acc_types[i % len(acc_types)],
            client_id=all_clients[i - 1].id,
        )
        accounts.append(account)
      db.add_all(accounts)
      db.commit()
      all_accounts = db.query(Account).all()

      # Transactions
      transactions = []
      tx_types = ["Deposit", "Withdrawal"]
      for i in range(1, 101):
        tx = Transaction(
            amount=float(50 + (i * 19) % 1000),
            transaction_type=tx_types[i % len(tx_types)],
            account_id=all_accounts[i % len(all_accounts)].id,
        )
        transactions.append(tx)
      db.add_all(transactions)
      db.commit()

      print("Mass database seeding completed successfully!")

    first_client = db.query(Client).order_by(Client.id).first()
    if first_client:
      has_current_account = (
          db.query(Account)
          .filter(
              Account.client_id == first_client.id,
              Account.account_type.in_(["Current", "Checking"]),
          )
          .first()
      )
      if not has_current_account:
        db.add(
            Account(
                account_number="DEMO-CURRENT-001",
                balance=0,
                account_type="Current",
                client_id=first_client.id,
            )
        )
        db.commit()
  finally:
    db.close()