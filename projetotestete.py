# =====================================================================
# PROJETO: EXCHANGE DE CRIPTOMOEDAS
# Disciplina: CCP110 - Fundamentos de Algoritmos
# Centro Universitário FEI
# Modalidade: INDIVIDUAL (apenas o usuário investidor)
# ---------------------------------------------------------------------
# Funcionalidades (Entregas Parciais 1 a 4):
#   1. Login do investidor (CPF 11 dígitos + senha 6 dígitos)
#   2. Menu pós-login com as 8 opções
#   3. Consultar saldo
#   4. Consultar extrato de operações
#   5. Depositar reais
#   6. Sacar reais (saldo nunca negativo)
#   7. Comprar criptomoedas (taxa de compra)
#   8. Vender criptomoedas (taxa de venda)
#   9. Atualizar cotação (variação aleatória de -5% a +5%)
#  10. Persistência permanente em arquivos .txt
# ---------------------------------------------------------------------
# Arquivos manipulados:
#   usuarios.txt     -> cpf;nome;senha;reais;BTC;ETH;XRP
#   criptomoedas.txt -> nome;ticker;cotacao;taxa_compra;taxa_venda
#   extrato.txt      -> cpf;data;sinal;valor;ativo;cotacao;taxa;
#                       reais;BTC;ETH;XRP
# ---------------------------------------------------------------------
# COMO RODAR:
#   python Projeto.py          -> inicia normalmente
#   python Projeto.py reset    -> apaga os .txt e recomeça do zero
# ---------------------------------------------------------------------
# Observação de projeto: NÃO existem variáveis globais.
# Os dados circulam por parâmetros e valores de retorno.
# =====================================================================

import os
import sys
import random
from datetime import datetime


# =====================================================================
# 0) CONSTANTES DE CONFIGURAÇÃO
# =====================================================================
ARQ_USUARIOS = "usuarios.txt"
ARQ_CRIPTOMOEDAS = "criptomoedas.txt"
ARQ_EXTRATO = "extrato.txt"

TAMANHO_CPF = 11
TAMANHO_SENHA = 6

VARIACAO_MAXIMA = 0.05
CASAS_DECIMAIS_CRIPTO = 8
CASAS_DECIMAIS_REAL = 2

# Criptomoedas criadas na primeira execução
CRIPTOMOEDAS_PADRAO = [
    {"nome": "Bitcoin",  "ticker": "BTC", "cotacao": 340000.00,
     "taxa_compra": 0.02, "taxa_venda": 0.03},
    {"nome": "Ethereum", "ticker": "ETH", "cotacao": 16108.00,
     "taxa_compra": 0.01, "taxa_venda": 0.02},
    {"nome": "Ripple",   "ticker": "XRP", "cotacao": 2.57,
     "taxa_compra": 0.01, "taxa_venda": 0.01},
]

# Investidor criado na primeira execução
CPF_PADRAO = "12345678900"
NOME_PADRAO = "Gustavo"
SENHA_PADRAO = "123456"
REAL_PADRAO = 1000.00


# =====================================================================
# 1) FUNÇÕES DE FORMATAÇÃO
# =====================================================================
def brl(valor):
    """Formata número no padrão brasileiro: 1234.5 -> '1.234,50'."""
    texto = f"{valor:,.2f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_cripto(valor):
    """Remove zeros inúteis: 0.01580000 -> '0,0158'."""
    texto = f"{valor:.8f}".rstrip("0").rstrip(".")
    return (texto or "0").replace(".", ",")


def formatar_cpf(cpf):
    """Formata CPF para exibição: 12345678900 -> '123.456.789-00'."""
    cpf = str(cpf).zfill(TAMANHO_CPF)
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def formatar_linha_extrato(registro):
    """Monta uma linha do extrato no formato pedido no enunciado."""
    return (f"{registro['data']} {registro['sinal']} {registro['valor']:.2f} "
            f"{registro['ativo']:<4} CT: {registro['cotacao']:.2f} "
            f"TX: {registro['taxa']:.2f} REAL: {registro['real']:.2f} "
            f"BTC: {registro['BTC']:.6f} ETH: {registro['ETH']:.6f} "
            f"XRP: {registro['XRP']:.6f}")


def cabecalho(titulo):
    """Imprime um cabeçalho padronizado de seção."""
    print(f"\n=== {titulo} ===")


# =====================================================================
# 2) FUNÇÕES DE ENTRADA E VALIDAÇÃO
# =====================================================================
def ler_valor(mensagem):
    """Lê um número positivo. Retorna None se a entrada for inválida."""
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
    """Lê a senha e valida o formato (exatamente 6 dígitos numéricos)."""
    senha = input(mensagem).strip()

    if not senha.isdigit() or len(senha) != TAMANHO_SENHA:
        print(">>> Senha inválida: digite exatamente 6 dígitos numéricos.")
        return None

    return senha


def confirmar_senha(usuario):
    """Pede a senha e compara com a senha cadastrada do investidor."""
    senha = ler_senha()
    if senha is None:
        return False

    if senha != usuario.get("senha"):
        print(">>> Senha incorreta.")
        return False

    return True


# =====================================================================
# 3) PERSISTÊNCIA - RESET, CRIAÇÃO E LEITURA DOS ARQUIVOS .TXT
# =====================================================================
def resetar_dados():
    """Apaga os três arquivos .txt para recomeçar do zero.

    Chamado por: python Projeto.py reset
    """
    apagados = 0

    for arquivo in (ARQ_USUARIOS, ARQ_CRIPTOMOEDAS, ARQ_EXTRATO):
        if os.path.exists(arquivo):
            os.remove(arquivo)
            apagados += 1

    if apagados:
        print(f">>> {apagados} arquivo(s) .txt apagado(s).")
    else:
        print(">>> Nenhum arquivo .txt encontrado para apagar.")

    print(">>> Os dados padrão serão recriados na próxima execução.")


def criar_dados_iniciais():
    """Cria os arquivos .txt com os dados padrão na primeira execução."""
    if not os.path.exists(ARQ_CRIPTOMOEDAS):
        with open(ARQ_CRIPTOMOEDAS, "w", encoding="utf-8") as arq:
            for cripto in CRIPTOMOEDAS_PADRAO:
                arq.write(f"{cripto['nome']};{cripto['ticker']};"
                          f"{cripto['cotacao']:.2f};"
                          f"{cripto['taxa_compra']:.4f};"
                          f"{cripto['taxa_venda']:.4f}\n")

    if not os.path.exists(ARQ_USUARIOS):
        with open(ARQ_USUARIOS, "w", encoding="utf-8") as arq:
            arq.write(f"{CPF_PADRAO};{NOME_PADRAO};{SENHA_PADRAO};"
                      f"{REAL_PADRAO:.2f};0.00000000;0.00000000;0.00000000\n")

    if not os.path.exists(ARQ_EXTRATO):
        with open(ARQ_EXTRATO, "w", encoding="utf-8"):
            pass


def carregar_usuarios():
    """Lê usuarios.txt e devolve uma lista de dicionários."""
    usuarios = []

    if not os.path.exists(ARQ_USUARIOS):
        return usuarios

    with open(ARQ_USUARIOS, "r", encoding="utf-8") as arq:
        for linha in arq:
            campos = linha.strip().split(";")

            if len(campos) != 7:
                print(f">>> Linha ignorada em {ARQ_USUARIOS}: "
                      f"{len(campos)} campos (esperado 7).")
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
    """Lê criptomoedas.txt e devolve uma lista de dicionários."""
    criptomoedas = []

    if not os.path.exists(ARQ_CRIPTOMOEDAS):
        return criptomoedas

    with open(ARQ_CRIPTOMOEDAS, "r", encoding="utf-8") as arq:
        for linha in arq:
            campos = linha.strip().split(";")

            if len(campos) != 5:
                print(f">>> Linha ignorada em {ARQ_CRIPTOMOEDAS}: "
                      f"{len(campos)} campos (esperado 5).")
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
    """Lê extrato.txt e devolve uma lista de dicionários."""
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
# 4) PERSISTÊNCIA - GRAVAÇÃO DOS ARQUIVOS .TXT
# =====================================================================
def salvar_usuarios(usuarios):
    """Regrava usuarios.txt com todos os saldos atualizados."""
    with open(ARQ_USUARIOS, "w", encoding="utf-8") as arq:
        for u in usuarios:
            arq.write(f"{u['cpf']};{u['nome']};{u['senha']};"
                      f"{u['real']:.2f};{u.get('BTC', 0.0):.8f};"
                      f"{u.get('ETH', 0.0):.8f};{u.get('XRP', 0.0):.8f}\n")


def salvar_criptomoedas(criptomoedas):
    """Regrava criptomoedas.txt com as cotações atualizadas."""
    with open(ARQ_CRIPTOMOEDAS, "w", encoding="utf-8") as arq:
        for c in criptomoedas:
            arq.write(f"{c['nome']};{c['ticker']};{c['cotacao']:.2f};"
                      f"{c['taxa_compra']:.4f};{c['taxa_venda']:.4f}\n")


def anexar_extrato(registro):
    """Acrescenta uma operação ao final do arquivo de extrato."""
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
    """Procura um investidor pelo CPF. Retorna None se não existir."""
    for usuario in usuarios:
        if usuario.get("cpf") == cpf:
            return usuario
    return None


def sincronizar_carteira(usuario, criptomoedas):
    """Garante chave para toda criptomoeda existente no sistema.

    Evita o KeyError quando o usuarios.txt é antigo ou foi editado
    à mão e não possui alguma das colunas de criptomoeda.
    """
    for cripto in criptomoedas:
        ticker = cripto.get("ticker")
        if ticker and ticker not in usuario:
            usuario[ticker] = 0.0

    usuario.setdefault("real", 0.0)
    return usuario


def registrar_operacao(usuario, sinal, valor, ativo, cotacao, taxa):
    """Monta o registro da operação e grava no arquivo de extrato."""
    registro = {
        "cpf": usuario.get("cpf", ""),
        "data": datetime.now().strftime("%d-%m-%Y %H:%M"),
        "sinal": sinal,
        "valor": valor,
        "ativo": ativo,
        "cotacao": cotacao,
        "taxa": taxa,
        "real": usuario.get("real", 0.0),
        "BTC": usuario.get("BTC", 0.0),
        "ETH": usuario.get("ETH", 0.0),
        "XRP": usuario.get("XRP", 0.0),
    }
    anexar_extrato(registro)


def mostrar_saldos(usuario, criptomoedas):
    """Exibe a carteira do investidor com todos os saldos."""
    print("\n----------------------------------------------")
    print(f"Nome: {usuario.get('nome', '-')}")
    print(f"CPF: {formatar_cpf(usuario.get('cpf', ''))}")
    print(f"Reais: {brl(usuario.get('real', 0.0))}")

    for cripto in criptomoedas:
        ticker = cripto.get("ticker", "")
        quantidade = usuario.get(ticker, 0.0)
        print(f"{cripto.get('nome', ticker)}: {fmt_cripto(quantidade)}")

    print("----------------------------------------------")


def mostrar_cotacoes(criptomoedas):
    """Exibe as cotações e as taxas de cada criptomoeda."""
    print("\n--- COTAÇÕES ATUAIS ---")

    for cripto in criptomoedas:
        print(f"{cripto['nome']:<10} ({cripto['ticker']}): "
              f"R$ {brl(cripto['cotacao'])}"
              f" | taxa compra {cripto['taxa_compra'] * 100:.1f}%"
              f" | taxa venda {cripto['taxa_venda'] * 100:.1f}%")

    print("-----------------------")


def escolher_criptomoeda(criptomoedas):
    """Mostra as criptomoedas e devolve a escolhida (ou None)."""
    if not criptomoedas:
        print(">>> Nenhuma criptomoeda cadastrada.")
        return None

    print("\nCriptomoedas disponíveis:")
    for indice, cripto in enumerate(criptomoedas, start=1):
        print(f"  {indice} - {cripto['nome']} ({cripto['ticker']})")

    opcao = input("Escolha a criptomoeda: ").strip()

    if not opcao.isdigit() or not (1 <= int(opcao) <= len(criptomoedas)):
        print(">>> Opção inválida.")
        return None

    return criptomoedas[int(opcao) - 1]


# =====================================================================
# 6) LOGIN E MENUS
# =====================================================================
def efetuar_login(usuarios):
    """Pede CPF e senha e devolve o investidor autenticado (ou None)."""
    print("\n=========== LOGIN DO INVESTIDOR ===========")

    cpf = input("CPF (somente números, sem pontos e traços): ").strip()

    if not cpf.isdigit() or len(cpf) != TAMANHO_CPF:
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
    """Exibe o menu completo do investidor."""
    print("\n============ MENU DO INVESTIDOR ============")
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
# Cada função devolve (usuario_atualizado, houve_alteracao).
# =====================================================================
def consultar_saldo(usuario, criptomoedas):
    """Opção 1 - Consulta o saldo da carteira (exige senha)."""
    cabecalho("CONSULTAR SALDO")

    if not confirmar_senha(usuario):
        return usuario, False

    mostrar_saldos(usuario, criptomoedas)
    return usuario, False


def consultar_extrato(usuario, criptomoedas):
    """Opção 2 - Consulta o extrato de operações (exige senha)."""
    cabecalho("EXTRATO DE OPERAÇÕES")

    if not confirmar_senha(usuario):
        return usuario, False

    registros = [r for r in carregar_extrato()
                 if r.get("cpf") == usuario.get("cpf")]

    print(f"\nNome: {usuario.get('nome', '-')}")
    print(f"CPF: {formatar_cpf(usuario.get('cpf', ''))}")

    if not registros:
        print(">>> Nenhuma operação registrada até o momento.")
        return usuario, False

    for registro in registros:
        print(formatar_linha_extrato(registro))

    return usuario, False


def depositar(usuario, criptomoedas):
    """Opção 3 - Deposita reais na carteira."""
    cabecalho("DEPÓSITO")

    valor = ler_valor("Valor do depósito (R$): ")
    if valor is None:
        return usuario, False

    usuario["real"] = round(usuario.get("real", 0.0) + valor,
                            CASAS_DECIMAIS_REAL)
    registrar_operacao(usuario, "+", valor, "REAL", 0.0, 0.0)

    print(f">>> Depósito de R$ {brl(valor)} realizado com sucesso.")
    mostrar_saldos(usuario, criptomoedas)

    return usuario, True


def sacar(usuario, criptomoedas):
    """Opção 4 - Saca reais (o saldo não pode ficar negativo)."""
    cabecalho("SAQUE")

    valor = ler_valor("Valor do saque (R$): ")
    if valor is None:
        return usuario, False

    if valor > usuario.get("real", 0.0):
        print(f">>> Saldo insuficiente. "
              f"Disponível: R$ {brl(usuario.get('real', 0.0))}.")
        return usuario, False

    usuario["real"] = round(usuario["real"] - valor, CASAS_DECIMAIS_REAL)
    registrar_operacao(usuario, "-", valor, "REAL", 0.0, 0.0)

    print(f">>> Saque de R$ {brl(valor)} realizado com sucesso.")
    mostrar_saldos(usuario, criptomoedas)

    return usuario, True


def comprar(usuario, criptomoedas):
    """Opção 5 - Compra criptomoeda informando a QUANTIDADE desejada.

    Valor da operação = quantidade x cotação
    Taxa de compra    = valor x taxa_compra
    Total debitado    = valor + taxa
    """
    cabecalho("COMPRA DE CRIPTOMOEDAS")

    if not confirmar_senha(usuario):
        return usuario, False

    mostrar_cotacoes(criptomoedas)

    cripto = escolher_criptomoeda(criptomoedas)
    if cripto is None:
        return usuario, False

    ticker = cripto["ticker"]
    print(f"Saldo em reais disponível: R$ {brl(usuario.get('real', 0.0))}")

    quantidade = ler_valor(f"Quantidade de {ticker} que deseja comprar: ")
    if quantidade is None:
        return usuario, False

    valor = quantidade * cripto["cotacao"]
    taxa = valor * cripto["taxa_compra"]
    total = valor + taxa

    if total > usuario.get("real", 0.0):
        print(f">>> Saldo insuficiente. Necessário R$ {brl(total)} "
              f"(R$ {brl(valor)} + R$ {brl(taxa)} de taxa). "
              f"Disponível: R$ {brl(usuario.get('real', 0.0))}.")
        return usuario, False

    usuario["real"] = round(usuario["real"] - total, CASAS_DECIMAIS_REAL)
    usuario[ticker] = round(usuario.get(ticker, 0.0) + quantidade,
                            CASAS_DECIMAIS_CRIPTO)

    registrar_operacao(usuario, "+", valor, ticker,
                       cripto["cotacao"], cripto["taxa_compra"])

    print(f"\n>>> Compra realizada: {fmt_cripto(quantidade)} {ticker} "
          f"a R$ {brl(cripto['cotacao'])} cada.")
    print(f"    Valor: R$ {brl(valor)} "
          f"| Taxa ({cripto['taxa_compra'] * 100:.1f}%): R$ {brl(taxa)} "
          f"| Total debitado: R$ {brl(total)}")
    mostrar_saldos(usuario, criptomoedas)

    return usuario, True


def vender(usuario, criptomoedas):
    """Opção 6 - Vende criptomoeda informando a QUANTIDADE desejada.

    Valor bruto     = quantidade x cotação
    Taxa de venda   = valor bruto x taxa_venda
    Valor creditado = valor bruto - taxa
    """
    cabecalho("VENDA DE CRIPTOMOEDAS")

    if not confirmar_senha(usuario):
        return usuario, False

    mostrar_cotacoes(criptomoedas)

    cripto = escolher_criptomoeda(criptomoedas)
    if cripto is None:
        return usuario, False

    ticker = cripto["ticker"]
    disponivel = usuario.get(ticker, 0.0)
    print(f"Você possui {fmt_cripto(disponivel)} {ticker}.")

    quantidade = ler_valor(f"Quantidade de {ticker} que deseja vender: ")
    if quantidade is None:
        return usuario, False

    if quantidade > disponivel:
        print(f">>> Quantidade insuficiente. Disponível: "
              f"{fmt_cripto(disponivel)} {ticker}.")
        return usuario, False

    valor = quantidade * cripto["cotacao"]
    taxa = valor * cripto["taxa_venda"]
    liquido = valor - taxa

    usuario[ticker] = round(disponivel - quantidade,
                            CASAS_DECIMAIS_CRIPTO)
    usuario["real"] = round(usuario.get("real", 0.0) + liquido,
                            CASAS_DECIMAIS_REAL)

    registrar_operacao(usuario, "-", valor, ticker,
                       cripto["cotacao"], cripto["taxa_venda"])

    print(f"\n>>> Venda realizada: {fmt_cripto(quantidade)} {ticker} "
          f"a R$ {brl(cripto['cotacao'])} cada.")
    print(f"    Bruto: R$ {brl(valor)} "
          f"| Taxa ({cripto['taxa_venda'] * 100:.1f}%): R$ {brl(taxa)} "
          f"| Creditado: R$ {brl(liquido)}")
    mostrar_saldos(usuario, criptomoedas)

    return usuario, True


def atualizar_cotacao(criptomoedas):
    """Opção 7 - Varia cada cotação entre -5% e +5% e grava no arquivo."""
    cabecalho("ATUALIZAÇÃO DE COTAÇÕES")

    if not criptomoedas:
        print(">>> Nenhuma criptomoeda cadastrada.")
        return

    for cripto in criptomoedas:
        variacao = random.uniform(-VARIACAO_MAXIMA, VARIACAO_MAXIMA)
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
    """Laço principal do menu, executado até a opção 8 (Sair)."""
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
    """Inicializa os dados, controla o login e encerra o programa."""
    # python Projeto.py reset -> apaga os .txt antes de começar
    if len(sys.argv) > 1 and sys.argv[1].strip().lower() == "reset":
        resetar_dados()
        print()

    criar_dados_iniciais()

    usuarios = carregar_usuarios()
    criptomoedas = carregar_criptomoedas()

    # Se o arquivo de criptomoedas estiver vazio, recria o padrão
    if not criptomoedas:
        criptomoedas = [dict(c) for c in CRIPTOMOEDAS_PADRAO]
        salvar_criptomoedas(criptomoedas)

    # Garante que todo investidor tenha as chaves das criptomoedas
    for usuario in usuarios:
        sincronizar_carteira(usuario, criptomoedas)

    print("=" * 60)
    print("           EXCHANGE DE CRIPTOMOEDAS - v2.2")
    print("=" * 60)
    print(f"Acesso de teste -> CPF: {CPF_PADRAO} | Senha: {SENHA_PADRAO}")

    while True:
        usuario = efetuar_login(usuarios)

        if usuario is not None:
            menu_investidor(usuarios, criptomoedas, usuario)
            break

        resposta = input("\nDeseja tentar o login novamente? (s/n): ")
        if resposta.strip().lower() != "s":
            print("\nEncerrando a Exchange. Até logo!")
            break


if __name__ == "__main__":
    main()