class Payment:
    def __init__(self, pay_id: int, pay_name: str, pay_description: str):
        self.pay_id = pay_id
        self.pay_name = pay_name
        self.pay_description = pay_description

    def __repr__(self):
        return f"Payment(id={self.pay_id}, name='{self.pay_name}', description='{self.pay_description}')"
