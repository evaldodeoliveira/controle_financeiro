# class Category:
#     def __init__(self, id: int, name: str, description: str):
#         self.id = id
#         self.name = name
#         self.description = description

class Category:
    def __init__(self, cat_id: int, cat_type: str, cat_name: str, cat_description: str):
        self.cat_id = cat_id
        self.cat_type = cat_type  # deve ser 'expense', 'income', ou 'investment'
        self.cat_name = cat_name
        self.cat_description = cat_description

    def __repr__(self):
        return f"Category(id={self.cat_id}, type='{self.cat_type}', name='{self.cat_name}', description='{self.cat_description}')"