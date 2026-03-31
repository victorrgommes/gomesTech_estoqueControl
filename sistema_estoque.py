import customtkinter as ctk
import pandas as pd
import os
import datetime
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox
from CTkTable import CTkTable
from database_manager import DatabaseManager
from export_manager import ExportManager

# --- Classes de Janelas Secundárias ---

class SearchWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Consultar Histórico de Conferência")
        self.geometry("800x600")
        self.transient(master)
        self.last_search_results = []

        # --- Frame de Busca ---
        search_frame = ctk.CTkFrame(self)
        search_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

        conferentes, produtos = self.load_filter_options()

        ctk.CTkLabel(search_frame, text="Data (dd/mm/aaaa):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = ctk.CTkEntry(search_frame, placeholder_text="Opcional")
        self.date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(search_frame, text="Conferente:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.conferente_entry = ctk.CTkComboBox(search_frame, values=conferentes)
        self.conferente_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.conferente_entry.set("")

        ctk.CTkLabel(search_frame, text="Produto:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.produto_entry = ctk.CTkComboBox(search_frame, values=produtos)
        self.produto_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.produto_entry.set("")

        search_frame.grid_columnconfigure(1, weight=1)
        
        search_button = ctk.CTkButton(search_frame, text="Buscar", command=self.perform_search)
        search_button.grid(row=3, column=0, padx=5, pady=10, sticky="ew")

        export_button = ctk.CTkButton(search_frame, text="Exportar para Planilha", command=self.export_filtered_data)
        export_button.grid(row=3, column=1, padx=5, pady=10, sticky="ew")

        self.edit_button = ctk.CTkButton(search_frame, text="Editar Quantidade", command=self.edit_quantity, state="disabled")
        self.edit_button.grid(row=4, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

        self.date_entry.bind("<Return>", lambda event: self.perform_search())
        self.conferente_entry.bind("<Return>", lambda event: self.perform_search())
        self.produto_entry.bind("<Return>", lambda event: self.perform_search())

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        results_frame = ctk.CTkFrame(self)
        results_frame.grid(row=1, column=0, pady=(0, 10), padx=10, sticky="nsew")
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        self.table_frame = ctk.CTkScrollableFrame(results_frame)
        self.table_frame.grid(row=0, column=0, sticky="nsew")

        self.table_values = [["ID", "Data/Hora", "Conferente", "Produto", "Quantidade"]]
        self.table = CTkTable(master=self.table_frame, values=self.table_values, command=self.on_table_click)
        self.table.pack(expand=True, fill="both")
        self.selected_row = None

    def _clear_search_results(self):
        """Limpa os resultados da Tabela e desabilita o botão de edição."""
        self.table_values = [["ID", "Data/Hora", "Conferente", "Produto", "Quantidade"]]
        self.table.update_values(self.table_values)
        self.edit_button.configure(state="disabled")
        self.last_search_results = []
        self.selected_row = None
    def load_filter_options(self):
        db_manager = self.master.db_manager
        conferentes = [""] + sorted(db_manager.get_all_conferentes())
        produtos = [""] + sorted(db_manager.get_all_products())
        return conferentes, produtos

    def refresh_filter_options(self):
        """Recarrega e atualiza as opções dos comboboxes de filtro."""
        conferentes, produtos = self.load_filter_options()
        current_conferente = self.conferente_entry.get()
        current_produto = self.produto_entry.get()
        self.conferente_entry.configure(values=conferentes)
        self.produto_entry.configure(values=produtos)
        # Tenta manter a seleção atual se ainda for válida
        if current_conferente in conferentes:
            self.conferente_entry.set(current_conferente)

    def perform_search(self):
        date_str = self.date_entry.get().strip()
        conferente_str = self.conferente_entry.get().strip()
        produto_str = self.produto_entry.get().strip()
        
        db_manager = self.master.db_manager

        self._clear_search_results()

        try:
            search_date_obj = None
            if date_str:
                try:
                    search_date_obj = datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
                except ValueError:
                    CTkMessagebox(title="Formato Inválido", message="Por favor, insira a data no formato dd/mm/aaaa.", icon="warning")
                    return
            
            results = db_manager.get_stock_entries(
                date_filter=search_date_obj,
                conferente_filter=conferente_str,
                product_filter=produto_str
            )

            if not results:
                self.last_search_results = []
                CTkMessagebox(title="Nenhum Resultado", message="Nenhum registro encontrado com os filtros aplicados.", icon="info")
                return
            
            for row in results:
                dt_str = row['entry_datetime'].strftime('%d/%m/%Y %H:%M:%S')
                self.table_values.append([row['id'], dt_str, row['conferente_name'], row['product_name'], str(row['quantity'])])
            self.table.update_values(self.table_values)
            self.last_search_results = results

        except Exception as e:
            CTkMessagebox(title="Erro ao Consultar", message=f"Ocorreu um erro ao consultar o histórico:\n{e}", icon="error")

    def on_table_click(self, cell):
        if cell["row"] > 0: # Ignorar cabeçalho
            self.selected_row = cell["row"]
            self.edit_button.configure(state="normal")
        else:
            self.selected_row = None
            self.edit_button.configure(state="disabled")

    def edit_quantity(self):
        if not self.selected_row:
            return
        
        item_values = self.table_values[self.selected_row]
        entry_id_str, timestamp_str, conferente, produto, old_quantity = item_values

        dialog = ctk.CTkInputDialog(text=f"Produto: {produto}\nConferente: {conferente}\n\nDigite a nova quantidade (atual: {old_quantity}):", title="Editar Quantidade")
        new_quantity_str = dialog.get_input()

        if new_quantity_str is None: # Usuário cancelou a entrada
            return
        
        if not new_quantity_str.strip().isdigit():
            CTkMessagebox(title="Entrada Inválida", message="Por favor, insira apenas números inteiros para a quantidade.", icon="warning")
            return
        if int(new_quantity_str.strip()) < 0:
            CTkMessagebox(title="Entrada Inválida", message="A quantidade não pode ser negativa.", icon="warning")
            return
        new_quantity = int(new_quantity_str)

        success, error_message = self.master.db_manager.update_stock_entry_quantity(int(entry_id_str), new_quantity)
        if not success:
            CTkMessagebox(title="Erro de Atualização", message=f"Não foi possível atualizar a quantidade no banco de dados:\n{error_message}", icon="error")
            return

        self.table_values[self.selected_row] = [entry_id_str, timestamp_str, conferente, produto, str(new_quantity)]
        self.table.update_values(self.table_values)
        CTkMessagebox(title="Sucesso", message="A quantidade foi atualizada com sucesso.", icon="check")

    def export_filtered_data(self):
        if not self.last_search_results:
            CTkMessagebox(title="Exportar Dados", message="Não há dados para exportar. Realize uma busca primeiro.", icon="warning")
            return

        df = pd.DataFrame([dict(row) for row in self.last_search_results])
        
        df.rename(columns={
            'entry_datetime': 'Data/Hora',
            'conferente_name': 'Conferente',
            'product_name': 'Produto',
            'quantity': 'Quantidade'
        }, inplace=True)

        df['Data/Hora'] = df['Data/Hora'].dt.strftime('%d/%m/%Y %H:%M:%S')

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Salvar Histórico de Estoque"
        )

        if file_path:
            try:
                # Usar o gerenciador MVC criado
                ExportManager.export_to_excel(df, file_path)
                CTkMessagebox(title="Exportação Concluída", message=f"Dados exportados com sucesso para:\n{file_path}", icon="check")
            except Exception as e:
                CTkMessagebox(title="Erro de Exportação", message=f"Ocorreu um erro ao exportar para Excel:\n{e}", icon="error")


class BaseManagerWindow(ctk.CTkToplevel):
    def __init__(self, master, title, item_name_singular, item_name_plural,
                 get_all_func, add_func, update_func, delete_func, refresh_master_func):
        super().__init__(master)
        self.master = master
        self.title(title)
        self.geometry("500x500")
        self.transient(master)
        self.grab_set()

        self.item_name_singular = item_name_singular
        self.item_name_plural = item_name_plural
        self.get_all_func = get_all_func
        self.add_func = add_func
        self.update_func = update_func
        self.delete_func = delete_func
        self.refresh_master_func = refresh_master_func # Callback para atualizar a UI da janela principal

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._create_add_frame()
        self._create_scrollable_frame()
        self.load_and_display_items()

    def _create_add_frame(self):
        add_frame = ctk.CTkFrame(self)
        add_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        add_frame.grid_columnconfigure(0, weight=1)

        self.new_item_entry = ctk.CTkEntry(add_frame, placeholder_text=f"Digite o nome do {self.item_name_singular} para adicionar")
        self.new_item_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.new_item_entry.bind("<Return>", lambda event: self.add_item())

        add_button = ctk.CTkButton(add_frame, text="Adicionar", width=80, command=self.add_item)
        add_button.grid(row=0, column=1, padx=5, pady=5)

    def _create_scrollable_frame(self):
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text=f"{self.item_name_plural} Cadastrados")
        self.scrollable_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    def load_and_display_items(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        items = self.get_all_func()
        for name in items:
            row_frame = ctk.CTkFrame(self.scrollable_frame)
            row_frame.pack(fill="x", pady=2, padx=2)

            label = ctk.CTkLabel(row_frame, text=name, anchor="w")
            label.pack(side="left", fill="x", expand=True, padx=10)

            edit_button = ctk.CTkButton(row_frame, text="Editar", width=70, command=lambda n=name: self.edit_item(n))
            edit_button.pack(side="right", padx=(0, 5))

            delete_button = ctk.CTkButton(row_frame, text="Excluir", width=70, fg_color="red", hover_color="#C00000", command=lambda n=name: self.delete_item(n))
            delete_button.pack(side="right")

    def add_item(self):
        new_name = self.new_item_entry.get().strip()
        if not new_name: return
        
        if new_name in self.get_all_func():
            CTkMessagebox(title="Duplicado", message=f"O {self.item_name_singular} '{new_name}' já existe.", icon="warning")
            return
        
        success, error_message = self.add_func(new_name)
        if success:
            self.master.update_status(f"{self.item_name_singular.capitalize()} '{new_name}' adicionado com sucesso.")
        else:
            CTkMessagebox(title="Erro ao Adicionar", message=f"Não foi possível adicionar o {self.item_name_singular}.\n\nMotivo: {error_message}", icon="error")
        self.load_and_display_items()
        self.refresh_master_func()
        self.new_item_entry.delete(0, 'end')

    def edit_item(self, old_name):
        dialog = ctk.CTkInputDialog(text=f"Editando '{old_name}'.\nDigite o novo nome:", title=f"Editar {self.item_name_singular.capitalize()}")
        new_name_input = dialog.get_input()
        if not new_name_input or not new_name_input.strip() or new_name_input.strip() == old_name: return
        clean_new_name = new_name_input.strip() # Garante que o novo nome não é apenas espaços em branco
        if clean_new_name in self.get_all_func():
            CTkMessagebox(title="Duplicado", message=f"O nome '{clean_new_name}' já existe.", icon="warning")
            return
        success, error_message = self.update_func(old_name, clean_new_name)
        if not success:
            CTkMessagebox(title="Erro ao Atualizar", message=f"Não foi possível atualizar o {self.item_name_singular}.\n\nMotivo: {error_message}", icon="error")
            return
        self.load_and_display_items()
        self.refresh_master_func()
        self.master.update_status(f"{self.item_name_singular.capitalize()} '{old_name}' atualizado para '{clean_new_name}'.")

    def delete_item(self, name_to_delete):
        msg = CTkMessagebox(title="Confirmar Exclusão", message=f"Tem certeza que deseja excluir o {self.item_name_singular} '{name_to_delete}'?", icon="question", option_1="Não", option_2="Sim")
        if msg.get() == "Sim":
            success, error_message = self.delete_func(name_to_delete)
            if success:
                self.master.update_status(f"{self.item_name_singular.capitalize()} '{name_to_delete}' concluído com sucesso.")
            else:
                CTkMessagebox(title="Erro ao Excluir", message=f"Não foi possível excluir o {self.item_name_singular} '{name_to_delete}'.\n\nMotivo: {error_message}", icon="error")
            self.load_and_display_items()
            self.refresh_master_func()


class ConferenteManagerWindow(BaseManagerWindow):
    def __init__(self, master):
        super().__init__(
            master,
            title="Gerenciar Conferentes",
            item_name_singular="conferente",
            item_name_plural="Conferentes",
            get_all_func=master.db_manager.get_all_conferentes,
            add_func=master.db_manager.add_conferente,
            update_func=master.db_manager.update_conferente,
            delete_func=master.db_manager.delete_conferente,
            refresh_master_func=master.refresh_conferente_combobox
        )


class ProductManagerWindow(BaseManagerWindow):
    def __init__(self, master):
        super().__init__(
            master,
            title="Gerenciar Produtos",
            item_name_singular="produto",
            item_name_plural="Produtos",
            get_all_func=master.db_manager.get_all_products,
            add_func=master.db_manager.add_product,
            update_func=master.db_manager.update_product,
            delete_func=master.db_manager.delete_product,
            refresh_master_func=master.refresh_product_list
        )


# --- Classe Principal da Aplicação ---

class InventoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.product_widgets = {}

        # --- Configuração da Janela Principal ---
        self.title("GomesTech - Controle de Estoque")
        self.geometry("600x700")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Configuração do Banco de Dados ---
        # Com SQLite, o banco de dados é um único arquivo. Não precisa de host, usuário ou senha.
        self.db_manager = DatabaseManager(db_file="estoque.db")
        
        # Tenta conectar e lida com falha na inicialização
        success, error_message = self.db_manager.connect()
        if not success:
            self.withdraw() # Esconde a janela principal antes de mostrar o erro
            CTkMessagebox(title="Erro Crítico de Banco de Dados", message=f"Não foi possível iniciar o banco de dados.\n\nArquivo: estoque.db\nErro: {error_message}\n\nO aplicativo será encerrado.", icon="error")
            self.after(100, self.destroy) # Fecha o app após mostrar a msg
            return
        
        # Adiciona dados padrão se o banco de dados estiver "novo"
        self.db_manager.initialize_default_data()

        # --- Construção da UI ---
        self.build_ui()
        self._load_last_conferente()

    def build_ui(self):
        """Constrói a interface do usuário."""
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        main_frame.grid_rowconfigure(3, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # MINI-DASHBOARD
        dash_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        dash_frame.grid(row=0, column=0, pady=5, padx=10, sticky="ew")
        dash_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.dash_total_lbl = ctk.CTkLabel(dash_frame, text="Produtos Cadastrados: -", font=("Arial", 14, "bold"))
        self.dash_total_lbl.grid(row=0, column=0, sticky="w")
        self.dash_conferentes_lbl = ctk.CTkLabel(dash_frame, text="Conferentes: -", font=("Arial", 14, "bold"))
        self.dash_conferentes_lbl.grid(row=0, column=1, sticky="w")
        self._update_dashboard()

        header_frame = ctk.CTkFrame(main_frame)
        header_frame.grid(row=1, column=0, pady=10, padx=10, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(header_frame, text="Nome do Conferente:", font=("Arial", 14)).grid(row=0, column=0, padx=(10, 5), pady=5)
        conferentes = self.db_manager.get_all_conferentes()
        self.conferente_entry = ctk.CTkComboBox(header_frame, values=conferentes, width=300)
        self.conferente_entry.grid(row=0, column=1, padx=(0, 10), pady=5, sticky="ew")
        self.conferente_entry.set("")

        # SEARCH BAR
        search_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        search_frame.grid(row=2, column=0, pady=5, padx=10, sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(search_frame, text="Buscar Produto:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.search_product_var = ctk.StringVar()
        self.search_product_var.trace_add("write", self.filter_products)
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_product_var, placeholder_text="Digite o nome...")
        search_entry.grid(row=0, column=1, sticky="ew")

        self.scrollable_frame = ctk.CTkScrollableFrame(main_frame, label_text="Lista de Produtos")
        self.scrollable_frame.grid(row=3, column=0, pady=10, padx=10, sticky="nsew")

        self.load_and_display_products()

        manage_frame = ctk.CTkFrame(main_frame)
        manage_frame.grid(row=4, column=0, pady=5, padx=10, sticky="ew")
        manage_frame.grid_columnconfigure((0, 1, 2), weight=1)

        manage_product_button = ctk.CTkButton(manage_frame, text="Gerenciar Produtos", command=self.open_product_manager)
        manage_product_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        manage_conferente_button = ctk.CTkButton(manage_frame, text="Gerenciar Conferentes", command=self.open_conferente_manager)
        manage_conferente_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        search_button = ctk.CTkButton(manage_frame, text="Consultar Histórico", command=self.open_search_window)
        search_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.overwrite_checkbox = ctk.CTkCheckBox(main_frame, text="Sobrescrever contagens existentes no mesmo dia")
        self.overwrite_checkbox.grid(row=5, column=0, pady=(10, 0), padx=10, sticky="w")

        self.export_button = ctk.CTkButton(main_frame, text="Salvar Conferência", command=self.finish_and_export, height=40, font=("Arial", 16, "bold"))
        self.export_button.grid(row=6, column=0, pady=15, padx=10, sticky="ew")

        self.status_label = ctk.CTkLabel(self, text="Pronto", anchor="w", font=("Arial", 12))
        self.status_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _load_last_conferente(self):
        """Carrega o último conferente usado a partir das configurações do banco de dados."""
        last_conferente = self.db_manager.get_last_used_conferente()
        if last_conferente:
            # Verifica se o conferente ainda existe na lista antes de setar
            if last_conferente in self.conferente_entry.cget('values'):
                self.conferente_entry.set(last_conferente)

    def on_closing(self):
        self.db_manager.disconnect()
        self.destroy()

    def load_and_display_products(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.product_widgets = {}

        products = self.db_manager.get_all_products()
        self.all_products = products # Para filtrar
        
        for product_name in products:
            self.create_product_entry_widget(product_name)
        
        self._update_dashboard()

    def _update_dashboard(self):
        try:
            total_prod = len(self.db_manager.get_all_products())
            total_conf = len(self.db_manager.get_all_conferentes())
            if hasattr(self, 'dash_total_lbl'):
                self.dash_total_lbl.configure(text=f"Produtos Cadastrados: {total_prod}")
                self.dash_conferentes_lbl.configure(text=f"Conferentes: {total_conf}")
        except:
            pass

    def filter_products(self, *args):
        search_text = self.search_product_var.get().lower()
        for product_name, widgets in self.product_widgets.items():
            if search_text in product_name.lower():
                widgets['frame'].pack(fill="x", pady=2, padx=5)
            else:
                widgets['frame'].pack_forget()

    def create_product_entry_widget(self, product_name):
        product_frame = ctk.CTkFrame(self.scrollable_frame)
        product_frame.pack(fill="x", pady=2, padx=5)

        label = ctk.CTkLabel(product_frame, text=product_name, anchor="w")
        label.pack(side="left", fill="x", expand=True, padx=10)

        vcmd = (self.register(self.validate_integer_input), '%P')
        entry = ctk.CTkEntry(product_frame, width=80, justify="center", validate="key", validatecommand=vcmd)
        entry.pack(side="right", padx=10)
        
        # Shortcut de enter
        entry.bind("<Return>", lambda e: self.finish_and_export())

        self.product_widgets[product_name] = {'frame': product_frame, 'entry': entry}

    def validate_integer_input(self, P):
        return P.isdigit() or P == ""

    def update_status(self, message, clear_after_ms=5000):
        self.status_label.configure(text=message)
        if clear_after_ms:
            self.after(clear_after_ms, lambda: self.status_label.configure(text="Pronto"))

    def finish_and_export(self):
        conferente = self.conferente_entry.get()
        if not conferente:
            CTkMessagebox(title="Erro de Validação", message="O campo 'Nome do Conferente' não pode estar vazio.", icon="warning")
            self.update_status("Salvamento cancelado: Nome do conferente é obrigatório.", 5000)
            return

        export_data = []
        
        for product_name, widgets in self.product_widgets.items():
            quantity = widgets['entry'].get()
            if quantity: # Se digitou algo, ele tenta salvar
                try:
                    export_data.append({
                        'Conferente': conferente,
                        'Produto': product_name,
                        'Quantidade': int(quantity)
                    })
                except ValueError:
                    # Este erro é improvável com a validação de entrada, mas é uma boa prática mantê-lo.
                    CTkMessagebox(title="Erro de Dados", message=f"Valor inválido para quantidade no produto '{product_name}'. Use apenas números.", icon="error")
                    return

        if not export_data:
            CTkMessagebox(title="Nenhum Dado", message="Nenhum produto foi preenchido. Digite as quantidades ao lado dos itens contados.", icon="warning")
            self.update_status("Salvamento cancelado: Nenhum produto marcado.", 5000)
            return

        # Desabilita o botão para evitar cliques duplos e dar feedback
        self.export_button.configure(state="disabled", text="Salvando...")
        self.update() # Força a atualização da UI

        # Salva o conferente para a próxima vez
        self.db_manager.set_last_used_conferente(conferente)
        
        try:
            timestamp = datetime.datetime.now()
            entries_to_add = []
            for record in export_data:
                entries_to_add.append({
                    'entry_datetime': timestamp,
                    'conferente_name': record['Conferente'],
                    'product_name': record['Produto'],
                    'quantity': record['Quantidade']
                })

            if self.overwrite_checkbox.get() == 1:
                # Usa a lógica de "upsert" (update/insert)
                success, error_message = self.db_manager.upsert_multiple_stock_entries(entries_to_add)
            else:
                # Usa a lógica original de apenas inserir novos registros
                success, error_message = self.db_manager.add_multiple_stock_entries(entries_to_add)

            if not success:
                raise Exception(error_message)
        except Exception as e:
            CTkMessagebox(title="Erro ao Salvar", message=f"Ocorreu um erro ao salvar no banco de dados:\n{e}\n\nA operação foi revertida e nenhum dado foi salvo.", icon="error")
            self.update_status("Falha ao salvar. Dados não foram salvos.", 5000)
            # Reabilita o botão em caso de erro
            self.export_button.configure(state="normal", text="Salvar Conferência")
            return

        # Limpa os campos dos itens que foram salvos
        for product_name, widgets in self.product_widgets.items():
            if widgets['entry'].get(): # Se estava preenchido, reseta
                widgets['entry'].delete(0, 'end')

        # Reabilita o botão
        self.export_button.configure(state="normal", text="Salvar Conferência")
        CTkMessagebox(title="Sucesso", message="Dados da conferência salvos com sucesso no banco de dados.", icon="check")
        self.update_status("Conferência salva com sucesso.")

    def refresh_conferente_combobox(self):
        conferentes = self.db_manager.get_all_conferentes()
        self.conferente_entry.configure(values=conferentes)
        self.conferente_entry.set("")
        # Atualiza a janela de busca se ela estiver aberta
        if hasattr(self, '_search_win') and self._search_win.winfo_exists():
            self._search_win.refresh_filter_options()

    def refresh_product_list(self):
        self.load_and_display_products()
        self.update_status("Lista de produtos atualizada.", 3000)
        # Atualiza a janela de busca se ela estiver aberta
        if hasattr(self, '_search_win') and self._search_win.winfo_exists():
            self._search_win.refresh_filter_options()

    def open_search_window(self):
        if not hasattr(self, '_search_win') or not self._search_win.winfo_exists():
            self._search_win = SearchWindow(self)
            self._search_win.grab_set()
        else:
            self._search_win.refresh_filter_options()
            self._search_win.focus()

    def open_conferente_manager(self):
        if not hasattr(self, '_conferente_win') or not self._conferente_win.winfo_exists():
            self._conferente_win = ConferenteManagerWindow(self)
            self._conferente_win.grab_set()

    def open_product_manager(self):
        if not hasattr(self, '_product_win') or not self._product_win.winfo_exists():
            self._product_win = ProductManagerWindow(self)
            self._product_win.grab_set()

# --- Bloco de Execução Principal ---

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()