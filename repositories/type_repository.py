from data.database import get_connection
import pandas as pd
import streamlit as st

class TypeRepository:
    @staticmethod
    def load_types():
        try:
            conn = get_connection()
            
            query = """
                SELECT * FROM type t
                JOIN category c ON t.type_category_id = c.cat_id;
                """
            payments_df = pd.read_sql_query(query, conn)
            
            conn.close()
            
            return payments_df
        except Exception as e:
            st.error(f"Ocorreu um erro ao ler os dados: \n\n{e}")
            return pd.DataFrame()

    @staticmethod
    def save_type(type_type, type_name, type_description, type_category_id):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                            INSERT INTO type (type_type, type_name, type_description, type_category_id)
                           VALUES (?, ?, ?, ?);
                           ''',
                           (type_type, type_name, type_description, type_category_id)
            )
            
            conn.commit()
            return True
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                st.error(f"Erro: O tipo '{type_name}' já existe.")
            else:
                st.error(f"Ocorreu um erro ao salvar o tipo: {e}")
            return False
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    @staticmethod
    def update_type(type_id, type_type, new_name, new_description, type_category_id):
        try:
            type_id = int(type_id)
            type_category_id = int(type_category_id)
            
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                '''
                UPDATE type SET type_type = ?, type_name = ?, type_description = ?, type_category_id = ?
                WHERE type_id = ?;
                ''',
                (type_type, new_name, new_description, type_category_id, type_id)
            )
            
            conn.commit()
            return True
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                st.error(f"Erro: O tipo '{new_name}' já existe.")
            else:
                st.error(f"Ocorreu um erro ao atualizar os dados: {e}")
            return False
        finally:
            if 'conn' in locals() and conn:
                conn.close()

    @staticmethod
    def delete_type(type_id):
        try:
            type_id = int(type_id)

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("PRAGMA foreign_keys = ON;")

            cursor.execute(
                '''
                DELETE FROM type
                WHERE type_id = ?; 
                ''', 
                (type_id,)
            )
            
            conn.commit()
            return True
        except conn.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                st.error(
                    f"Erro: Não é possível deletar o tipo com ID {type_id} "
                    "porque ele está associado a outros registros."
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