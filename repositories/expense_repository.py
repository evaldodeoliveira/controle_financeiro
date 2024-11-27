from data.database import get_connection
from models.expense import Expense
import pandas as pd
import streamlit as st

class ExpenseRepository:
    @staticmethod
    def load_expenses():
        try:
            conn = get_connection()
            
            query = """
                SELECT * FROM expense e
                JOIN type t ON e.exp_type_id = t.type_id
                JOIN payment p ON e.exp_pay_id = p.pay_id
                ORDER BY exp_date DESC;
                """
            payments_df = pd.read_sql_query(query, conn)
            
            conn.close()
            
            return payments_df
        except Exception as e:
            st.error(f"Ocorreu um erro ao ler os dados: \n\n{e}")
            return pd.DataFrame()

    @staticmethod
    def save_expense(expense: Expense):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                '''
                    INSERT INTO expense (
                        exp_date, 
                        exp_value, 
                        exp_description, 
                        exp_type_id, 
                        exp_pay_id, 
                        exp_number_of_installments, 
                        exp_final_date_of_installment,
                        exp_value_total_installment
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                ''', (
                        expense.exp_date,
                        float(expense.exp_value),
                        str(expense.exp_description),
                        int(expense.exp_type_id),
                        int(expense.exp_pay_id),
                        int(expense.exp_number_of_installments),
                        expense.exp_final_date_of_installment,
                        float(expense.exp_value_total_installments)
                )
            )
            
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Ocorreu um erro ao salvar o tipo: {e}")
            return False
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    @staticmethod
    def update_expense(expense: Expense):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                '''
                    UPDATE expense 
                    SET exp_date = ?, 
                        exp_value = ?, 
                        exp_description = ?, 
                        exp_type_id = ?, 
                        exp_pay_id = ?, 
                        exp_number_of_installments = ?, 
                        exp_final_date_of_installment = ?, 
                        exp_value_total_installment = ?
                    WHERE exp_id = ?;
                ''',(
                        expense.exp_date,
                        float(expense.exp_value),
                        str(expense.exp_description),
                        int(expense.exp_type_id),
                        int(expense.exp_pay_id),
                        int(expense.exp_number_of_installments),
                        expense.exp_final_date_of_installment,
                        float(expense.exp_value_total_installments),
                        int(expense.exp_id)
                )
            )
            
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Ocorreu um erro ao atualizar os dados: {e}")
            return False
        finally:
            if 'conn' in locals() and conn:
                conn.close()

    @staticmethod
    def delete_expense(exp_id):
        try:
            exp_id = int(exp_id)

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("PRAGMA foreign_keys = ON;")

            cursor.execute(
                '''
                DELETE FROM expense
                WHERE exp_id = ?; 
                ''', 
                (exp_id,)
            )
            
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado ao deletar: {e}")
            return False
        finally:
            if 'conn' in locals() and conn:
                conn.close()