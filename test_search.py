from sistema_estoque import InventoryApp
import traceback

def main():
    try:
        app = InventoryApp()
        app.update()
        app.open_search_window()
        app._search_win.update()
        try:
            app._search_win.perform_search()
            print("BUSCA: OK!")
        except Exception as e:
            traceback.print_exc()
        app.destroy()
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    main()
