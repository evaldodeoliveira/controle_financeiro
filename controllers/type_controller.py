from repositories.data_repository import DataRepository

class TypeController:
    def __init__(self):
        self.repo = DataRepository()

    def get_types(self):
        return self.repo.load_types()

    def add_type(self, type_type, type_name, type_description, type_cat_id):
        return self.repo.save_type(type_type, type_name, type_description, type_cat_id)

    def update_type(self, type_id, type_type, new_name, new_description, type_cat_id):
        return self.repo.update_type(type_id, type_type, new_name, new_description, type_cat_id),

    def delete_type(self, type_id):
        return self.repo.delete_type(type_id)
