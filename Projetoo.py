# =====================================================================
# PROJETO: EXCHANGE DE CRIPTOMOEDAS - versão INDIVIDUAL
# CCP110 - Fundamentos de Algoritmos - Centro Universitário FEI
# ---------------------------------------------------------------------
# REFATORAÇÃO: nenhuma variável global.
# Todos os dados circulam como parâmetros e valores de retorno.
#
# COMPRA: o investidor informa a QUANTIDADE de criptomoeda desejada.
#   valor_bruto = quantidade * cotacao
#   taxa        = valor_bruto * taxa_compra
#   total       = valor_bruto + taxa   (debitado do saldo em reais)
#
# Arquivos .txt manipulados:
#   usuarios.txt     -> cpf;nome;senha;reais;BTC;ETH;XRP
#   criptomoedas.txt -> nome;ticker;cotacao;taxa_compra;taxa_venda
#   extrato.txt      -> cpf;data;sinal;valor;ativo;cotacao;taxa;reais;BTC;ETH;XRP
# =====================================================================

import os
import random
from datetime import datetime

ARQ_USUARIOS = "usuarios.txt"
ARQ_CRIPTOMOEDAS = "criptomoedas.txt"
ARQ_EXTRATO = "extrato.txt"


# =====================================================================
# 1) FORMATAÇÃO
# =====================================================================
def brl(valor):
    """1234.5 -> '1.234,50' (padrão brasileiro)."""
    texto = f"{valor:,.2f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_cripto(valor):
    """Remove zeros inúteis: 0.01580000 -> '0,0158'."""
    texto = f"{valor:.8f}".rstrip("0").rstrip(".")
    return (texto or "0").replace(".", ",")


def formatar_cpf(cpf):
    """12345678900 -> '123.456.789-00'."""
    cpf = str(cpf).zfill(11)
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def formatar_linha_extrato(registro):
    """Monta uma linha do extrato no formato do enunciado."""
    return (f"{registro['data']} {registro['sinal']} {registro['valor']:.2f} "
            f"{registro['ativo']:<4} CT: {registro['cotacao']:.2f} "
            f"TX: {registro['taxa']:.2f} REAL: {registro['real']:.2f} "
            f"BTC: {registro['BTC']:.6f} ETH: {registro['ETH']:.6f} "
            f"XRP: {registro['XRP']:.6f}")


# =====================================================================
# 2) ENTRADA DE DADOS COM VALIDAÇÃO
# =====================================================================
def ler_valor(mensagem):
    """Lê um número positivo. Retorna None se inválido."""
    texto = input(mensagem).strip().replace(",", ".")
    try:
        valor = float(texto)
    except ValueError:
        print(">>> Valor inválido. Use apenas números (ex.: 0,0158).")
        return None
    if valor <= 0:
        print(">>> O valor deve ser maior que zero.")
        return None
    return valor


def ler_senha(mensagem="Senha (6 dígitos): "):
    """Lê e valida o formato da senha."""
    senha = input(mensagem).strip()
    if not senha.isdigit() or len(senha) != 6:
        print(">>> Senha inválida: digite exatamente 6 dígitos numéricos.")
        return None
    return senha


def confirmar_senha(usuario):
    """Confere a senha digitada com a senha cadastrada."""
    senha = ler_senha()
    if senha is None:
        return False
    if senha != usuario["senha"]:
        print(">>> Senha incorreta.")
        return False
    return True


# =====================================================================
# 3) PERSISTÊNCIA - LEITURA
# =====================================================================
def criar_dados_iniciais():
    """Na primeira execução, cria os arquivos com dados padrão."""
    if not os.path.exists(ARQ_CRIPTOMOEDAS):
        with open(ARQ_CRIPTOMOEDAS, "w", encoding="utf-8") as arq:
            arq.write("Bitcoin;BTC;340000.00;0.02;0.03\n")
            arq.write("Ethereum;ETH;16108.00;0.01;0.02\n")
            arq.write("Ripple;XRP;2.57;0.01;0.01\n")

    if not os.path.exists(ARQ_USUARIOS):
        with open(ARQ_USUARIOS, "w", encoding="utf-8") as arq:
            arq.write("12345678900;Investidor Teste;123456;1000.00;"
                      "0.00000000;0.00000000;0.00000000\n")

    if not os.path.exists(ARQ_EXTRATO):
        with open(ARQ_EXTRATO, "w", encoding="utf-8"):
            pass


def carregar_usuarios():
    usuarios = []
    if not os.path.exists(ARQ_USUARIOS):
        return usuarios

    with open(ARQ_USUARIOS, "r", encoding="utf-8") as arq:
        for linha in arq:
            campos = linha.strip().split(";")
            if len(campos) != 7:
                continue
            usuarios.append({
                "cpf": campos[0],
                "nome": campos[1],
                "senha": campos[2],
                "real": float(campos[3]),
                "BTC": float(campos[4]),
                "ETH": float(campos[5]),
                "XRP": float(campos[6]),
            })
    return usuarios


def carregar_criptomoedas():
    criptomoedas = []
    if not os.path.exists(ARQ_CRIPTOMOEDAS):
        return criptomoedas

    with open(ARQ_CRIPTOMOEDAS, "r", encoding="utf-8") as arq:
        for linha in arq:
            campos = linha.strip().split(";")
            if len(campos) != 5:
                continue
            criptomoedas.append({
                "nome": campos[0],
                "ticker": campos[1],
                "cotacao": float(campos[2]),
                "taxa_compra": float(campos[3]),
                "taxa_venda": float(campos[4]),
            })
    return criptomoedas


def carregar_extrato():
    registros = []
    if not os.path.exists(ARQ_EXTRATO):
        return registros

    with open(ARQ_EXTRATO, "r", encoding="utf-8") as arq:
        for linha in arq:
            campos = linha.strip().split(";")
            if len(campos) != 11:
                continue
            registros.append({
                "cpf": campos[0],
                "data": campos[1],
                "sinal": campos[2],
                "valor": float(campos[3]),
                "ativo": campos[4],
                "cotacao": float(campos[5]),
                "taxa": float(campos[6]),
                "real": float(campos[7]),
                "BTC": float(campos[8]),
                "ETH": float(campos[9]),
                "XRP": float(campos[10]),
            })
    return registros


# =====================================================================
# 4) PERSISTÊNCIA - GRAVAÇÃO
# =====================================================================
def salvar_usuarios(usuarios):
    with open(ARQ_USUARIOS, "w", encoding="utf-8") as arq:
        for u in usuarios:
            arq.write(f"{u['cpf']};{u['nome']};{u['senha']};{u['real']:.2f};"
                      f"{u['BTC']:.8f};{u['ETH']:.8f};{u['XRP']:.8f}\n")


def salvar_criptomoedas(criptomoedas):
    with open(ARQ_CRIPTOMOEDAS, "w", encoding="utf-8") as arq:
        for c in criptomoedas:
            arq.write(f"{c['nome']};{c['ticker']};{c['cotacao']:.2f};"
                      f"{c['taxa_compra']:.4f};{c['taxa_venda']:.4f}\n")


def anexar_extrato(registro):
    """Acrescenta uma operação ao arquivo de extrato."""
    with open(ARQ_EXTRATO, "a", encoding="utf-8") as arq:
        arq.write(f"{registro['cpf']};{registro['data']};{registro['sinal']};"
                  f"{registro['valor']:.2f};{registro['ativo']};"
                  f"{registro['cotacao']:.2f};{registro['taxa']:.4f};"
                  f"{registro['real']:.2f};{registro['BTC']:.8f};"
                  f"{registro['ETH']:.8f};{registro['XRP']:.8f}\n")


# =====================================================================
# 5) FUNÇÕES AUXILIARES DE NEGÓCIO
# =====================================================================
def buscar_usuario(usuarios, cpf):
    for usuario in usuarios:
        if usuario["cpf"] == cpf:
            return usuario
    return None


def registrar_operacao(usuario, sinal, valor, ativo, cotacao, taxa):
    """Monta o registro da operação e grava no arquivo de extrato."""
    registro = {
        "cpf": usuario["cpf"],
        "data": datetime.now().strftime("%d-%m-%Y %H:%M"),
        "sinal": sinal,
        "valor": valor,
        "ativo": ativo,
        "cotacao": cotacao,
        "taxa": taxa,
        "real": usuario["real"],
        "BTC": usuario["BTC"],
        "ETH": usuario["ETH"],
        "XRP": usuario["XRP"],
    }
    anexar_extrato(registro)


def mostrar_saldos(usuario, criptomoedas):
    print("\n----------------------------------------------")
    print(f"Nome: {usuario['nome']}")
    print(f"CPF: {formatar_cpf(usuario['cpf'])}")
    print(f"Reais: {brl(usuario['real'])}")
    for cripto in criptomoedas:
        print(f"{cripto['nome']}: {fmt_cripto(usuario[cripto['ticker']])}")
    print("----------------------------------------------")


def mostrar_cotacoes(criptomoedas):
    print("\n--- COTAÇÕES ATUAIS ---")
    for cripto in criptomoedas:
        print(f"{cripto['nome']:<10} ({cripto['ticker']}): R$ {brl(cripto['cotacao'])}"
              f" | taxa compra {cripto['taxa_compra'] * 100:.1f}%"
              f" | taxa venda {cripto['taxa_venda'] * 100:.1f}%")
    print("-----------------------")


def escolher_criptomoeda(criptomoedas):
    print("\nCriptomoedas disponíveis:")
    for indice, cripto in enumerate(criptomoedas, start=1):
        print(f"  {indice} - {cripto['nome']} ({cripto['ticker']})")

    opcao = input("Escolha a criptomoeda: ").strip()
    if not opcao.isdigit() or not (1 <= int(opcao) <= len(criptomoedas)):
        print(">>> Opção inválida.")
        return None
    return criptomoedas[int(opcao) - 1]


# =====================================================================
# 6) LOGIN E MENU
# =====================================================================
def efetuar_login(usuarios):
    print("\n=========== LOGIN DO INVESTIDOR ===========")
    cpf = input("CPF (somente números, sem pontos e traços): ").strip()

    if not cpf.isdigit() or len(cpf) != 11:
        print(">>> CPF inválido: informe 11 dígitos numéricos.")
        return None

    usuario = buscar_usuario(usuarios, cpf)
    if usuario is None:
        print(">>> CPF não cadastrado.")
        return None

    if not confirmar_senha(usuario):
        return None

    print(f"\nBem-vindo(a), {usuario['nome']}!")
    return usuario


def exibir_menu():
    print("\nGustavo ")
    print("1 - Consultar saldo")
    print("2 - Consultar extrato")
    print("3 - Depositar")
    print("4 - Sacar")
    print("5 - Comprar criptomoedas")
    print("6 - Vender criptomoedas")
    print("7 - Atualizar cotação")
    print("8 - Sair")
    print("============================================")


# =====================================================================
# 7) OPERAÇÕES DO INVESTIDOR
# Cada função devolve o usuário atualizado e um indicador de alteração.
# =====================================================================
def consultar_saldo(usuario, criptomoedas):
    print("\n=== CONSULTAR SALDO ===")
    if not confirmar_senha(usuario):
        return usuario, False
    mostrar_saldos(usuario, criptomoedas)
    return usuario, False


def consultar_extrato(usuario, criptomoedas):
    print("\n=== EXTRATO DE OPERAÇÕES ===")
    if not confirmar_senha(usuario):
        return usuario, False

    registros = [r for r in carregar_extrato() if r["cpf"] == usuario["cpf"]]

    print(f"\nNome: {usuario['nome']}")
    print(f"CPF: {formatar_cpf(usuario['cpf'])}")

    if not registros:
        print(">>> Nenhuma operação registrada até o momento.")
        return usuario, False

    for registro in registros:
        print(formatar_linha_extrato(registro))
    return usuario, False


def depositar(usuario, criptomoedas):
    print("\n=== DEPÓSITO ===")
    valor = ler_valor("Valor do depósito (R$): ")
    if valor is None:
        return usuario, False

    usuario["real"] = round(usuario["real"] + valor, 2)
    registrar_operacao(usuario, "+", valor, "REAL", 0.0, 0.0)

    print(f">>> Depósito de R$ {brl(valor)} realizado com sucesso.")
    mostrar_saldos(usuario, criptomoedas)
    return usuario, True


def sacar(usuario, criptomoedas):
    print("\n=== SAQUE ===")
    valor = ler_valor("Valor do saque (R$): ")
    if valor is None:
        return usuario, False

    if valor > usuario["real"]:
        print(f">>> Saldo insuficiente. Disponível: R$ {brl(usuario['real'])}.")
        return usuario, False

    usuario["real"] = round(usuario["real"] - valor, 2)
    registrar_operacao(usuario, "-", valor, "REAL", 0.0, 0.0)

    print(f">>> Saque de R$ {brl(valor)} realizado com sucesso.")
    mostrar_saldos(usuario, criptomoedas)
    return usuario, True


def comprar(usuario, criptomoedas):
    """Compra por QUANTIDADE de criptomoeda (taxa de compra sobre o valor)."""
    print("\n=== COMPRA DE CRIPTOMOEDAS ===")
    if not confirmar_senha(usuario):
        return usuario, False

    mostrar_cotacoes(criptomoedas)
    cripto = escolher_criptomoeda(criptomoedas)
    if cripto is None:
        return usuario, False

    ticker = cripto["ticker"]
    quantidade = ler_valor(f"Quantidade de {ticker} que deseja comprar: ")
    if quantidade is None:
        return usuario, False

    valor = quantidade * cripto["cotacao"]
    taxa = valor * cripto["taxa_compra"]
    total = valor + taxa

    if total > usuario["real"]:
        print(f">>> Saldo insuficiente. Necessário R$ {brl(total)} "
              f"(R$ {brl(valor)} + R$ {brl(taxa)} de taxa). "
              f"Disponível: R$ {brl(usuario['real'])}.")
        return usuario, False

    usuario["real"] = round(usuario["real"] - total, 2)
    usuario[ticker] = round(usuario[ticker] + quantidade, 8)
    registrar_operacao(usuario, "+", valor, ticker, cripto["cotacao"],
                       cripto["taxa_compra"])

    print(f"\n>>> Compra realizada: {fmt_cripto(quantidade)} {ticker} "
          f"a R$ {brl(cripto['cotacao'])} cada.")
    print(f"    Valor: R$ {brl(valor)} | Taxa ({cripto['taxa_compra'] * 100:.1f}%): "
          f"R$ {brl(taxa)} | Total debitado: R$ {brl(total)}")
    mostrar_saldos(usuario, criptomoedas)
    return usuario, True


def vender(usuario, criptomoedas):
    """Venda por QUANTIDADE de criptomoeda (taxa de venda sobre o valor bruto)."""
    print("\n=== VENDA DE CRIPTOMOEDAS ===")
    if not confirmar_senha(usuario):
        return usuario, False

    mostrar_cotacoes(criptomoedas)
    cripto = escolher_criptomoeda(criptomoedas)
    if cripto is None:
        return usuario, False

    ticker = cripto["ticker"]
    print(f"Você possui {fmt_cripto(usuario[ticker])} {ticker}.")

    quantidade = ler_valor(f"Quantidade de {ticker} que deseja vender: ")
    if quantidade is None:
        return usuario, False

    if quantidade > usuario[ticker]:
        print(f">>> Quantidade insuficiente. Disponível: "
              f"{fmt_cripto(usuario[ticker])} {ticker}.")
        return usuario, False

    valor = quantidade * cripto["cotacao"]
    taxa = valor * cripto["taxa_venda"]
    liquido = valor - taxa

    usuario[ticker] = round(usuario[ticker] - quantidade, 8)
    usuario["real"] = round(usuario["real"] + liquido, 2)
    registrar_operacao(usuario, "-", valor, ticker, cripto["cotacao"],
                       cripto["taxa_venda"])

    print(f"\n>>> Venda realizada: {fmt_cripto(quantidade)} {ticker} "
          f"a R$ {brl(cripto['cotacao'])} cada.")
    print(f"    Bruto: R$ {brl(valor)} | Taxa ({cripto['taxa_venda'] * 100:.1f}%): "
          f"R$ {brl(taxa)} | Creditado: R$ {brl(liquido)}")
    mostrar_saldos(usuario, criptomoedas)
    return usuario, True


def atualizar_cotacao(criptomoedas):
    """Varia cada cotação em um percentual aleatório entre -5% e +5%."""
    print("\n=== ATUALIZAÇÃO DE COTAÇÕES ===")
    for cripto in criptomoedas:
        variacao = random.uniform(-0.05, 0.05)
        anterior = cripto["cotacao"]
        cripto["cotacao"] = round(anterior * (1 + variacao), 2)
        print(f"{cripto['nome']:<10}: R$ {brl(anterior)} -> "
              f"R$ {brl(cripto['cotacao'])} ({variacao * 100:+.2f}%)")

    salvar_criptomoedas(criptomoedas)
    print(">>> Cotações atualizadas e gravadas em arquivo.")


# =====================================================================
# 8) MENU DO INVESTIDOR
# =====================================================================
def menu_investidor(usuarios, criptomoedas, usuario):
    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            usuario, _ = consultar_saldo(usuario, criptomoedas)
        elif opcao == "2":
            usuario, _ = consultar_extrato(usuario, criptomoedas)
        elif opcao == "3":
            usuario, alterou = depositar(usuario, criptomoedas)
            if alterou:
                salvar_usuarios(usuarios)
        elif opcao == "4":
            usuario, alterou = sacar(usuario, criptomoedas)
            if alterou:
                salvar_usuarios(usuarios)
        elif opcao == "5":
            usuario, alterou = comprar(usuario, criptomoedas)
            if alterou:
                salvar_usuarios(usuarios)
        elif opcao == "6":
            usuario, alterou = vender(usuario, criptomoedas)
            if alterou:
                salvar_usuarios(usuarios)
        elif opcao == "7":
            atualizar_cotacao(criptomoedas)
        elif opcao == "8":
            salvar_usuarios(usuarios)
            salvar_criptomoedas(criptomoedas)
            print("\nSaindo do sistema... Dados salvos com sucesso.")
            return
        else:
            print(">>> Opção inválida. Digite um número de 1 a 8.")


# =====================================================================
# 9) PROGRAMA PRINCIPAL
# =====================================================================
def main():
    criar_dados_iniciais()

    usuarios = carregar_usuarios()
    criptomoedas = carregar_criptomoedas()

    print("=" * 60)
    print("           EXCHANGE DE CRIPTOMOEDAS - v2.0")
    print("=" * 60)
    print("Usuário de teste -> CPF: 12345678900 | Senha: 123456")

    while True:
        usuario = efetuar_login(usuarios)

        if usuario is not None:
            menu_investidor(usuarios, criptomoedas, usuario)
            break

        resposta = input("\nDeseja tentar o login novamente? (s/n): ").strip().lower()
        if resposta != "s":
            print("\nEncerrando a Exchange. Até logo!")
            break


if __name__ == "__main__":
    main()