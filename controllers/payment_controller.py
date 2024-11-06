from repositories.data_repository import DataRepository

class PaymentController:
    def __init__(self):
        self.repo = DataRepository()

    def get_payments(self):
        return self.repo.load_payments()

    def add_payment(self, pay_name, pay_description):
        return self.repo.save_payment(pay_name, pay_description)

    def update_payment(self, pay_id, new_name, new_description):
        return self.repo.update_payment(pay_id, new_name, new_description)

    def delete_payment(self, pay_id):
        return self.repo.delete_payment(pay_id)
