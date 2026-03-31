# 📘 Documentação da Arquitetura: GomesTech EstoqueControl

Esta documentação fornece uma visão geral clara da estrutura do projeto e detalha o papel de cada script que compõe a nossa aplicação. O sistema foi refatorado utilizando conceitos de modularização (MVC e Separação de Preocupações), o que facilita muito manutenções, melhorias visuais e escalabilidade no futuro.

---

## Estrutura Principal dos Arquivos

A aplicação foi rigorosamente dividida em "Camada Visual" (Interface), "Camada de Dados" (Banco de dados) e "Serviços Extracurriculares" (Exportação de Planilhas).

### 1. `sistema_estoque.py`
**Responsabilidade:** É o coração visual da operação (User Interface - UI). É este o arquivo que o PyInstaller lê para gerar o `.exe`.
*   **O que ele faz?** Tudo que você ou o funcionário vê na tela é desenhado aqui usando `customtkinter`, `CTkTable` e `CTkMessagebox`.
*   **Principais Funcionalidades:**
    *   Constrói o **Dashboard** inicial.
    *   Cria a lista contínua com barras de texto inteligentes onde o funcionário digita as contagens e já é salvo automaticamente com <Enter>.
    *   Gerencia as pop-ups de interface para adicionar novos Conferentes e Produtos (Janelas do tipo *Toplevel*).
    *   Controla a janela de `Consultar Histórico`.
*   **Por que é separado?** Porque ele não precisa saber como salvar no SQL puro ou como pintar o fundo de uma célula do Excel; caso precise fazer essas funções, ele simplesmente "ordena" que os demais gerentes (`database_manager` ou `export_manager`) façam.

---

### 2. `database_manager.py`
**Responsabilidade:** É o zelador dos seus dados, a única ponte de comunicação oficial entre a sua telinha azul (App) e o arquivo real do SQLite (`estoque.db`).
*   **O que ele faz?** Executa as famosas *Queries* (Buscas, Criações e Deleções em SQL). 
*   **Melhorias e Diferenciais:**
    *   **Context Managers (`with`):** Ele empacota qualquer salvamento que você faz em "blocos super seguros". Se acabar a energia no meio de um clique de Salvar Múltiplos Itens, o banco não é corrompido (as linhas são abortadas automaticamente via *Rollback*).
    *   **Tradução Humana:** Ele varre os erros complicados do banco de dados (exemplo: "UNIQUE constraint failed") e transforma em retornos que o `sistema_estoque.py` entende, retornando mensagens como `"Erro de Duplicata"`.
    *   Ele possui as restrições que proíbem deletar um Conferente que já possui histórico (`FOREIGN KEY RESTRICT`).

---

### 3. `export_manager.py`
**Responsabilidade:** O especialista em Microsoft Excel (Serviço de Exportação).
*   **O que ele faz?** Quando o usuário decide exportar o histórico depois de uma consulta, é neste script que a mágica da planilha ocorre.
*   **Principais Funcionalidades:**
    *   Lê os dados formatados usando o poderoso `pandas` (`DataFrame`).
    *   Usa o motor do `openpyxl` debaixo dos panos para ditar regras de Design da tabela: cabeçalhos com o fundo *Azul Escuro*, largura automática e alinhamento centralizado para todas as colunas do seu Excel gerado.
*   **Por que ele existe?** Porque códigos visuais e códigos de formatação de relatório não combinam no mesmo arquivo. Separando isso, no dia de amanhã se você quiser adicionar exportação para PDF, basta colocar as regrinhas exclusivas aqui.

---

## Arquivos de Configuração e Debug

*   **`sistema_estoque.spec`**: Um roteiro gravado em texto. É ele que ensina o `PyInstaller` (gerador do executável) quais bibliotecas (CTk, pandas, openpyxl) precisam ser comprimidas e congeladas num arquivo só (`sistema_estoque.exe`) da forma correta sem dar falhas de "ModuleNotFound".
*   **Scripts de Teste (`test_query.py` e `test_search.py`)**: Foram arquivos descartáveis (scripts de debug) que foram criados temporariamente para testar a comunicação pura do banco de dados e contornar de maneira programática as falhas na biblioteca gráfica do *CTkTable*. Eles não afetam sua aplicação.
