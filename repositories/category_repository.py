from data.database import get_connection
import pandas as pd
import streamlit as st

class CategoryRepository:
    @staticmethod
    def load_categories():
        try:
            conn = get_connection()
            
            query = "SELECT * FROM category;"
            payments_df = pd.read_sql_query(query, conn)
            
            conn.close()
            
            return payments_df
        except Exception as e:
            st.error(f"Ocorreu um erro ao ler os dados: \n\n{e}")
            return pd.DataFrame()

    @staticmethod
    def save_category(cat_type, cat_name, cat_description):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                           INSERT INTO category (cat_type, cat_name, cat_description)
                           VALUES (?, ?, ?);
                           ''', 
                            (cat_type, cat_name, cat_description)
            )
            
            conn.commit()
            return True
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                st.error(f"Erro: A categoria '{cat_name}' já existe.")
            else:
                st.error(f"Ocorreu um erro ao salvar a categoria: {e}")
            return False
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    @staticmethod
    def update_category(category_id, new_name, new_description):
        try:
            category_id = int(category_id)

            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                '''
                UPDATE category SET cat_name = ?, cat_description = ?
                WHERE cat_id = ?;
                ''',
                (new_name, new_description, category_id)
            )
            
            conn.commit()
            return True
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                st.error(f"Erro: A categoria '{new_name}' já existe.")
            else:
                st.error(f"Ocorreu um erro ao atualizar os dados: {e}")
            return False
        finally:
            if 'conn' in locals() and conn:
                conn.close()

    @staticmethod
    def delete_category(category_id):
        try:
            category_id = int(category_id)

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("PRAGMA foreign_keys = ON;")

            cursor.execute(
                '''
                DELETE FROM category
                WHERE cat_id = ?; 
                ''', 
                (category_id,)
            )
            
            conn.commit()
            return True
        except conn.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                st.error(
                    f"Erro: Não é possível deletar a categoria com ID {category_id} "
                    "porque ela está associado a outros registros."
                )
            else:
                st.error(f"Erro de integridade: {e}")
            return False
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado ao deletar: {e}")
            return False
        finally:
            if 'conn' in locals() and conn:
                conn.close()