from repositories.data_repository import DataRepository
from models.expense import Expense


class ExpenseController:
    def __init__(self):
        self.repo = DataRepository()

    def get_expenses(self):
        return self.repo.load_expenses()
    
    def add_expense(self, expense: Expense):
        # Valida se o objeto Expense foi completamente preenchido
        if not expense.is_complete():
            raise ValueError("O objeto Expense não está completamente preenchido.")

        # Se estiver completo, salva no banco de dados
        return self.repo.save_expense(expense)

    # def add_expense(self, exp_date, exp_value, exp_description, exp_type_id, exp_pay_id, exp_number_of_installments):
    #     return self.repo.save_expense(exp_date, exp_value, exp_description, exp_type_id, exp_pay_id, exp_number_of_installments)

    # def update_expense(self, exp_id, exp_date, exp_value, exp_description, exp_type_id, exp_pay_id, exp_number_of_installments):
    #     return self.repo.update_expese(exp_id, exp_date, exp_value, exp_description, exp_type_id, exp_pay_id, exp_number_of_installments)

    # def delete_expense(self, exp_id):
    #     return self.repo.delete_expense(exp_id)
