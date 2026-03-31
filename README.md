# 📦 GomesTech EstoqueControl

Sistema de gerenciamento de inventário e controle de estoque desenvolvido em Python, focado em alta disponibilidade, integridade de dados e automação de processos operacionais.

## 🚀 Sobre o Projeto

O sistema foi projetado para atuar na ponte entre a execução técnica e a estratégia de negócios, permitindo o registro preciso de conferências de materiais, auditoria de histórico e exportação de relatórios para suporte à decisão da diretoria.

## 🛠️ Tecnologias Utilizadas

-   **Linguagem Principal:** Python 3.x
-   **Interface Gráfica (GUI):** CustomTkinter (Modern Dark Mode)
-   **Banco de Dados:** SQLite com suporte a transações ACID e Integridade Referencial
-   **Manipulação de Dados:** Pandas
-   **Relatórios:** Openpyxl (Geração de planilhas Excel formatadas)

## ✨ Funcionalidades Principais

-   **Controle de Conferência:** Registro de entradas de estoque vinculadas a conferentes específicos com timestamp automático.
-   **Lógica de Upsert:** Opção de sobrescrever contagens existentes no mesmo dia, evitando redundância de dados.
-   **Busca Avançada:** Filtros dinâmicos por data, produto ou colaborador.
-   **Edição em Tempo Real:** Alteração de quantidades diretamente na interface de consulta com persistência segura no banco de dados.
-   **Exportação Estratégica:** Gerador de relatórios em Excel com formatação automática para apresentações e auditorias.
-   **Segurança de Dados:** Implementação de chaves estrangeiras (FOREIGN KEYS) para prevenir a exclusão de produtos com histórico vinculado.

## 🏗️ Estrutura do Software

O projeto segue uma arquitetura modular para facilitar a manutenção e escalabilidade:

-   `database_manager.py`: Camada de persistência e gerenciamento de banco de dados SQL.
-   `sistema_estoque.py`: Camada de interface e lógica de negócios.

## 📋 Requisitos de Instalação

Para rodar o projeto localmente, é necessário instalar as dependências via pip:

```bash
pip install customtkinter pandas openpyxl
```

## 👤 Autor

**Victor de Souza Gomes** - Analista Técnico de TI | Especialista em Automação e Infraestrutura
*Graduando em Gestão da Tecnologia da Informação.*