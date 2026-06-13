from datetime import datetime

# ==============================================================================
# БЛОК 0: СТРУКТУРНІ ЕЛЕМЕНТИ ВАРІАНТА
# ==============================================================================

class Category:
    FOOD = "FOOD"
    TRANSPORT = "TRANSPORT"
    SALARY = "SALARY"
    ENTERTAINMENT = "ENTERTAINMENT"


class Transaction:
    def __init__(self, category: str, amount: float):
        self.category = category
        self.amount = amount

    @property
    def amount(self) -> float:
        return self._amount

    @amount.setter
    def amount(self, value: float):
        if value <= 0:
            raise ValueError("Сума транзакції повинна бути більшою за 0!")
        self._amount = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.category}', amount={self.amount})"


class Income(Transaction):
    def __str__(self) -> str:
        return f"Income('{self.category}', amount={self.amount})"


class Expense(Transaction):
    def __str__(self) -> str:
        return f"Expense('{self.category}', amount={self.amount})"


# ==============================================================================
# 1. КЛАС ФУНКТОРА
# ==============================================================================
class FinanceAnalytics:
    def __init__(self, base_fee: float):
        self.base_fee = base_fee
        self.calculations_made = 0
        self.total_analyzed_amount = 0.0

    def __call__(self, transaction: Transaction) -> float:
        self.calculations_made += 1
        self.total_analyzed_amount += transaction.amount
        
        # Розрахунок додаткової комісії в залежності від типу категорії
        multiplier = 1.5 if transaction.category == Category.ENTERTAINMENT else 1.0
        fee = (transaction.amount * 0.02 * multiplier) + self.base_fee
        return fee


# ==============================================================================
# 2. КЛАС КАСТОМНОГО ІТЄРАТОРА
# ==============================================================================
class ExpenseFilterIterator:
    def __init__(self, transactions: list):
        self.transactions = transactions
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self) -> Expense:
        while self.index < len(self.transactions):
            current_tx = self.transactions[self.index]
            self.index += 1
            if isinstance(current_tx, Expense):
                return current_tx
        raise StopIteration


# ==============================================================================
# 3. КЛАС-МЕНЕДЖЕР
# ==============================================================================
class Wallet:
    def __init__(self, initial_balance: float = 10000.0):
        self.balance = initial_balance
        self.transactions = []
        self.analyzer = FinanceAnalytics(base_fee=5.0)  # Композиція функтора

    def add_transaction(self, transaction: Transaction) -> None:
        if isinstance(transaction, Income):
            self.balance += transaction.amount
        elif isinstance(transaction, Expense):
            self.balance -= transaction.amount
        self.transactions.append(transaction)

    # Метод генератора для пагінації
    def generate_statement_pages(self, page_size: int):
        print(f"--- Генерація сторінками (по {page_size} транзакції) ---")
        for i in range(0, len(self.transactions), page_size):
            yield self.transactions[i:i + page_size]

    # Метод для отримання кастомного ітератора
    def get_expense_transactions(self) -> ExpenseFilterIterator:
        return ExpenseFilterIterator(self.transactions)


# ==============================================================================
# КОНТЕКСТНИЙ МЕНЕДЖЕР
# ==============================================================================
class FinancialSession:
    def __init__(self, wallet: Wallet, timeout_seconds: int = 2):
        self.wallet = wallet
        self.timeout_seconds = timeout_seconds
        self.status = "Active"
        self.start_time = None
        self._snapshot_balance = 0.0
        self._snapshot_transactions = []

    def __enter__(self):
        self._snapshot_balance = self.wallet.balance
        self._snapshot_transactions = self.wallet.transactions.copy()
        self.start_time = datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, traceback) -> bool:
        duration = (datetime.now() - self.start_time).total_seconds()
        if exc_type is not None:
            self.wallet.balance = self._snapshot_balance
            self.wallet.transactions = self._snapshot_transactions
            return True
        if duration > self.timeout_seconds:
            self.status = "Expired"
        return False


# ==============================================================================
# БЛОК ДЕМОНСТРАЦІЇ (ВИКОНАННЯ ЗАВДАНЬ ПО ПУНКТАХ)
# ==============================================================================
if __name__ == "__main__":
    # Базова підготовка даних для роботи менеджера
    manager = Wallet()
    tx1 = Expense(Category.FOOD, 250.0)
    tx2 = Income(Category.SALARY, 5000.0)
    tx3 = Expense(Category.TRANSPORT, 120.0)
    tx4 = Expense(Category.ENTERTAINMENT, 1500.0)
    tx5 = Expense(Category.FOOD, 300.0)

    manager.add_transaction(tx1)
    manager.add_transaction(tx2)
    manager.add_transaction(tx3)
    manager.add_transaction(tx4)
    manager.add_transaction(tx5)

    # --------------------------------------------------------------------------
    # a. Зміну стану функтора (вивід лічильника або історії після кількох викликів obj())
    # --------------------------------------------------------------------------
    print("--- Демонстрація Функтора ---")
    print(f"Складність для Обід: {manager.analyzer(tx1)}")
    print(f"Складність для Таксі: {manager.analyzer(tx3)}")
    print(f"Складність for Кіно: {manager.analyzer(tx4)}")
    print(f"Складність для Вечеря: {manager.analyzer(tx5)}")
    
    print(f"\n[СТАН ФУНКТОРА]: Проаналізовано завдань: {manager.analyzer.calculations_made}")
    print(f"[СТАН ФУНКТОРА]: Загальна розрахована складність: {manager.analyzer.total_analyzed_amount}")

    # --------------------------------------------------------------------------
    # b. Результат циклу for, який працює через ваш кастомний ітератор (фільтрація)
    # --------------------------------------------------------------------------
    print("\n--- Демонстрація Ітератора (лише Expense, за пріоритетом/типом) ---")
    for tx in manager.get_expense_transactions():
        print(tx)

    # --------------------------------------------------------------------------
    # c. Результат роботи генератора (покрокова видача даних через yield)
    # --------------------------------------------------------------------------
    print("\n--- Демонстрація Генератора (Пагінація) ---")
    page_number = 1
    for page in manager.generate_statement_pages(2):
        print(f"Сторінка {page_number}:")
        for tx in page:
            print(f"  - {tx}")
        page_number += 1