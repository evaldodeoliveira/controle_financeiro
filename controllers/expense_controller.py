#from repositories.data_repository import DataRepository
from repositories.expense_repository import ExpenseRepository
from models.expense import Expense


class ExpenseController:
    def __init__(self):
        #self.repo = DataRepository()
        self.repo = ExpenseRepository()

    def get_expenses(self):
        return self.repo.load_expenses()
    
    def add_expense(self, expense: Expense):
        # Valida se o objeto Expense foi completamente preenchido
        if not expense.is_complete():
            raise ValueError("O objeto Expense não está completamente preenchido.")
        # Se estiver completo, salva no banco de dados
        return self.repo.save_expense(expense)

    def update_expense(self, expense: Expense):
        if not expense.is_complete():
            raise ValueError("O objeto Expense não está completamente preenchido.")
        return self.repo.update_expense(expense)

    def delete_expense(self, exp_id):
        return self.repo.delete_expense(exp_id)
