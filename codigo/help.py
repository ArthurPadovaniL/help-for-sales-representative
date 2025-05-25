import pandas as pd
from datetime import datetime
from pandas.tseries.offsets import DateOffset
from tabulate import tabulate
import os

# Ler todas as planilhas do arquivo Excel
arquivo = 'dados/planilha_vendas_teste.xlsx'
print(arquivo) 
# coloque a planilia na pasta dados e depois mude o nome para a sua planila do exel
planilhas = pd.read_excel(arquivo, sheet_name=None)
df = pd.concat(planilhas.values(), ignore_index=True)

# Padronizar datas
df['Ano Mês'] = pd.to_datetime(df['Ano Mês'], errors='coerce')

#Menu principal
while True:
    print("\n MENU ")
    print("1️ Verificar clientes inativos de um item")
    print("2️ meta sobre um item específico")
    print("3️ Verificar metas sobre vendas")
    print("4️ Top 10 clientes + item que mais compram")
    print("5️ Sair")
    
    opcao = input("\nEscolha uma opção: ")
#verifica os clientes inativos em algum produto especifico
    if opcao == "1":
        vendedor = input("\n Seu nome (Vendedor): ").strip()
        item = input(" Nome do item: ").strip()
        meses = int(input(" Meses sem compra: "))

        df_vendedor = df[df['Vendedor'].str.lower() == vendedor.lower()]

        if df_vendedor.empty:
            print(f"\n Vendedor '{vendedor}' não encontrado.")
            continue

        df_item = df_vendedor[df_vendedor['Item'].str.lower() == item.lower()]

        if df_item.empty:
            print(f"\n O vendedor '{vendedor}' não vendeu o item '{item}'.")
            continue

        limite = datetime.today() - DateOffset(months=meses)

        ultimas = df_item.groupby('Cliente')['Ano Mês'].max().reset_index()
        ultimas.columns = ['Cliente', 'Última Compra']

        benchmark = df_item.groupby('Cliente')['Volume Realizado'].sum().reset_index()
        benchmark.columns = ['Cliente', 'Total Comprado']

        relatorio = pd.merge(ultimas, benchmark, on='Cliente')

        relatorio_filtrado = relatorio[relatorio['Última Compra'] < limite]

        print(f"\n Clientes do vendedor '{vendedor}' que não compram '{item}' há mais de {meses} meses:\n")
        if relatorio_filtrado.empty:
            print(" Todos os clientes compraram recentemente.")
        else:
            relatorio_filtrado.loc[:, 'Última Compra'] = relatorio_filtrado['Última Compra'].dt.strftime('%d/%m/%Y')
            print(tabulate(relatorio_filtrado.sort_values('Última Compra'), headers='keys', tablefmt='grid'))
#       verifica a meta de vendas em um item especifico
    elif opcao == "2":
        vendedor = input("\n Seu nome (Vendedor): ").strip()
        item = input(" Nome do item: ").strip()

        df_vendedor = df[df['Vendedor'].str.lower() == vendedor.lower()]

        if df_vendedor.empty:
            print(f"\n Vendedor '{vendedor}' não encontrado.")
            continue

        df_item = df_vendedor[df_vendedor['Item'].str.lower() == item.lower()]

        if df_item.empty:
            print(f"\n O vendedor '{vendedor}' não vendeu o item '{item}'.")
            continue

        df_item = df_item.copy()
        df_item['Bateu Meta'] = df_item['Faturamento Realizado'] >= df_item['Faturamento Meta']

        if df_item['Bateu Meta'].all():
            print(f"\n O vendedor '{vendedor}' BATEU a meta em TODAS as vendas do item '{item}'.")
        elif df_item['Bateu Meta'].any():
            print(f"\n O vendedor '{vendedor}' bateu a meta em ALGUMAS vendas do item '{item}', mas não em todas.")
        else:
            print(f"\n O vendedor '{vendedor}' NÃO bateu a meta em nenhuma venda do item '{item}'.")
#           verifica metas no geral
    elif opcao == "3":
        vendedor = input("\n Seu nome (Vendedor): ").strip()

        df_vendedor = df[df['Vendedor'].str.lower() == vendedor.lower()]

        if df_vendedor.empty:
            print(f"\n Vendedor '{vendedor}' não encontrado.")
            continue

        df_vendedor = df_vendedor.copy()
        df_vendedor['Bateu Meta'] = df_vendedor['Faturamento Realizado'] >= df_vendedor['Faturamento Meta']

        total_vendas = df_vendedor.shape[0]
        metas_batidas = df_vendedor['Bateu Meta'].sum()
        metas_nao_batidas = total_vendas - metas_batidas
        taxa_sucesso = (metas_batidas / total_vendas) * 100 if total_vendas > 0 else 0

        print(f"\n Análise geral de metas do vendedor '{vendedor}':")
        print(f" Total de vendas: {total_vendas}")
        print(f" Metas batidas: {metas_batidas}")
        print(f" Metas NÃO batidas: {metas_nao_batidas}")
        print(f" Taxa de sucesso: {taxa_sucesso:.2f}%")
#          Os top 10 melhores clientes
    elif opcao == "4":
        vendedor = input("\n Seu nome (Vendedor): ").strip()

        df_vendedor = df[df['Vendedor'].str.lower() == vendedor.lower()]

        if df_vendedor.empty:
            print(f"\n Vendedor '{vendedor}' não encontrado.")
            continue

        # Top 10 clientes por Volume Realizado
        top_clientes = df_vendedor.groupby('Cliente')['Volume Realizado'].sum().reset_index()
        top_clientes = top_clientes.sort_values(by='Volume Realizado', ascending=False).head(10)

        # Item mais comprado de cada cliente
        itens_por_cliente = df_vendedor.groupby(['Cliente', 'Item'])['Volume Realizado'].sum().reset_index()

        lista = []
        for _, row in top_clientes.iterrows():
            cliente = row['Cliente']
            total = row['Volume Realizado']
            itens_cliente = itens_por_cliente[itens_por_cliente['Cliente'] == cliente]
            item_mais_comprado = itens_cliente.sort_values(by='Volume Realizado', ascending=False).iloc[0]['Item']
            lista.append({'Cliente': cliente, 'Total Comprado': total, 'Item Mais Comprado': item_mais_comprado})

        relatorio = pd.DataFrame(lista)

        print(f"\n Top 10 clientes do vendedor '{vendedor}':\n")
        print(tabulate(relatorio, headers='keys', tablefmt='grid'))
#sair
    elif opcao == "5":
        print("\n Encerrando... Até logo!")
        break

    else:
        print("\n Opção inválida. Tente novamente.")

