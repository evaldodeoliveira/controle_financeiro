from data.database import get_connection
import pandas as pd
import streamlit as st

class PaymentRepository:
    @staticmethod
    def load_payments():
        """Carrega os pagamentos do banco de dados como DataFrame."""
        try:
            # Obter conexão do banco de dados
            conn = get_connection()
            
            # Executar a consulta SQL
            query = "SELECT * FROM payment;"
            payments_df = pd.read_sql_query(query, conn)
            
            # Fechar a conexão
            conn.close()
            
            return payments_df
        except Exception as e:
            # Exibir mensagem de erro no Streamlit em caso de falha
            st.error(f"Ocorreu um erro ao ler os dados: \n\n{e}")
            return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro

    @staticmethod
    def save_payment(pay_name, pay_description):
        """Adiciona um novo pagamento ao banco de dados."""
        try:
            # Obter conexão com o banco de dados
            conn = get_connection()
            cursor = conn.cursor()
            
            # Executar a inserção
            cursor.execute(
                '''
                INSERT INTO payment (pay_name, pay_description) 
                VALUES (?, ?);
                ''', 
                (pay_name, pay_description)
            )
            
            # Confirmar a transação
            conn.commit()
            return True  # Indica sucesso
        except Exception as e:
            # Verificar se o erro é de restrição UNIQUE
            if "UNIQUE constraint failed" in str(e):
                st.error(f"Erro: O pagamento '{pay_name}' já existe.")
            else:
                st.error(f"Ocorreu um erro ao salvar o pagamento: {e}")
            return False  # Indica erro
        finally:
            # Garantir que a conexão será fechada
            if 'conn' in locals() and conn:
                conn.close()

    @staticmethod
    def update_payment(pay_id, new_name, new_description):
        """
        Atualiza um pagamento no banco de dados.
        """
        try:
            # Converter o ID para inteiro (por segurança)
            pay_id = int(pay_id)
            
            # Obter conexão com o banco de dados
            conn = get_connection()
            cursor = conn.cursor()
            
            # Executar a atualização
            cursor.execute(
                '''
                UPDATE payment 
                SET pay_name = ?, pay_description = ? 
                WHERE pay_id = ?;
                ''',
                (new_name, new_description, pay_id)
            )
            
            # Confirmar a transação
            conn.commit()
            return True  # Indica sucesso
        except Exception as e:
            # Verificar se o erro é de restrição UNIQUE
            if "UNIQUE constraint failed" in str(e):
                st.error(f"Erro: O pagamento '{new_name}' já existe.")
            else:
                st.error(f"Ocorreu um erro ao atualizar os dados: {e}")
            return False  # Indica erro
        finally:
            # Garantir que a conexão será fechada
            if 'conn' in locals() and conn:
                conn.close()

    @staticmethod
    def delete_payment(pay_id):
        """
        Deleta um pagamento do banco de dados.
        """
        try:
            # Converter o ID para inteiro (por segurança)
            pay_id = int(pay_id)

            # Obter conexão com o banco de dados
            conn = get_connection()
            cursor = conn.cursor()

            # Habilitar chaves estrangeiras, se necessário
            cursor.execute("PRAGMA foreign_keys = ON;")

            # Executar o comando de exclusão
            cursor.execute(
                '''
                DELETE FROM payment 
                WHERE pay_id = ?;
                ''', 
                (pay_id,)
            )
            
            # Confirmar a transação
            conn.commit()
            return True  # Indica sucesso
        except conn.IntegrityError as e:
            # Verifica se o erro é relacionado a falha em chave estrangeira
            if "FOREIGN KEY constraint failed" in str(e):
                st.error(
                    f"Erro: Não é possível deletar o pagamento com ID {pay_id} "
                    "porque ele está associado a outros registros."
                )
            else:
                # Para outros tipos de erro de integridade
                st.error(f"Erro de integridade: {e}")
            return False  # Indica erro relacionado à integridade
        except Exception as e:
            # Captura qualquer erro inesperado (não relacionado à integridade)
            st.error(f"Ocorreu um erro inesperado ao deletar: {e}")
            return False  # Indica erro genérico
        finally:
            # Garantir que a conexão será fechada
            if 'conn' in locals() and conn:
                conn.close()