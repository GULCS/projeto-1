andj = int(input("Digite o ano desejado: "))
porcento = 0.015
salario = 5000 * (1 + porcento)
for i in range(2007, andj + 1):
    porcento =   porcento * 2
    salario *= (1 + porcento)
print("Salário de %d: R$  %.2f"  % andj, salario)
    

    