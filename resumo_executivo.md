# Resumo executivo - perfis de olhos

## Contexto

- Segmentacao baseada apenas em AL, ACD, WTW, K1, K2
- Base: 1.528 olhos, sem valores ausentes nas 5 variaveis

## Metodo

- Padronizacao por z-score
- KMeans com avaliacao de k entre 2 e 8
- Melhor separacao em k = 2 (silhouette = 0,2866)

## Resultados principais

- Dois perfis claros e interpretaveis
- Cluster 0 (n=740): olho mais curto, camara mais rasa, WTW menor, cornea mais curva
- Cluster 1 (n=788): olho mais longo, camara mais profunda, WTW maior, cornea mais plana

## Complemento (coluna "Correto")

- Cluster 0: S = 69,3% | N = 30,7%
- Cluster 1: S = 72,2% | N = 27,8%
- Frequencias semelhantes, sem influencia na formacao dos grupos

## Implicacoes para o cliente

- Segmentacao pragmatica para comunicacao clinica e operacional
- Base para padronizar protocolos e orientar futuras analises

## Recomendacoes

- Validacao clinica dos perfis com especialistas
- Caso seja necessario mais granularidade, testar k=3 ou k=4
