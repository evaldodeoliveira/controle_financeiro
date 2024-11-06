# 
class Expense:
    def __init__(self, exp_id: int = None, exp_date: str = None, exp_value: float = None, exp_description: str = None,
                 exp_type_id: int = None, exp_pay_id: int = None, exp_number_of_installments: int = 0,
                 exp_installment_value: float = 0.0):
        self.exp_id = exp_id
        self.exp_date = exp_date
        self.exp_value = exp_value
        self.exp_description = exp_description
        self.exp_type_id = exp_type_id
        self.exp_pay_id = exp_pay_id
        self.exp_number_of_installments = exp_number_of_installments
        self.exp_installment_value = exp_installment_value

    def __repr__(self):
        return (f"Expense(id={self.exp_id}, date='{self.exp_date}', value={self.exp_value}, "
                f"description='{self.exp_description}', type_id={self.exp_type_id}, "
                f"pay_id={self.exp_pay_id}, number_of_installments={self.exp_number_of_installments}, "
                f"installment_value={self.exp_installment_value})")

    def is_complete(self):
        # Verifica se os atributos obrigatórios estão preenchidos
        required_attributes = [
            self.exp_date, self.exp_value, self.exp_description,
            self.exp_type_id, self.exp_pay_id
        ]
        return all(attr is not None for attr in required_attributes)
