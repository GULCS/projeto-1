"""
Exchange de Criptomoedas - CCP110 Fundamentos de Algoritmos
Aplicacao console para o investidor comprar e vender criptomoedas.
"""

import autenticacao
import carteira
import cotacao
import persistencia


def exibir_menu():
    print()
    print("=" * 40)
    print("       EXCHANGE DE CRIPTOMOEDAS")
    print("=" * 40)
    print("1. Consultar saldo")
    print("2. Consultar extrato")
    print("3. Depositar")
    print("4. Sacar")
    print("5. Comprar criptomoedas")
    print("6. Vender criptomoedas")
    print("7. Atualizar cotacao")
    print("8. Sair")
    print("=" * 40)


def login(usuarios):
    print()
    print("=" * 40)
    print("              LOGIN")
    print("=" * 40)
    while True:
        cpf = input("CPF (somente numeros): ").strip()
        senha = input("Senha (6 digitos): ").strip()
        ok, resultado = autenticacao.autenticar(usuarios, cpf, senha)
        if ok:
            print(f"\nBem-vindo(a), {resultado['nome']}!")
            return cpf, resultado
        print(resultado)
        print("Tente novamente.\n")


def main():
    usuarios = persistencia.carregar_usuarios()
    criptomoedas = persistencia.carregar_criptomoedas()

    if not usuarios:
        print("Nenhum usuario cadastrado em dados/usuarios.txt")
        return
    if not criptomoedas:
        print("Nenhuma criptomoeda cadastrada em dados/criptomoedas.txt")
        return

    cpf, usuario = login(usuarios)

    while True:
        # Garante referencia atualizada do usuario apos gravacoes
        usuario = usuarios.get(cpf)
        if usuario is None:
            print("Erro: usuario nao encontrado. Encerrando.")
            break

        exibir_menu()
        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            carteira.consultar_saldo(cpf, usuario)
        elif opcao == "2":
            carteira.consultar_extrato(cpf, usuario)
        elif opcao == "3":
            carteira.depositar(cpf, usuario, usuarios)
        elif opcao == "4":
            carteira.sacar(cpf, usuario, usuarios)
        elif opcao == "5":
            carteira.comprar_criptomoeda(cpf, usuario, usuarios, criptomoedas)
        elif opcao == "6":
            carteira.vender_criptomoeda(cpf, usuario, usuarios, criptomoedas)
        elif opcao == "7":
            cotacao.atualizar_cotacoes(criptomoedas)
        elif opcao == "8":
            print("\nEncerrando a exchange. Ate logo!")
            break
        else:
            print("Opcao invalida. Escolha de 1 a 8.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperacao cancelada pelo usuario. Ate logo!")
    except Exception as erro:
        print(f"\nErro inesperado: {erro}")