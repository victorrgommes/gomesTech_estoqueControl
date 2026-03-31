import sqlite3
import datetime
import pandas as pd # Necessário para os métodos de migração
import os # Necessário para os métodos de migração

class DatabaseManager:
    def __init__(self, db_file):
        self.db_file = db_file
        self.connection = None

    def connect(self):
        try:
            # SQLite conecta a um arquivo. Se não existir, ele será criado.
            self.connection = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            # Isso permite acessar as colunas pelo nome (como um dicionário)
            self.connection.row_factory = sqlite3.Row
            # Habilita o suporte a chaves estrangeiras, que é desabilitado por padrão no SQLite
            self.connection.execute("PRAGMA foreign_keys = ON")

            print(f"Conectado ao banco de dados SQLite: {self.db_file}")
            success, error_msg = self._create_tables_if_not_exist()
            if not success:
                return False, error_msg
            return True, None
        except sqlite3.Error as e:
            error_msg = f"Erro ao conectar ao SQLite: {e}"
            print(error_msg)
            self.connection = None
            return False, error_msg

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Conexão SQLite fechada.")
    
    def _check_connection(self):
        """Verifica se a conexão com o banco de dados está ativa."""
        if not self.connection:
            print("Erro: Conexão com o banco de dados não estabelecida ou perdida.")
            return False
        return True

    def _create_tables_if_not_exist(self):
        """Verifica e cria as tabelas do sistema se elas não existirem."""
        if not self._check_connection():
            return False, "Conexão com o banco de dados não estabelecida."
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conferentes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_datetime TIMESTAMP NOT NULL,
                    conferente_id INT NOT NULL,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL,
                    FOREIGN KEY (conferente_id) REFERENCES conferentes(id) ON DELETE RESTRICT ON UPDATE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT ON UPDATE CASCADE
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_settings (
                    setting_name TEXT PRIMARY KEY,
                    setting_value TEXT
                );
            """)
            self.connection.commit() # Commita as criações de tabela
            print("Tabelas do sistema verificadas/criadas com sucesso.")
            return True, None
        except sqlite3.Error as e:
            error_msg = f"Erro ao criar tabelas: {e}"
            print(error_msg)
            self.connection.rollback()
            return False, error_msg
        finally:
            cursor.close()

    def execute_query(self, query, params=None, fetch=False):
        if not self._check_connection():
            return False, "Conexão com o banco de dados perdida. Por favor, reinicie o aplicativo."

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            if fetch:
                result = cursor.fetchall()
                return True, result
            else:
                self.connection.commit()
                # Para INSERT, lastrowid indica se uma nova linha foi realmente inserida
                # (ou None se não, como em INSERT IGNORE para duplicatas).
                return True, (cursor.lastrowid if "INSERT" in query.upper() else None)
        except sqlite3.Error as e:
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> da84a72eaae0988189b64c5e29cde514102e92e5
            error_str = str(e)
            print(f"Erro ao executar query: {error_str}")
            self.connection.rollback()
            # Tenta traduzir erros comuns do SQLite para mensagens mais amigáveis
            if "UNIQUE constraint failed" in error_str:
                failed_field = error_str.split(': ')[-1]
                return False, f"O valor fornecido para o campo '{failed_field.split('.')[-1]}' já existe e deve ser único."
            if "FOREIGN KEY constraint failed" in error_str:
                return False, "A operação falhou porque o item está sendo usado em outro lugar (ex: em um registro de estoque)."
            if "NOT NULL constraint failed" in error_str:
                return False, f"Um campo obrigatório não foi preenchido: {error_str.split(': ')[-1]}."
            return False, error_str # Retorna o erro original se não for um dos casos conhecidos
<<<<<<< HEAD
=======
=======
            print(f"Erro ao executar query: {e}")
            self.connection.rollback()
            return False, str(e)
>>>>>>> bb3728385c64ebfc94f8708c835c62f5ee560ad8
>>>>>>> da84a72eaae0988189b64c5e29cde514102e92e5
        finally:
            cursor.close()

    # --- Métodos para Produtos ---
    def get_all_products(self):
        success, results = self.execute_query("SELECT name FROM products ORDER BY name", (), fetch=True)
        return [row['name'] for row in results] if success and results else []

    def add_product(self, product_name):
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> da84a72eaae0988189b64c5e29cde514102e92e5
        success, result = self.execute_query("INSERT INTO products (name) VALUES (?)", (product_name,))
        if success and result is not None:
            return True, None
        return False, result if not success else "O item não foi inserido."

    def update_product(self, old_name, new_name):
        return self.execute_query("UPDATE products SET name = ? WHERE name = ?", (new_name, old_name))

    def delete_product(self, product_name):
        return self.execute_query("DELETE FROM products WHERE name = ?", (product_name,))
<<<<<<< HEAD
=======
=======
        success, lastrowid = self.execute_query("INSERT INTO products (name) VALUES (?)", (product_name,))
        return success and lastrowid is not None # Retorna True apenas se a query for bem-sucedida E um novo ID foi gerado

    def update_product(self, old_name, new_name):
        success, _ = self.execute_query("UPDATE products SET name = ? WHERE name = ?", (new_name, old_name))
        return success

    def delete_product(self, product_name):
        success, _ = self.execute_query("DELETE FROM products WHERE name = ?", (product_name,))
        return success
>>>>>>> bb3728385c64ebfc94f8708c835c62f5ee560ad8
>>>>>>> da84a72eaae0988189b64c5e29cde514102e92e5

    def get_product_id(self, product_name):
        success, result = self.execute_query("SELECT id FROM products WHERE name = ?", (product_name,), fetch=True)
        return result[0]['id'] if success and result else None

    # --- Métodos para Conferentes ---
    def get_all_conferentes(self):
        success, results = self.execute_query("SELECT name FROM conferentes ORDER BY name", (), fetch=True)
        return [row['name'] for row in results] if success and results else []

    def add_conferente(self, conferente_name):
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> da84a72eaae0988189b64c5e29cde514102e92e5
        success, result = self.execute_query("INSERT INTO conferentes (name) VALUES (?)", (conferente_name,))
        if success and result is not None:
            return True, None
        return False, result if not success else "O item não foi inserido."

    def update_conferente(self, old_name, new_name):
        return self.execute_query("UPDATE conferentes SET name = ? WHERE name = ?", (new_name, old_name))

    def delete_conferente(self, conferente_name):
        return self.execute_query("DELETE FROM conferentes WHERE name = ?", (conferente_name,))
<<<<<<< HEAD
=======
=======
        success, lastrowid = self.execute_query("INSERT INTO conferentes (name) VALUES (?)", (conferente_name,))
        return success and lastrowid is not None

    def update_conferente(self, old_name, new_name):
        success, _ = self.execute_query("UPDATE conferentes SET name = ? WHERE name = ?", (new_name, old_name))
        return success

    def delete_conferente(self, conferente_name):
        success, _ = self.execute_query("DELETE FROM conferentes WHERE name = ?", (conferente_name,))
        return success
>>>>>>> bb3728385c64ebfc94f8708c835c62f5ee560ad8
>>>>>>> da84a72eaae0988189b64c5e29cde514102e92e5

    def get_conferente_id(self, conferente_name):
        success, result = self.execute_query("SELECT id FROM conferentes WHERE name = ?", (conferente_name,), fetch=True)
        return result[0]['id'] if success and result else None

    # --- Métodos para Entradas de Estoque ---
    def add_stock_entry(self, entry_datetime, conferente_name, product_name, quantity):
        conferente_id = self.get_conferente_id(conferente_name)
        product_id = self.get_product_id(product_name)

        if conferente_id is None:
            return False, f"Conferente '{conferente_name}' não encontrado no banco de dados."
        if product_id is None:
            return False, f"Produto '{product_name}' não encontrado no banco de dados."
        
        query = "INSERT INTO stock_entries (entry_datetime, conferente_id, product_id, quantity) VALUES (?, ?, ?, ?)"
        success, _ = self.execute_query(query, (entry_datetime, conferente_id, product_id, quantity))
        return success, None

    def add_multiple_stock_entries(self, entries):
        """Adiciona múltiplas entradas de estoque em uma única transação.
        'entries' é uma lista de dicionários, cada um com 'entry_datetime',
        'conferente_name', 'product_name', 'quantity'.
        """
        if not self._check_connection():
            return False, "Conexão com o banco de dados perdida. Por favor, reinicie o aplicativo."

        cursor = self.connection.cursor()
        try:
            query = "INSERT INTO stock_entries (entry_datetime, conferente_id, product_id, quantity) VALUES (?, ?, ?, ?)"

            for entry in entries:
                conferente_id = self.get_conferente_id(entry['conferente_name'])
                product_id = self.get_product_id(entry['product_name'])

                if conferente_id is None:
                    raise ValueError(f"Conferente '{entry['conferente_name']}' não encontrado.")
                if product_id is None:
                    raise ValueError(f"Produto '{entry['product_name']}' não encontrado.")

                params = (entry['entry_datetime'], conferente_id, product_id, entry['quantity'])
                cursor.execute(query, params)

            self.connection.commit()
            return True, None
        except (sqlite3.Error, ValueError) as e:
            error_msg = f"Erro ao adicionar múltiplas entradas de estoque: {e}"
            print(error_msg)
            self.connection.rollback()
            return False, str(e)
        finally:
            cursor.close()

    def upsert_multiple_stock_entries(self, entries):
        """
        Adiciona ou atualiza múltiplas entradas de estoque em uma única transação.
        Se já existir uma entrada para o mesmo conferente, produto e dia, atualiza a quantidade.
        Caso contrário, insere um novo registro.
        'entries' é uma lista de dicionários, cada um com 'entry_datetime',
        'conferente_name', 'product_name', 'quantity'.
        """
        if not self._check_connection():
            return False, "Conexão com o banco de dados perdida. Por favor, reinicie o aplicativo."

        cursor = self.connection.cursor()
        try:
            for entry in entries:
                conferente_id = self.get_conferente_id(entry['conferente_name'])
                product_id = self.get_product_id(entry['product_name'])
                entry_date = entry['entry_datetime'].date()

                if conferente_id is None:
                    raise ValueError(f"Conferente '{entry['conferente_name']}' não encontrado.")
                if product_id is None:
                    raise ValueError(f"Produto '{entry['product_name']}' não encontrado.")

                # Verifica se já existe um registro para o mesmo dia, conferente e produto
                find_query = "SELECT id FROM stock_entries WHERE conferente_id = ? AND product_id = ? AND DATE(entry_datetime) = ?"
                cursor.execute(find_query, (conferente_id, product_id, entry_date))
                existing_entry = cursor.fetchone()

                if existing_entry:
                    # Atualiza o registro existente
                    existing_entry_id = existing_entry[0]
                    update_query = "UPDATE stock_entries SET quantity = ?, entry_datetime = ? WHERE id = ?"
                    cursor.execute(update_query, (entry['quantity'], entry['entry_datetime'], existing_entry_id))
                else:
                    # Insere um novo registro
                    insert_query = "INSERT INTO stock_entries (entry_datetime, conferente_id, product_id, quantity) VALUES (?, ?, ?, ?)"
                    cursor.execute(insert_query, (entry['entry_datetime'], conferente_id, product_id, entry['quantity']))

            self.connection.commit()
            return True, None
        except (sqlite3.Error, ValueError) as e:
            error_msg = f"Erro ao adicionar/atualizar múltiplas entradas de estoque: {e}"
            print(error_msg)
            self.connection.rollback()
            return False, str(e)
        finally:
            cursor.close()

    def get_stock_entries(self, date_filter=None, conferente_filter=None, product_filter=None):
        query = """
            SELECT
                se.id,
                se.entry_datetime,
                c.name AS conferente_name,
                p.name AS product_name,
                se.quantity
            FROM
                stock_entries se
            JOIN
                conferentes c ON se.conferente_id = c.id
            JOIN
                products p ON se.product_id = p.id
            WHERE 1=1
        """
        params = []

        if date_filter:
            query += " AND DATE(se.entry_datetime) = ?"
            params.append(date_filter)
        if conferente_filter:
            query += " AND c.name LIKE ?"
            params.append(f"%{conferente_filter}%")
        if product_filter:
            query += " AND p.name LIKE ?"
            params.append(f"%{product_filter}%")
        
        query += " ORDER BY se.entry_datetime DESC"

        success, results = self.execute_query(query, tuple(params), fetch=True)
        return results if success else []

    def update_stock_entry_quantity(self, entry_id, new_quantity):
        """Atualiza a quantidade de uma entrada de estoque específica pelo seu ID."""
        query = "UPDATE stock_entries SET quantity = ? WHERE id = ?"
        success, result = self.execute_query(query, (new_quantity, entry_id))
        # result é a mensagem de erro em caso de falha, ou None em sucesso
        return success, result

    # --- Métodos para Configurações da Aplicação ---
    def get_setting(self, setting_name):
        query = "SELECT setting_value FROM app_settings WHERE setting_name = ?"
        success, result = self.execute_query(query, (setting_name,), fetch=True)
        return result[0]['setting_value'] if success and result else None

    def set_setting(self, setting_name, setting_value):
        query = """
            INSERT INTO app_settings (setting_name, setting_value) VALUES (?, ?)
            ON CONFLICT(setting_name) DO UPDATE SET setting_value = excluded.setting_value
        """
        success, _ = self.execute_query(query, (setting_name, setting_value))
        return success

    # --- Métodos de Configuração Específicos ---
    def get_last_used_conferente(self):
        """Recupera o nome do último conferente usado."""
        return self.get_setting('last_used_conferente')

    def set_last_used_conferente(self, conferente_name):
        """Salva o nome do último conferente usado."""
        return self.set_setting('last_used_conferente', conferente_name)

    def is_default_data_initialized(self):
        """Verifica se os dados padrão já foram inicializados."""
        return self.get_setting('default_data_initialized') == 'true'

    def mark_default_data_as_initialized(self):
        """Marca no banco de dados que os dados padrão foram inicializados."""
        print("Flag 'default_data_initialized' definido como 'true'.")
        return self.set_setting('default_data_initialized', 'true')

    def initialize_default_data(self):
        """Adiciona produtos e conferentes padrão apenas uma única vez, na primeira execução do programa com um DB 'novo'."""
        # Verifica se o flag de inicialização já foi setado
        if self.is_default_data_initialized():
            # print("Dados padrão já inicializados. Ignorando.") # Para debug, se necessário
            return
        print("Primeira execução detectada. Inicializando dados padrão...")

        # Adiciona produtos padrão
        default_products = ['Teclado Mecanico', 'Mouse Optico', 'Monitor 24pol', 'Cabo HDMI 2m', 'Switch 8 Portas']
        for product_name in default_products:
<<<<<<< HEAD
            success, _ = self.add_product(product_name)
=======
<<<<<<< HEAD
            success, _ = self.add_product(product_name)
=======
            success = self.add_product(product_name)
>>>>>>> bb3728385c64ebfc94f8708c835c62f5ee560ad8
>>>>>>> da84a72eaae0988189b64c5e29cde514102e92e5
            if success:
                print(f"Adicionado produto padrão: {product_name}")

        # Adiciona conferente padrão
        default_conferentes = ['Admin']
        for conferente_name in default_conferentes:
<<<<<<< HEAD
            success, _ = self.add_conferente(conferente_name)
=======
<<<<<<< HEAD
            success, _ = self.add_conferente(conferente_name)
=======
            success = self.add_conferente(conferente_name)
>>>>>>> bb3728385c64ebfc94f8708c835c62f5ee560ad8
>>>>>>> da84a72eaae0988189b64c5e29cde514102e92e5
            if success:
                print(f"Adicionado conferente padrão: {conferente_name}")

        # Marca que os dados padrão foram inicializados para não rodar novamente
        self.mark_default_data_as_initialized()

    # --- Métodos de Migração (Opcional, para usar uma vez) ---
    # Estes métodos são para migrar dados de arquivos antigos para o banco de dados.
    def migrate_products_from_csv(self, csv_path):
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path, encoding='utf-8')
            for product_name in df['Produto'].unique():
                self.add_product(product_name)
            print(f"Produtos migrados de {csv_path}")

    def migrate_conferentes_from_csv(self, csv_path):
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path, encoding='utf-8')
            for conferente_name in df['Conferente'].unique():
                self.add_conferente(conferente_name)
            print(f"Conferentes migrados de {csv_path}")

    def migrate_stock_entries_from_excel(self, excel_path):
        if os.path.exists(excel_path):
            df = pd.read_excel(excel_path)
            for index, row in df.iterrows(): # pandas.DataFrame.iterrows()
                entry_datetime = pd.to_datetime(row['Data/Hora'], format='%d/%m/%Y %H:%M:%S') # pandas.to_datetime
                conferente_name = row['Conferente']
                product_name = row['Produto']
                quantity = row['Quantidade']
                self.add_stock_entry(entry_datetime, conferente_name, product_name, quantity)
            print(f"Entradas de estoque migradas de {excel_path}")
            