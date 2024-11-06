# class Type:
#     def __init__(self, id: int, name: str, description: str):
#         self.id = id
#         self.name = name
#         self.description = description

class Type:
    def __init__(self, type_id: int, type_type: str, type_name: str, type_description: str, type_category_id: int):
        self.type_id = type_id
        self.type_type = type_type  # deve ser 'expense', 'income', ou 'investment'
        self.type_name = type_name
        self.type_description = type_description
        self.type_category_id = type_category_id  # Referência à categoria

    def __repr__(self):
        return (f"Type(id={self.type_id}, type='{self.type_type}', name='{self.type_name}', "
                f"description='{self.type_description}', category_id={self.type_category_id})")
