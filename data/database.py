import sqlite3

#passar data_repository pra c'ou este def pra lá
# tem que entender porque o data_repository e executado ao iniciar o programa

def get_connection():
    return sqlite3.connect('./data/financial_control.db')