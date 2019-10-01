matriz_teste = []
matriz_teste1 = [1,2,3,4]
matriz_teste2 = [4,5,6,7,8,1,2]
for i in matriz_teste1:
	for j in matriz_teste2:
		if i==j:
			matriz_teste.append(j)
print(matriz_teste)
