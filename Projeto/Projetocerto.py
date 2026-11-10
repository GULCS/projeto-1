# Projeto - Exchange de Criptomoedas
# CCP110 - Fundamentos de Algoritmos
# Aluno: Gustavo Levi Cano Sahid - RA: 22.226.006-9

from random import random
from datetime import datetime

ARQ_INVESTIDORES = "investidores.txt"
ARQ_COTACOES = "cotacoes.txt"

MOEDAS = ["BTC", "ETH", "XRP"]
NOMES = {"BTC": "Bitcoin", "ETH": "Ethereum", "XRP": "Ripple"}


# ---------------- arquivos ----------------

def carregar_investidores():
    investidores = {}
    try:
        arquivo = open(ARQ_INVESTIDORES, "r")
    except FileNotFoundError:
        # primeira execucao: cria um investidor de exemplo
        investidores["12345678900"] = {"senha": "123456", "nome": "Gustavo Levi Cano Sahid",
                                       "REAL": 0.0, "BTC": 0.0, "ETH": 0.0, "XRP": 0.0}
        salvar_investidores(investidores)
        return investidores

    for linha in arquivo.readlines():
        linha = linha.strip()
        if linha == "":
            continue
        d = linha.split(";")
        investidores[d[0]] = {"senha": d[1], "nome": d[2], "REAL": float(d[3]),
                              "BTC": float(d[4]), "ETH": float(d[5]), "XRP": float(d[6])}
    arquivo.close()
    return investidores


def salvar_investidores(investidores):
    arquivo = open(ARQ_INVESTIDORES, "w")
    for cpf in investidores:
        u = investidores[cpf]
        arquivo.write("%s;%s;%s;%.2f;%.8f;%.8f;%.8f\n" % (cpf, u["senha"], u["nome"], u["REAL"],
                                                          u["BTC"], u["ETH"], u["XRP"]))
    arquivo.close()


def carregar_cotacoes():
    cotacoes = {}
    try:
        arquivo = open(ARQ_COTACOES, "r")
    except FileNotFoundError:
        # cotacao inicial, taxa de compra, taxa de venda
        cotacoes["BTC"] = [350000.00, 0.02, 0.03]
        cotacoes["ETH"] = [16108.00, 0.01, 0.02]
        cotacoes["XRP"] = [2.57, 0.01, 0.01]
        salvar_cotacoes(cotacoes)
        return cotacoes

    for linha in arquivo.readlines():
        linha = linha.strip()
        if linha == "":
            continue
        d = linha.split(";")
        cotacoes[d[0]] = [float(d[1]), float(d[2]), float(d[3])]
    arquivo.close()
    return cotacoes


def salvar_cotacoes(cotacoes):
    arquivo = open(ARQ_COTACOES, "w")
    for sigla in cotacoes:
        c = cotacoes[sigla]
        arquivo.write("%s;%.4f;%.2f;%.2f\n" % (sigla, c[0], c[1], c[2]))
    arquivo.close()


def registrar_extrato(cpf, usuario, sinal, valor, moeda, cotacao, taxa):
    # cada investidor tem o seu proprio arquivo de extrato
    data = datetime.now().strftime("%d-%m-%Y %H:%M")
    linha = "%s %s %.2f %-4s CT: %-8.2f TX: %.2f REAL: %.2f BTC: %.6f ETH: %.6f XRP: %.2f\n" % (
        data, sinal, valor, moeda, cotacao, taxa,
        usuario["REAL"], usuario["BTC"], usuario["ETH"], usuario["XRP"])
    arquivo = open("extrato_%s.txt" % cpf, "a")
    arquivo.write(linha)
    arquivo.close()


# ---------------- auxiliares ----------------

def formata_cpf(cpf):
    return "%s.%s.%s-%s" % (cpf[0:3], cpf[3:6], cpf[6:9], cpf[9:11])


def virgula(valor, casas):
    # mostra o numero no formato brasileiro (580,00)
    return ("%.*f" % (casas, valor)).replace(".", ",")


def ler_valor(mensagem):
    while True:
        texto = input(mensagem).replace(",", ".")
        try:
            valor = float(texto)
        except ValueError:
            print("Valor invalido, digite um numero.")
            continue
        if valor <= 0:
            print("O valor precisa ser maior que zero.")
        else:
            return valor


def confere_senha(usuario):
    senha = input("Digite sua senha: ")
    if senha == usuario["senha"]:
        return True
    print("Senha incorreta!")
    return False


def mostrar_saldo(cpf, usuario):
    print()
    print("Nome:", usuario["nome"])
    print("CPF:", formata_cpf(cpf))
    print()
    print("Reais:", virgula(usuario["REAL"], 2))
    print("Bitcoin:", virgula(usuario["BTC"], 4))
    print("Ethereum:", virgula(usuario["ETH"], 4))
    print("Ripple:", virgula(usuario["XRP"], 2))


def mostrar_cotacoes(cotacoes):
    print()
    print("Moeda      Cotacao (R$)    Tx compra  Tx venda")
    for i in range(len(MOEDAS)):
        sigla = MOEDAS[i]
        c = cotacoes[sigla]
        print("%d - %-8s %14s %8d%% %8d%%" % (i + 1, NOMES[sigla], virgula(c[0], 2),
                                              round(c[1] * 100), round(c[2] * 100)))


def escolher_moeda():
    opcao = input("Escolha a criptomoeda (1-3): ")
    if opcao in ["1", "2", "3"]:
        return MOEDAS[int(opcao) - 1]
    print("Opcao invalida!")
    return None


# ---------------- operacoes do menu ----------------

def consultar_saldo(cpf, usuario):
    if confere_senha(usuario):
        mostrar_saldo(cpf, usuario)


def consultar_extrato(cpf, usuario):
    if not confere_senha(usuario):
        return
    print()
    print("Nome:", usuario["nome"])
    print("CPF:", formata_cpf(cpf))
    print()
    try:
        arquivo = open("extrato_%s.txt" % cpf, "r")
    except FileNotFoundError:
        print("Nenhuma operacao realizada ainda.")
        return
    for linha in arquivo.readlines():
        print(linha, end="")
    arquivo.close()


def depositar(cpf, usuario, investidores):
    valor = ler_valor("Valor do deposito: R$ ")
    usuario["REAL"] += valor
    salvar_investidores(investidores)
    registrar_extrato(cpf, usuario, "+", valor, "REAL", 0, 0)
    print("Deposito realizado!")
    mostrar_saldo(cpf, usuario)


def sacar(cpf, usuario, investidores):
    valor = ler_valor("Valor do saque: R$ ")
    if valor > usuario["REAL"]:
        print("Saldo insuficiente! Voce tem R$", virgula(usuario["REAL"], 2))
        return
    usuario["REAL"] -= valor
    salvar_investidores(investidores)
    registrar_extrato(cpf, usuario, "-", valor, "REAL", 0, 0)
    print("Saque realizado!")
    mostrar_saldo(cpf, usuario)


def comprar_cripto(cpf, usuario, investidores, cotacoes):
    if not confere_senha(usuario):
        return
    mostrar_cotacoes(cotacoes)
    sigla = escolher_moeda()
    if sigla is None:
        return
    cotacao, taxa = cotacoes[sigla][0], cotacoes[sigla][1]

    valor = ler_valor("Quantos reais deseja investir em %s? R$ " % NOMES[sigla])
    total = valor + valor * taxa   # a taxa e cobrada em cima do valor
    if total > usuario["REAL"]:
        print("Saldo insuficiente! Com a taxa o total seria R$ %s" % virgula(total, 2))
        return

    quantidade = valor / cotacao
    usuario["REAL"] -= total
    usuario[sigla] += quantidade
    salvar_investidores(investidores)
    registrar_extrato(cpf, usuario, "+", valor, sigla, cotacao, taxa)
    print("Compra de %s %s realizada (taxa de R$ %s)." % (virgula(quantidade, 6), sigla,
                                                          virgula(valor * taxa, 2)))
    mostrar_saldo(cpf, usuario)


def vender_cripto(cpf, usuario, investidores, cotacoes):
    if not confere_senha(usuario):
        return
    mostrar_cotacoes(cotacoes)
    sigla = escolher_moeda()
    if sigla is None:
        return
    cotacao, taxa = cotacoes[sigla][0], cotacoes[sigla][2]

    print("Voce tem %s %s (R$ %s)" % (virgula(usuario[sigla], 6), sigla,
                                       virgula(usuario[sigla] * cotacao, 2)))
    valor = ler_valor("Quantos reais em %s deseja vender? R$ " % NOMES[sigla])
    quantidade = valor / cotacao
    if quantidade > usuario[sigla]:
        print("Saldo de %s insuficiente!" % NOMES[sigla])
        return

    usuario[sigla] -= quantidade
    usuario["REAL"] += valor - valor * taxa   # desconta a taxa de venda
    salvar_investidores(investidores)
    registrar_extrato(cpf, usuario, "-", valor, sigla, cotacao, taxa)
    print("Venda realizada! Voce recebeu R$ %s (taxa de R$ %s)." % (virgula(valor - valor * taxa, 2),
                                                                    virgula(valor * taxa, 2)))
    mostrar_saldo(cpf, usuario)


def atualizar_cotacao(cotacoes):
    print()
    for sigla in MOEDAS:
        antiga = cotacoes[sigla][0]
        variacao = random() * 0.10 - 0.05   # entre -5% e +5%
        cotacoes[sigla][0] = antiga + antiga * variacao
        print("%-8s R$ %s -> R$ %s (%+.2f%%)" % (NOMES[sigla], virgula(antiga, 2),
                                                  virgula(cotacoes[sigla][0], 2), variacao * 100))
    salvar_cotacoes(cotacoes)


# ---------------- login e menu ----------------

def login(investidores):
    while True:
        print("\n===== EXCHANGE DE CRIPTOMOEDAS =====")
        cpf = input("CPF (somente numeros): ")
        senha = input("Senha (6 digitos): ")

        if len(cpf) != 11 or not cpf.isdigit():
            print("CPF deve ter 11 numeros, sem pontos e sem traco.")
        elif len(senha) != 6 or not senha.isdigit():
            print("A senha deve ter 6 numeros.")
        elif cpf in investidores and investidores[cpf]["senha"] == senha:
            print("Bem-vindo(a), %s!" % investidores[cpf]["nome"])
            return cpf
        else:
            print("CPF ou senha incorretos.")


def menu(cpf, investidores, cotacoes):
    usuario = investidores[cpf]
    while True:
        print("\n----------- MENU -----------")
        print("1. Consultar saldo")
        print("2. Consultar extrato")
        print("3. Depositar")
        print("4. Sacar")
        print("5. Comprar criptomoedas")
        print("6. Vender criptomoedas")
        print("7. Atualizar cotacao")
        print("8. Sair")
        opcao = input("Opcao: ")

        if opcao == "1":
            consultar_saldo(cpf, usuario)
        elif opcao == "2":
            consultar_extrato(cpf, usuario)
        elif opcao == "3":
            depositar(cpf, usuario, investidores)
        elif opcao == "4":
            sacar(cpf, usuario, investidores)
        elif opcao == "5":
            comprar_cripto(cpf, usuario, investidores, cotacoes)
        elif opcao == "6":
            vender_cripto(cpf, usuario, investidores, cotacoes)
        elif opcao == "7":
            atualizar_cotacao(cotacoes)
        elif opcao == "8":
            print("Saindo... ate logo!")
            break
        else:
            print("Opcao invalida!")


investidores = carregar_investidores()
cotacoes = carregar_cotacoes()
cpf = login(investidores)
menu(cpf, investidores, cotacoes)
