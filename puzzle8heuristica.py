import pygame
import time
from collections import deque

# Definição de cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (100, 100, 255)
GREEN = (100, 255, 100)
RED = (255, 100, 100)

# Configuração da tela do Pygame
WIDTH, HEIGHT = 400, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulador do 8-Puzzle - DFS")

# Estado inicial e objetivo
estado_inicial =   [[1, 2, 3],
                    [4, 0, 6],
                    [7, 5, 8]]

estado_objetivo =  [[0, 1, 2],
                    [3, 4, 5], 
                    [6, 7, 8]]

# Movimentos possíveis
movimentos = {
    "↑": (-1, 0),
    "↓": (1, 0),
    "←": (0, -1),
    "→": (0, 1)
}

acoes = {
    "W": lambda e: mover(e, "↑"),
    "S": lambda e: mover(e, "↓"),
    "A": lambda e: mover(e, "←"),
    "D": lambda e: mover(e, "→")
}

# Função para encontrar a posição do zero (espaço vazio)
def encontrar_zero(estado):
    for i in range(3):
        for j in range(3):
            if estado[i][j] == 0:
                return i, j

# Função para mover o zero
def mover(estado, direcao):
    i, j = encontrar_zero(estado)
    di, dj = movimentos[direcao]
    novo_i, novo_j = i + di, j + dj

    if 0 <= novo_i < 3 and 0 <= novo_j < 3:
        novo_estado = [linha[:] for linha in estado]  # Copia o tabuleiro
        novo_estado[i][j], novo_estado[novo_i][novo_j] = novo_estado[novo_i][novo_j], novo_estado[i][j]
        return novo_estado

    return None  # Movimento inválido

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
#start buscas

def dfs(inicio, objetivo):
    pilha = [[inicio]]  
    visitados = set([inicio]) 
    limite_profundidade = 30  
    
    while pilha:
        caminho = pilha.pop()  
        estado_atual = caminho[-1]
        
        if estado_atual == objetivo:
            return caminho  
            
        if len(caminho) <= limite_profundidade:
            for acao, transicao in acoes.items():
                estado_lista = [list(linha) for linha in estado_atual]
                novo_estado = transicao(estado_lista)
                
                if novo_estado:  
                    novo_estado_tupla = tuple(tuple(linha) for linha in novo_estado)
                    
                    if novo_estado_tupla not in visitados:
                        visitados.add(novo_estado_tupla)
                        novo_caminho = caminho + [novo_estado_tupla]
                        pilha.append(novo_caminho)
    
    return None 

def bfs(inicio, objetivo):
    fila = deque([[inicio]])
    visitados = set()
    
    while fila:
        caminho = fila.popleft()
        estado_atual = caminho[-1]  

        if estado_atual == objetivo:
            return caminho 

        if estado_atual not in visitados:
            visitados.add(estado_atual)

            for acao, transicao in acoes.items():
                estado_lista = [list(linha) for linha in estado_atual]
                novo_estado = transicao(estado_lista)

                if novo_estado and tuple(tuple(linha) for linha in novo_estado) not in visitados:
                    novo_caminho = caminho + [tuple(tuple(linha) for linha in novo_estado)]
                    fila.append(novo_caminho)

    return None 


def heuristica_quantos_faltam(estado, objetivo):
    distancia_total = 0

    for i in range(3):
        for j in range(3):
            if estado[i][j] != 0: 
                valor = estado[i][j]
                objetivo_i, objetivo_j = valor // 3, valor % 3
                distancia = abs(i - objetivo_i) + abs(j - objetivo_j)
                distancia_total += distancia
                
    return distancia_total


def busca_heuristica(inicio, objetivo):
    fila = [[inicio]]
    visitados = set([inicio])
    limite_estados = 10000  # pra evitar llops infitoso
    estados_expandidos = 0
    
    while fila and estados_expandidos < limite_estados:
        caminho = fila.pop(0)
        estado_atual = caminho[-1]
        
        if estado_atual == objetivo:
            return caminho
            
        estados_expandidos += 1
        proximos_estados = []
        
        for acao, transicao in acoes.items():
            estado_lista = [list(linha) for linha in estado_atual]
            novo_estado = transicao(estado_lista)
            
            if novo_estado:
                novo_estado_tupla = tuple(tuple(linha) for linha in novo_estado)
                
                if novo_estado_tupla not in visitados:
                    visitados.add(novo_estado_tupla)
                    
                    valor_heuristico = heuristica_quantos_faltam(novo_estado_tupla, objetivo)
                    
                    proximos_estados.append((valor_heuristico, novo_caminho := caminho + [novo_estado_tupla]))
        
        proximos_estados.sort(key=lambda x: x[0], reverse=True)
        
        for _, novo_caminho in proximos_estados:
            fila.insert(0, novo_caminho)  
    
    return None


#absurdo isso aqui
def a_estrela(inicio, objetivo):
    fila = [[inicio]]
    visitados = set([inicio])
    limite_estados = 50000
    estados_expandidos = 0
    
    while fila and estados_expandidos < limite_estados:
        candidatos = []
        for caminho in fila:
            #soma das heuristicas igual fizemos em aula
            g = len(caminho) - 1
            h = heuristica_quantos_faltam(caminho[-1], objetivo)
            f = g + h
            candidatos.append((f, caminho))
        
        candidatos.sort(key=lambda x: x[0])
        
        _, caminho = candidatos[0]
        fila.remove(caminho)
        
        estado_atual = caminho[-1]
        
        if estado_atual == objetivo:
            return caminho
            
        estados_expandidos += 1
        
        for acao, transicao in acoes.items():
            estado_lista = [list(linha) for linha in estado_atual]
            novo_estado = transicao(estado_lista)
            
            if novo_estado:
                novo_estado_tupla = tuple(tuple(linha) for linha in novo_estado)
                
                if novo_estado_tupla not in visitados:
                    visitados.add(novo_estado_tupla)
                    novo_caminho = caminho + [novo_estado_tupla]
                    fila.append(novo_caminho)
    
    return []

#end buscas
#----------------------------------------------------------------------------------------------------------------------------------------------------------------
#start tabulerio 

def desenhar_tabuleiro(estado):
    screen.fill(WHITE)
    tam_celula = WIDTH // 3

    for i in range(3):
        for j in range(3):
            num = estado[i][j]
            rect = pygame.Rect(j * tam_celula, i * tam_celula, tam_celula, tam_celula)
            pygame.draw.rect(screen, BLUE if num == 0 else GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 3)

            if num != 0:
                font = pygame.font.Font(None, 60)
                text = font.render(str(num), True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

    pygame.display.flip()

# Loop de animação da solução
def executar_simulacao(caminho):
    pygame.init()
    clock = pygame.time.Clock()

    for estado in caminho:
        desenhar_tabuleiro(estado)
        time.sleep(1)
        clock.tick(1)

    time.sleep(2)
    pygame.quit()

#end rtabuleiro
#----------------------------------------------------------------------------------------------------------------------------------------------------------------

estado_inicial = tuple(tuple(state) for state in estado_inicial)
estado_objetivo = tuple(tuple(state) for state in estado_objetivo)

# caminho_solucao = bfs(estado_inicial, estado_objetivo)
# caminho_solucao = dfs(estado_inicial, estado_objetivo)
caminho_solucao = busca_heuristica(estado_inicial, estado_objetivo)
# caminho_solucao = a_estrela(estado_inicial, estado_objetivo)

# Executa a simulação animada do 8-Puzzle com DFS
executar_simulacao(caminho_solucao)
print(len(caminho_solucao))
print(caminho_solucao)
