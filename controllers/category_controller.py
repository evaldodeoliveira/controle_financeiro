from repositories.data_repository import DataRepository

class CategoryController:
    def __init__(self):
        self.repo = DataRepository()

    def get_categories(self):
        return self.repo.load_categories()

    def add_category(self, cat_type, cat_name, cat_description):
        return self.repo.save_category(cat_type, cat_name, cat_description)

    def update_category(self, category_id, cat_type, new_name, new_description):
        return self.repo.update_category(category_id, cat_type, new_name, new_description)

    def delete_category(self, category_id):
        return self.repo.delete_category(category_id)
