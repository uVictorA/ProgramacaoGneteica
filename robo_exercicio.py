import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
import json
import time
import math

# =====================================================================
# PARTE 1: ESTRUTURA DA SIMULAÇÃO (NÃO MODIFICAR)
# Esta parte contém a estrutura básica da simulação, incluindo o ambiente,
# o robô e a visualização. Não é recomendado modificar esta parte.
# =====================================================================

class Ambiente:
    def __init__(self, largura=800, altura=600, num_obstaculos=5, num_recursos=5):
        self.largura = largura
        self.altura = altura
        self.obstaculos = self.gerar_obstaculos(num_obstaculos)
        self.recursos = self.gerar_recursos(num_recursos)
        self.tempo = 0
        self.max_tempo = 1000  # Tempo máximo de simulação
        self.meta = self.gerar_meta()  # Adicionando a meta
        self.meta_atingida = False  # Flag para controlar se a meta foi atingida
    
    def gerar_obstaculos(self, num_obstaculos):
        obstaculos = []
        for _ in range(num_obstaculos):
            x = random.randint(50, self.largura - 50)
            y = random.randint(50, self.altura - 50)
            largura = random.randint(20, 100)
            altura = random.randint(20, 100)
            obstaculos.append({
                'x': x,
                'y': y,
                'largura': largura,
                'altura': altura
            })
        return obstaculos
    
    def gerar_recursos(self, num_recursos):
        recursos = []
        for _ in range(num_recursos):
            x = random.randint(20, self.largura - 20)
            y = random.randint(20, self.altura - 20)
            recursos.append({
                'x': x,
                'y': y,
                'coletado': False
            })
        return recursos
    
    def gerar_meta(self):
        # Gerar a meta em uma posição segura, longe dos obstáculos
        max_tentativas = 100
        margem = 50  # Margem das bordas
        
        for _ in range(max_tentativas):
            x = random.randint(margem, self.largura - margem)
            y = random.randint(margem, self.altura - margem)
            
            # Verificar se a posição está longe o suficiente dos obstáculos
            posicao_segura = True
            for obstaculo in self.obstaculos:
                # Calcular a distância até o obstáculo mais próximo
                dist_x = max(obstaculo['x'] - x, 0, x - (obstaculo['x'] + obstaculo['largura']))
                dist_y = max(obstaculo['y'] - y, 0, y - (obstaculo['y'] + obstaculo['altura']))
                dist = math.hypot(dist_x, dist_y)
                
                if dist < 50:  # 50 pixels de margem extra
                    posicao_segura = False
                    break
            
            if posicao_segura:
                return {
                    'x': x,
                    'y': y,
                    'raio': 30  # Raio da meta
                }
        
        # Se não encontrar uma posição segura, retorna o centro
        return {
            'x': self.largura // 2,
            'y': self.altura // 2,
            'raio': 30
        }
    
    def verificar_colisao(self, x, y, raio):
        # Verificar colisão com as bordas
        if x - raio < 0 or x + raio > self.largura or y - raio < 0 or y + raio > self.altura:
            return True
        
        # Verificar colisão com obstáculos
        for obstaculo in self.obstaculos:
            if (x + raio > obstaculo['x'] and 
                x - raio < obstaculo['x'] + obstaculo['largura'] and
                y + raio > obstaculo['y'] and 
                y - raio < obstaculo['y'] + obstaculo['altura']):
                return True
        
        return False
    
    def verificar_coleta_recursos(self, x, y, raio):
        recursos_coletados = 0
        for recurso in self.recursos:
            if not recurso['coletado']:
                distancia = math.hypot(x - recurso['x'], y - recurso['y'])
                if distancia < raio + 10:  # 10 é o raio do recurso
                    recurso['coletado'] = True
                    recursos_coletados += 1
        return recursos_coletados
    
    def verificar_atingir_meta(self, x, y, raio):
        if not self.meta_atingida:
            distancia = math.hypot(x - self.meta['x'], y - self.meta['y'])
            if distancia < raio + self.meta['raio']:
                self.meta_atingida = True
                return True
        return False
    
    def reset(self):
        self.tempo = 0
        for recurso in self.recursos:
            recurso['coletado'] = False
        self.meta_atingida = False
        return self.get_estado()
    
    def get_estado(self):
        return {
            'tempo': self.tempo,
            'recursos_coletados': sum(1 for r in self.recursos if r['coletado']),
            'recursos_restantes': sum(1 for r in self.recursos if not r['coletado']),
            'meta_atingida': self.meta_atingida
        }
    
    def passo(self):
        self.tempo += 1
        return self.tempo >= self.max_tempo
    
    def posicao_segura(self, raio_robo=15):
        """Encontra uma posição segura para o robô, longe dos obstáculos"""
        max_tentativas = 100
        margem = 50  # Margem das bordas
        
        for _ in range(max_tentativas):
            x = random.randint(margem, self.largura - margem)
            y = random.randint(margem, self.altura - margem)
            
            # Verificar se a posição está longe o suficiente dos obstáculos
            posicao_segura = True
            for obstaculo in self.obstaculos:
                # Calcular a distância até o obstáculo mais próximo
                dist_x = max(obstaculo['x'] - x, 0, x - (obstaculo['x'] + obstaculo['largura']))
                dist_y = max(obstaculo['y'] - y, 0, y - (obstaculo['y'] + obstaculo['altura']))
                dist = math.hypot(dist_x, dist_y)
                
                if dist < raio_robo + 20:  # 20 pixels de margem extra
                    posicao_segura = False
                    break
            
            if posicao_segura:
                return x, y
        
        # Se não encontrar uma posição segura, retorna o centro
        return self.largura // 2, self.altura // 2

class Robo:
    def __init__(self, x, y, raio=15):
        self.x = x
        self.y = y
        self.raio = raio
        self.angulo = 0  # em radianos
        self.velocidade = 0
        self.velocidade_max = 5  # Nova constante para velocidade máxima
        self.energia = 100
        self.recursos_coletados = 0
        self.colisoes = 0
        self.distancia_percorrida = 0
        self.tempo_parado = 0  # Novo: contador de tempo parado
        self.ultima_posicao = (x, y)  # Novo: última posição conhecida
        self.meta_atingida = False  # Novo: flag para controlar se a meta foi atingida
        self.passos_desde_coleta = 0  # Novo atributo
        self.ambiente = None  # Novo atributo para referência ao ambiente
    
    def reset(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.energia = 100
        self.recursos_coletados = 0
        self.colisoes = 0
        self.distancia_percorrida = 0
        self.tempo_parado = 0
        self.ultima_posicao = (x, y)
        self.meta_atingida = False
        self.passos_desde_coleta = 0  # Reset do novo atributo
    
    def mover(self, aceleracao, rotacao, ambiente):
        # Atualizar ângulo
        self.angulo += rotacao
        
        # Verificar se o robô está parado
        distancia_movimento = math.hypot(self.x - self.ultima_posicao[0], self.y - self.ultima_posicao[1])
        if distancia_movimento < 0.1:  # Se moveu menos de 0.1 unidades
            self.tempo_parado += 1
            # Forçar movimento após ficar parado por muito tempo
            if self.tempo_parado > 5:  # Após 5 passos parado
                aceleracao = max(0.2, aceleracao)  # Força aceleração mínima
                rotacao = random.uniform(-0.2, 0.2)  # Pequena rotação aleatória
        else:
            self.tempo_parado = 0
        
        # Atualizar velocidade
        self.velocidade += aceleracao
        self.velocidade = max(0.1, min(5, self.velocidade))  # Velocidade mínima de 0.1
        
        # Calcular nova posição
        novo_x = self.x + self.velocidade * np.cos(self.angulo)
        novo_y = self.y + self.velocidade * np.sin(self.angulo)
        
        # Verificar colisão
        if ambiente.verificar_colisao(novo_x, novo_y, self.raio):
            self.colisoes += 1
            self.velocidade = 0.1  # Mantém velocidade mínima mesmo após colisão
            # Tenta uma direção diferente após colisão
            self.angulo += random.uniform(-np.pi/4, np.pi/4)
        else:
            # Atualizar posição
            self.distancia_percorrida += math.hypot(novo_x - self.x, novo_y - self.y)
            self.x = novo_x
            self.y = novo_y
        
        # Atualizar última posição conhecida
        self.ultima_posicao = (self.x, self.y)
        
        # Verificar coleta de recursos
        recursos_coletados = ambiente.verificar_coleta_recursos(self.x, self.y, self.raio)
        self.recursos_coletados += recursos_coletados
        
        # Verificar se atingiu a meta
        if not self.meta_atingida and ambiente.verificar_atingir_meta(self.x, self.y, self.raio):
            self.meta_atingida = True
            # Recuperar energia ao atingir a meta
            self.energia = min(100, self.energia + 50)
        
        # Consumir energia
        self.energia -= 0.1 + 0.05 * self.velocidade + 0.1 * abs(rotacao)
        self.energia = max(0, self.energia)
        
        # Recuperar energia ao coletar recursos
        if recursos_coletados > 0:
            self.energia = min(100, self.energia + 20 * recursos_coletados)
        
        return self.energia <= 0

    def mover_novo(self, aceleracao, rotacao, ambiente):
        self.velocidade += aceleracao
        self.velocidade = max(min(self.velocidade, self.velocidade_max), -self.velocidade_max)
        
        self.angulo += rotacao
        self.energia -= abs(aceleracao) * 0.1
        self.energia -= 0.01  # Consumo base

        nova_x = self.x + self.velocidade * math.cos(self.angulo)
        nova_y = self.y + self.velocidade * math.sin(self.angulo)
        
        colidiu = False
        for obstaculo in ambiente.obstaculos:
            # Calcular distância até o centro do obstáculo
            centro_x = obstaculo['x'] + obstaculo['largura'] / 2
            centro_y = obstaculo['y'] + obstaculo['altura'] / 2
            distancia = math.hypot(nova_x - centro_x, nova_y - centro_y)
            # Usar a maior dimensão do obstáculo como "raio"
            raio_obstaculo = max(obstaculo['largura'], obstaculo['altura']) / 2
            if distancia < raio_obstaculo + self.raio:
                colidiu = True
                break

        if colidiu:
            self.velocidade = 0
            self.angulo += random.uniform(-math.pi/4, math.pi/4)
            self.tempo_parado += 1
            self.colisoes += 1
        else:
            self.x = nova_x
            self.y = nova_y
            self.tempo_parado = 0
            self.distancia_percorrida += math.hypot(nova_x - self.x, nova_y - self.y)

        if self.tempo_parado > 5:
            self.velocidade = 0.5
            self.angulo += random.uniform(-0.1, 0.1)

        self.passos_desde_coleta += 1

        # Verificar coleta de recursos
        recursos_coletados = ambiente.verificar_coleta_recursos(self.x, self.y, self.raio)
        if recursos_coletados > 0:
            self.passos_desde_coleta = 0
            self.recursos_coletados += recursos_coletados
            self.energia = min(100, self.energia + 20 * recursos_coletados)

        # Verificar se atingiu a meta
        if not self.meta_atingida and ambiente.verificar_atingir_meta(self.x, self.y, self.raio):
            self.meta_atingida = True
            self.energia = min(100, self.energia + 50)

        return self.energia <= 0

    def get_sensores(self, ambiente):
        # Inicializações
        dist_recurso = float('inf')
        recursos_restantes = 0
        soma_vetores_recursos_x = 0
        soma_vetores_recursos_y = 0
        recursos_cone_frontal_count = 0
        
        for recurso in ambiente.recursos:
            if not recurso['coletado']:
                recursos_restantes += 1
                dx = recurso['x'] - self.x
                dy = recurso['y'] - self.y
                dist = math.hypot(dx, dy)
                dist_recurso = min(dist_recurso, dist)
                
                # Soma vetores unitários para recursos
                if dist > 0:
                    soma_vetores_recursos_x += dx / dist
                    soma_vetores_recursos_y += dy / dist
                    
                # Checar se recurso está no cone frontal de ±30°
                angulo_recurso = math.atan2(dy, dx) - self.angulo
                # Normalizar angulo para [-pi, pi]
                while angulo_recurso > math.pi:
                    angulo_recurso -= 2 * math.pi
                while angulo_recurso < -math.pi:
                    angulo_recurso += 2 * math.pi
                if abs(angulo_recurso) <= math.radians(30):
                    recursos_cone_frontal_count += 1
        
        # Proporção de recursos no cone frontal
        recursos_cone_frontal = (recursos_cone_frontal_count / recursos_restantes) if recursos_restantes > 0 else 0

        # Distância até obstáculo mais próximo (usar math.hypot)
        dist_obstaculo = float('inf')
        for obstaculo in ambiente.obstaculos:
            centro_x = obstaculo['x'] + obstaculo['largura'] / 2
            centro_y = obstaculo['y'] + obstaculo['altura'] / 2
            dist = math.hypot(self.x - centro_x, self.y - centro_y)
            dist_obstaculo = min(dist_obstaculo, dist)
        
        # Distância até a meta
        dx_meta = ambiente.meta['x'] - self.x
        dy_meta = ambiente.meta['y'] - self.y
        dist_meta = math.hypot(dx_meta, dy_meta)
        
        # Vetor unitário direção meta
        if dist_meta > 0:
            direcao_meta_x = dx_meta / dist_meta
            direcao_meta_y = dy_meta / dist_meta
        else:
            direcao_meta_x, direcao_meta_y = 0, 0
        
        # Vetor soma direção recursos (normalizado)
        soma_magnitude = math.hypot(soma_vetores_recursos_x, soma_vetores_recursos_y)
        if soma_magnitude > 0:
            direcao_recursos_x = soma_vetores_recursos_x / soma_magnitude
            direcao_recursos_y = soma_vetores_recursos_y / soma_magnitude
        else:
            direcao_recursos_x, direcao_recursos_y = 0, 0
        
        # Ângulo até recurso mais próximo
        angulo_recurso = 0
        if dist_recurso < float('inf'):
            for recurso in ambiente.recursos:
                if not recurso['coletado']:
                    dx = recurso['x'] - self.x
                    dy = recurso['y'] - self.y
                    angulo = math.atan2(dy, dx)
                    angulo_recurso = angulo - self.angulo
                    while angulo_recurso > math.pi:
                        angulo_recurso -= 2 * math.pi
                    while angulo_recurso < -math.pi:
                        angulo_recurso += 2 * math.pi
                    break
        
        # Ângulo até a meta
        angulo_meta = math.atan2(dy_meta, dx_meta) - self.angulo
        while angulo_meta > math.pi:
            angulo_meta -= 2 * math.pi
        while angulo_meta < -math.pi:
            angulo_meta += 2 * math.pi
        
        # Passos desde a última coleta (normalizado, supondo max 100 passos)
        passos_desde_coleta_norm = min(self.passos_desde_coleta / 100, 1.0)
        
        return {
            'dist_recurso': dist_recurso,
            'dist_obstaculo': dist_obstaculo,
            'dist_meta': dist_meta,
            'angulo_recurso': angulo_recurso,
            'angulo_meta': angulo_meta,
            'energia': self.energia,
            'velocidade': self.velocidade,
            'meta_atingida': self.meta_atingida,
            'tempo_parado': self.tempo_parado,
            'recursos_restantes': recursos_restantes,
            'direcao_meta_x': direcao_meta_x,
            'direcao_meta_y': direcao_meta_y,
            'direcao_recursos_x': direcao_recursos_x,
            'direcao_recursos_y': direcao_recursos_y,
            'recursos_cone_frontal': recursos_cone_frontal,
            'passos_desde_coleta': passos_desde_coleta_norm
        }

    def get_sensores_novo(self, ambiente):
        self.ambiente = ambiente  # Armazenar referência ao ambiente
        sensores = {}
        
        # Distância normalizada até a meta
        dx_meta = ambiente.meta['x'] - self.x
        dy_meta = ambiente.meta['y'] - self.y
        distancia_meta = np.hypot(dx_meta, dy_meta) / ambiente.largura
        sensores['distancia_meta'] = distancia_meta
        sensores['direcao_meta_x'] = dx_meta / (np.hypot(dx_meta, dy_meta) + 1e-5)
        sensores['direcao_meta_y'] = dy_meta / (np.hypot(dx_meta, dy_meta) + 1e-5)

        # Vetor de direção para recursos
        recursos_direcao_x, recursos_direcao_y = 0, 0
        recursos_cone_frontal = 0
        recursos_nao_coletados = [r for r in ambiente.recursos if not r['coletado']]
        
        for recurso in recursos_nao_coletados:
            dx = recurso['x'] - self.x
            dy = recurso['y'] - self.y
            dist = np.hypot(dx, dy)
            recursos_direcao_x += dx / (dist + 1e-5)
            recursos_direcao_y += dy / (dist + 1e-5)

            angulo = math.atan2(dy, dx) - self.angulo
            # Normalizar ângulo para [-pi, pi]
            while angulo > math.pi:
                angulo -= 2 * math.pi
            while angulo < -math.pi:
                angulo += 2 * math.pi
            if abs(angulo) < math.pi / 6:  # ±30°
                recursos_cone_frontal += 1

        sensores['direcao_recursos_x'] = recursos_direcao_x
        sensores['direcao_recursos_y'] = recursos_direcao_y
        sensores['recursos_cone_frontal'] = recursos_cone_frontal / (len(recursos_nao_coletados) + 1e-5)
        
        sensores['tempo_parado'] = self.tempo_parado
        sensores['passos_desde_coleta'] = self.passos_desde_coleta / 100.0
        sensores['recursos_restantes'] = len(recursos_nao_coletados)

        return sensores

class Simulador:
    def __init__(self, ambiente, robo, individuo):
        self.ambiente = ambiente
        self.robo = robo
        self.individuo = individuo
        self.frames = []
        
        # Configurar matplotlib para melhor visualização
        plt.style.use('default')  # Usar estilo padrão
        plt.ion()  # Modo interativo
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.ax.set_xlim(0, ambiente.largura)
        self.ax.set_ylim(0, ambiente.altura)
        self.ax.set_title("Simulador de Robô com Programação Genética", fontsize=14)
        self.ax.set_xlabel("X", fontsize=12)
        self.ax.set_ylabel("Y", fontsize=12)
        self.ax.grid(True, linestyle='--', alpha=0.7)
    
    def simular(self):
        self.ambiente.reset()
        # Encontrar uma posição segura para o robô
        x_inicial, y_inicial = self.ambiente.posicao_segura(self.robo.raio)
        self.robo.reset(x_inicial, y_inicial)
        self.frames = []
        
        # Limpar a figura atual
        self.ax.clear()
        self.ax.set_xlim(0, self.ambiente.largura)
        self.ax.set_ylim(0, self.ambiente.altura)
        self.ax.set_title("Simulador de Robô com Programação Genética", fontsize=14)
        self.ax.set_xlabel("X", fontsize=12)
        self.ax.set_ylabel("Y", fontsize=12)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        # Desenhar obstáculos (estáticos)
        for obstaculo in self.ambiente.obstaculos:
            rect = patches.Rectangle(
                (obstaculo['x'], obstaculo['y']),
                obstaculo['largura'],
                obstaculo['altura'],
                linewidth=1,
                edgecolor='black',
                facecolor='#FF9999',  # Vermelho claro
                alpha=0.7
            )
            self.ax.add_patch(rect)
        
        # Desenhar recursos (estáticos)
        for recurso in self.ambiente.recursos:
            if not recurso['coletado']:
                circ = patches.Circle(
                    (recurso['x'], recurso['y']),
                    10,
                    linewidth=1,
                    edgecolor='black',
                    facecolor='#99FF99',  # Verde claro
                    alpha=0.8
                )
                self.ax.add_patch(circ)
        
        # Desenhar a meta
        meta_circ = patches.Circle(
            (self.ambiente.meta['x'], self.ambiente.meta['y']),
            self.ambiente.meta['raio'],
            linewidth=2,
            edgecolor='black',
            facecolor='#FFFF00',  # Amarelo
            alpha=0.8
        )
        self.ax.add_patch(meta_circ)
        
        # Criar objetos para o robô e direção (serão atualizados)
        robo_circ = patches.Circle(
            (self.robo.x, self.robo.y),
            self.robo.raio,
            linewidth=1,
            edgecolor='black',
            facecolor='#9999FF',  # Azul claro
            alpha=0.8
        )
        self.ax.add_patch(robo_circ)
        
        # Criar texto para informações
        info_text = self.ax.text(
            10, self.ambiente.altura - 50,  # Alterado de 10 para 50 para descer a legenda
            "",
            fontsize=12,
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', boxstyle='round,pad=0.5')
        )
        
        # Atualizar a figura
        plt.draw()
        plt.pause(0.01)
        
        try:
            while True:
                # Obter sensores
                sensores = self.robo.get_sensores(self.ambiente)
                
                # Avaliar árvores de decisão
                aceleracao = self.individuo.avaliar(sensores, 'aceleracao')
                rotacao = self.individuo.avaliar(sensores, 'rotacao')
                
                # Limitar valores
                aceleracao = max(-1, min(1, aceleracao))
                rotacao = max(-0.5, min(0.5, rotacao))
                
                # Mover robô
                sem_energia = self.robo.mover(aceleracao, rotacao, self.ambiente)
                
                # Atualizar visualização em tempo real
                self.ax.clear()
                self.ax.set_xlim(0, self.ambiente.largura)
                self.ax.set_ylim(0, self.ambiente.altura)
                self.ax.set_title("Simulador de Robô com Programação Genética", fontsize=14)
                self.ax.set_xlabel("X", fontsize=12)
                self.ax.set_ylabel("Y", fontsize=12)
                self.ax.grid(True, linestyle='--', alpha=0.7)
                
                # Desenhar obstáculos
                for obstaculo in self.ambiente.obstaculos:
                    rect = patches.Rectangle(
                        (obstaculo['x'], obstaculo['y']),
                        obstaculo['largura'],
                        obstaculo['altura'],
                        linewidth=1,
                        edgecolor='black',
                        facecolor='#FF9999',
                        alpha=0.7
                    )
                    self.ax.add_patch(rect)
                
                # Desenhar recursos
                for recurso in self.ambiente.recursos:
                    if not recurso['coletado']:
                        circ = patches.Circle(
                            (recurso['x'], recurso['y']),
                            10,
                            linewidth=1,
                            edgecolor='black',
                            facecolor='#99FF99',
                            alpha=0.8
                        )
                        self.ax.add_patch(circ)
                
                # Desenhar a meta
                meta_circ = patches.Circle(
                    (self.ambiente.meta['x'], self.ambiente.meta['y']),
                    self.ambiente.meta['raio'],
                    linewidth=2,
                    edgecolor='black',
                    facecolor='#FFFF00',  # Amarelo
                    alpha=0.8
                )
                self.ax.add_patch(meta_circ)
                
                # Desenhar robô
                robo_circ = patches.Circle(
                    (self.robo.x, self.robo.y),
                    self.robo.raio,
                    linewidth=1,
                    edgecolor='black',
                    facecolor='#9999FF',
                    alpha=0.8
                )
                self.ax.add_patch(robo_circ)
                
                # Desenhar direção do robô
                direcao_x = self.robo.x + self.robo.raio * np.cos(self.robo.angulo)
                direcao_y = self.robo.y + self.robo.raio * np.sin(self.robo.angulo)
                self.ax.plot([self.robo.x, direcao_x], [self.robo.y, direcao_y], 'r-', linewidth=2)
                
                # Adicionar informações
                info_text = self.ax.text(
                    10, self.ambiente.altura - 50,  # Alterado de 10 para 50 para descer a legenda
                    f"Tempo: {self.ambiente.tempo}\n"
                    f"Recursos: {self.robo.recursos_coletados}\n"
                    f"Energia: {self.robo.energia:.1f}\n"
                    f"Colisões: {self.robo.colisoes}\n"
                    f"Distância: {self.robo.distancia_percorrida:.1f}\n"
                    f"Meta atingida: {'Sim' if self.robo.meta_atingida else 'Não'}",
                    fontsize=12,
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', boxstyle='round,pad=0.5')
                )
                
                # Atualizar a figura
                plt.draw()
                plt.pause(0.05)
                
                # Verificar fim da simulação
                if sem_energia or self.ambiente.passo():
                    break
            
            # Manter a figura aberta até que o usuário a feche
            plt.ioff()
            plt.show()
            
        except KeyboardInterrupt:
            plt.close('all')
        
        return self.frames
    
    def animar(self):
        # Desativar o modo interativo antes de criar a animação
        plt.ioff()
        
        # Criar a animação
        anim = animation.FuncAnimation(
            self.fig, self.atualizar_frame,
            frames=len(self.frames),
            interval=50,
            blit=True,
            repeat=True  # Permitir que a animação repita
        )
        
        # Mostrar a animação e manter a janela aberta
        plt.show(block=True)
    
    def atualizar_frame(self, frame_idx):
        return self.frames[frame_idx]

# =====================================================================
# PARTE 2: ALGORITMO GENÉTICO (PARA O VOCÊ MODIFICAR)
# Esta parte contém a implementação do algoritmo genético.
# Deve modificar os parâmetros e a lógica para melhorar o desempenho.
# =====================================================================

class IndividuoPG:
    def __init__(self, profundidade=3):
        self.profundidade = profundidade
        self.arvore_aceleracao = self.criar_arvore_aleatoria()
        self.arvore_rotacao    = self.criar_arvore_aleatoria()
        self.fitness           = 0
    
    def criar_arvore_aleatoria(self):
        if self.profundidade == 0:
            return self.criar_folha()

        operador = random.choice([
            '+', '-', '*', '/',
            'max', 'min', 'abs',
            'if_positivo', 'if_negativo',
            'and', 'or', 'not',
            'if_then_else','goto_meta'
        ])

        # Para binários simples e max/min
        if operador in ['+', '-', '*', '/', 'max', 'min', 'and', 'or']:
            esquerda = IndividuoPG(self.profundidade - 1).arvore_aceleracao
            direita = IndividuoPG(self.profundidade - 1).arvore_aceleracao
            return {
                'tipo': 'operador',
                'operador': operador,
                'esquerda': esquerda,
                'direita': direita
            }

        # Para unário abs e not
        if operador in ['abs', 'not']:
            return {
                'tipo': 'operador',
                'operador': operador,
                'esquerda': IndividuoPG(self.profundidade - 1).arvore_aceleracao,
                'direita': None
            }

        # Para if_positivo e if_negativo
        if operador in ['if_positivo', 'if_negativo']:
            return {
                'tipo': 'operador',
                'operador': operador,
                'esquerda': IndividuoPG(self.profundidade - 1).arvore_aceleracao,
                'direita': IndividuoPG(self.profundidade - 1).arvore_aceleracao
            }

        # Para o ternário if_then_else
        if operador == 'if_then_else':
            cond = IndividuoPG(self.profundidade - 1).arvore_aceleracao
            then_branch = IndividuoPG(self.profundidade - 1).arvore_aceleracao
            else_branch = IndividuoPG(self.profundidade - 1).arvore_aceleracao
            return {
                'tipo': 'operador',
                'operador': 'if_then_else',
                'esquerda': cond,
                'direita': {
                    'then': then_branch,
                    'else': else_branch
                }
            }
            
        if operador == 'goto_meta':
            # Nós filhos (podem ser ignorados ou usados para afinar intensidade)
            cond = {'tipo':'folha', 'variavel':'recursos_restantes'}
            coleta_sub = IndividuoPG(self.profundidade-1).criar_arvore_aleatoria()
            goto_sub   = {
                'tipo': 'operador',
                'operador': 'goto_meta',
                'esquerda': IndividuoPG(self.profundidade-1).criar_arvore_aleatoria(),
                'direita':  IndividuoPG(self.profundidade-1).criar_arvore_aleatoria()
            }
            return {
                'tipo': 'operador',
                'operador': 'if_then_else',
                'esquerda': cond,
                'direita': {
                    'then': coleta_sub,  # enquanto recursos_restantes > 0
                    'else': goto_sub     # quando recursos_restantes == 0
                }
            }
    
    def criar_folha(self):
        tipo = random.choice([
            'constante',
            'dist_recurso', 'dist_obstaculo', 'dist_meta',
            'angulo_recurso', 'angulo_meta',
            'energia', 'velocidade', 'meta_atingida',
            'tempo_parado', 'recursos_restantes',     # adicionadas
            'direcao_meta_x', 'direcao_meta_y'        # adicionadas
        ])
        if tipo == 'constante':
            return {
                'tipo': 'folha',
                'valor': random.uniform(-5, 5)
            }
        else:
            return {
                'tipo': 'folha',
                'variavel': tipo
            }
    
    def avaliar(self, sensores, tipo='aceleracao'):
        # escolhe qual árvore usar
        arvore = self.arvore_aceleracao if tipo == 'aceleracao' else self.arvore_rotacao
        return self.avaliar_no(arvore, sensores)
    
    def avaliar_no(self, no, sensores):
        # caso base
        if no is None or not isinstance(no, dict) or 'tipo' not in no:
            return 0

        # folha
        if no['tipo'] == 'folha':
            if 'valor' in no:
                return no['valor']
            return sensores[no['variavel']]

        op = no.get('operador')

        # ── if_then_else ──
        if op == 'if_then_else':
            raw = self.avaliar_no(no['esquerda'], sensores)
            cond = raw[0] if isinstance(raw, tuple) else raw
            ramo = no['direita']['then'] if cond > 0 else no['direita']['else']
            return self.avaliar_no(ramo, sensores)

        # ── goto_meta ──
        if op == 'goto_meta':
            # direção unitária até a meta (em x)
            dx = sensores['direcao_meta_x']
            # ângulo até a meta
            ang_meta = sensores['angulo_meta']

            # (opcional) usar os filhos como intensidades
            scale_a = (
                no['esquerda']['valor']
                if isinstance(no.get('esquerda'), dict) and 'valor' in no['esquerda']
                else 1.0
            )
            scale_r = (
                no['direita']['valor']
                if isinstance(no.get('direita'), dict) and 'valor' in no['direita']
                else 1.0
            )

            acel = dx * scale_a
            rot  = ang_meta * scale_r
            return (acel, rot)

        # ── unários ──
        if op == 'abs':
            raw = self.avaliar_no(no['esquerda'], sensores)
            v = raw[0] if isinstance(raw, tuple) else raw
            return abs(v)

        if op == 'not':
            raw = self.avaliar_no(no['esquerda'], sensores)
            v = raw[0] if isinstance(raw, tuple) else raw
            return float(not bool(v))

        # ── condicionais simples ──
        if op in ('if_positivo', 'if_negativo'):
            raw = self.avaliar_no(no['esquerda'], sensores)
            v = raw[0] if isinstance(raw, tuple) else raw
            if op == 'if_positivo':
                return self.avaliar_no(no['direita'], sensores) if v > 0 else 0
            else:
                return self.avaliar_no(no['direita'], sensores) if v < 0 else 0

        # ── binários ──
        esquerda = self.avaliar_no(no['esquerda'], sensores)
        direita = self.avaliar_no(no['direita'], sensores) if no.get('direita') is not None else 0

        if isinstance(esquerda, tuple):
            esquerda = esquerda[0]
        if isinstance(direita, tuple):
            direita = direita[0]

        if op == '+':
            return esquerda + direita
        if op == '-':
            return esquerda - direita
        if op == '*':
            return esquerda * direita
        if op == '/':
            return esquerda / direita if direita != 0 else 0
        if op == 'max':
            return max(esquerda, direita)
        if op == 'min':
            return min(esquerda, direita)
        if op == 'and':
            return float(bool(esquerda) and bool(direita))
        if op == 'or':
            return float(bool(esquerda) or bool(direita))

        # fallback
        return 0
       
   
    def mutacao(self, probabilidade=0.1):
        # PROBABILIDADE DE MUTAÇÃO PARA O ALUNO MODIFICAR
        self.mutacao_no(self.arvore_aceleracao, probabilidade)
        self.mutacao_no(self.arvore_rotacao, probabilidade)
    
    def mutacao_no(self, no, probabilidade):
        # 0) se não houver nó, nada a fazer
        if no is None:
            return

        # 1) mutação do próprio nó
        if random.random() < probabilidade:
            # se for folha, altera valor ou variável
            if no.get('tipo') == 'folha':
                if 'valor' in no:
                    no['valor'] = random.uniform(-5, 5)
                else:
                    no['variavel'] = random.choice([
                        'dist_recurso', 'dist_obstaculo', 'dist_meta',
                        'angulo_recurso', 'angulo_meta',
                        'energia', 'velocidade', 'meta_atingida',
                        'tempo_parado', 'recursos_restantes',
                        'direcao_meta_x', 'direcao_meta_y'
                    ])
            # se for operador simples, troca operador
            elif no.get('tipo') == 'operador':
                no['operador'] = random.choice([
                    '+', '-', '*', '/', 'max', 'min',
                    'abs', 'if_positivo', 'if_negativo'
                ])

        # 2) recursão apenas se for operador
        if no.get('tipo') == 'operador':
            # caso especial: if_then_else tem ramo then/else
            if no['operador'] == 'if_then_else':
                self.mutacao_no(no['esquerda'], probabilidade)
                self.mutacao_no(no['direita']['then'], probabilidade)
                self.mutacao_no(no['direita']['else'], probabilidade)
            else:
                # operadores unários (abs, not) ou binários comuns
                self.mutacao_no(no.get('esquerda'), probabilidade)
                # para unário, direita será None; para goto_meta/binaries, pode haver
                if no.get('direita') is not None:
                    self.mutacao_no(no.get('direita'), probabilidade)
    
    def crossover(self, outro):
        filho = IndividuoPG(self.profundidade)
        # faz subtree crossover em aceleração e rotação
        filho.arvore_aceleracao = self.crossover_no(self.arvore_aceleracao, outro.arvore_aceleracao)
        filho.arvore_rotacao    = self.crossover_no(self.arvore_rotacao,    outro.arvore_rotacao)
        return filho
    
    def crossover_no(self, no1, no2, p_corte: float = 0.1):
        """
        Faz crossover entre duas subárvores no1 e no2:
        1) Com probabilidade p_corte, copia no2 inteiro;
        2) Se qualquer um não for um nó operador válido, devolve cópia de no1 (leaf);
        3) Caso contrário, despacha para unários, ternário ou binários.
        """
        # 1) troca inteira de subárvore
        if random.random() < p_corte:
            return copy.deepcopy(no2)

        # 2) se não for nó operador (ou faltar campos), devolve leaf de no1
        if not (isinstance(no1, dict) and no1.get('tipo') == 'operador'):
            return copy.deepcopy(no1)
        if not (isinstance(no2, dict) and no2.get('tipo') == 'operador'):
            return copy.deepcopy(no1)

        op = no1['operador']

        # 3) operadores unários
        if op in ('abs', 'not'):
            return {
                'tipo': 'operador',
                'operador': op,
                'esquerda':   self.crossover_no(no1.get('esquerda'), no2.get('esquerda'), p_corte),
                'direita':    None
            }

        # 4) ternário if_then_else
        if op == 'if_then_else':
            # extrai com segurança os ramos de no2
            b2 = no2.get('direita') or {}
            then2 = b2.get('then')
            else2 = b2.get('else')
            return {
                'tipo': 'operador',
                'operador': 'if_then_else',
                'esquerda': self.crossover_no(no1.get('esquerda'), no2.get('esquerda'), p_corte),
                'direita':  {
                    'then': self.crossover_no(no1['direita']['then'], then2, p_corte),
                    'else': self.crossover_no(no1['direita']['else'], else2, p_corte)
                }
            }

        # 5) binários comuns (+, -, *, /, max, min, and, or, if_positivo, if_negativo, goto_meta)
        return {
            'tipo': 'operador',
            'operador': op,
            'esquerda':  self.crossover_no(no1.get('esquerda'), no2.get('esquerda'), p_corte),
            'direita':   self.crossover_no(no1.get('direita'),  no2.get('direita'),  p_corte)
        }
    
    def salvar(self, arquivo):
        with open(arquivo, 'w') as f:
            json.dump({
                'arvore_aceleracao': self.arvore_aceleracao,
                'arvore_rotacao': self.arvore_rotacao
            }, f)
    
    @classmethod
    def carregar(cls, arquivo):
        with open(arquivo, 'r') as f:
            dados = json.load(f)
            individuo = cls()
            individuo.arvore_aceleracao = dados['arvore_aceleracao']
            individuo.arvore_rotacao = dados['arvore_rotacao']
            return individuo

class ProgramacaoGenetica:
    def __init__(self, tamanho_populacao=50, profundidade=3):
        # PARÂMETROS PARA O ALUNO MODIFICAR
        self.tamanho_populacao = tamanho_populacao
        self.profundidade = profundidade
        self.populacao = [IndividuoPG(profundidade) for _ in range(tamanho_populacao)]
        self.melhor_individuo = None
        self.melhor_fitness = float('-inf')
        self.historico_fitness = []
    
    def avaliar_populacao(self):
        ambiente = Ambiente()
        robo = Robo(ambiente.largura // 2, ambiente.altura // 2)
        
        for individuo in self.populacao:
            fitness = 0
            
            # Simular 5 tentativas
            for _ in range(5):
                ambiente.reset()
                robo.reset(ambiente.largura // 2, ambiente.altura // 2)
                
                while True:
                    # Obter sensores
                    sensores = robo.get_sensores(ambiente)
                    
                    # Avaliar árvores de decisão
                    aceleracao = individuo.avaliar(sensores, 'aceleracao')
                    rotacao = individuo.avaliar(sensores, 'rotacao')
                    
                    # Limitar valores
                    aceleracao = max(-1, min(1, aceleracao))
                    rotacao = max(-0.5, min(0.5, rotacao))
                    
                    # Mover robô
                    sem_energia = robo.mover(aceleracao, rotacao, ambiente)
                    
                    # Verificar fim da simulação
                    if sem_energia or ambiente.passo():
                        break
                
                # Calcular fitness
                fitness_tentativa = (
                    robo.recursos_coletados * 100 +  # Pontos por recursos coletados
                    robo.distancia_percorrida * 0.1 -  # Pontos por distância percorrida
                    robo.colisoes * 50 -  # Penalidade por colisões
                    (100 - robo.energia) * 0.5  # Penalidade por consumo de energia
                )
                
                # Adicionar pontos extras por atingir a meta
                if robo.meta_atingida:
                    fitness_tentativa += 500  # Pontos extras por atingir a meta
                
                fitness += max(0, fitness_tentativa)
            
            individuo.fitness = fitness / 5  # Média das 5 tentativas
            
            # Atualizar melhor indivíduo
            if individuo.fitness > self.melhor_fitness:
                self.melhor_fitness = individuo.fitness
                self.melhor_individuo = individuo
    
    def selecionar(self):
        # MÉTODO DE SELEÇÃO PARA O ALUNO MODIFICAR
        # Seleção por torneio
        tamanho_torneio = 3  # TAMANHO DO TORNEIO PARA O ALUNO MODIFICAR
        selecionados = []
        
        for _ in range(self.tamanho_populacao):
            torneio = random.sample(self.populacao, tamanho_torneio)
            vencedor = max(torneio, key=lambda x: x.fitness)
            selecionados.append(vencedor)
        
        return selecionados
    
    def evoluir(self, n_geracoes=50):
        # NÚMERO DE GERAÇÕES PARA O ALUNO MODIFICAR
        for geracao in range(n_geracoes):
            print(f"Geração {geracao + 1}/{n_geracoes}")
            
            # Avaliar população
            self.avaliar_populacao()
            
            # Registrar melhor fitness
            self.historico_fitness.append(self.melhor_fitness)
            print(f"Melhor fitness: {self.melhor_fitness:.2f}")
            
            # Selecionar indivíduos
            selecionados = self.selecionar()
            
            # Criar nova população
            nova_populacao = []
            
            # Elitismo - manter o melhor indivíduo
            nova_populacao.append(self.melhor_individuo)
            
            # Preencher o resto da população
            while len(nova_populacao) < self.tamanho_populacao:
                pai1, pai2 = random.sample(selecionados, 2)
                filho = pai1.crossover(pai2)
                filho.mutacao(probabilidade=0.1)  # PROBABILIDADE DE MUTAÇÃO PARA O ALUNO MODIFICAR
                nova_populacao.append(filho)
            
            self.populacao = nova_populacao
        
        return self.melhor_individuo, self.historico_fitness

# =====================================================================
# PARTE 3: EXECUÇÃO DO PROGRAMA (PARA O ALUNO MODIFICAR)
# Esta parte contém a execução do programa e os parâmetros finais.
# =====================================================================

# Executando o algoritmo
if __name__ == "__main__":
    print("Iniciando simulação de robô com programação genética...")
    
    # Criar e treinar o algoritmo genético
    print("Treinando o algoritmo genético...")
    # PARÂMETROS PARA O ALUNO MODIFICAR
    pg = ProgramacaoGenetica(tamanho_populacao=20, profundidade=4)
    melhor_individuo, historico = pg.evoluir(n_geracoes=5)
    
    # Salvar o melhor indivíduo
    print("Salvando o melhor indivíduo...")
    melhor_individuo.salvar('melhor_robo.json')
    
    # Plotar evolução do fitness
    print("Plotando evolução do fitness...")
    plt.figure(figsize=(10, 5))
    plt.plot(historico)
    plt.title('Evolução do Fitness')
    plt.xlabel('Geração')
    plt.ylabel('Fitness')
    plt.savefig('evolucao_fitness_robo.png')
    plt.close()
    
    # Simular o melhor indivíduo
    print("Simulando o melhor indivíduo...")
    ambiente = Ambiente()
    robo = Robo(ambiente.largura // 2, ambiente.altura // 2)
    simulador = Simulador(ambiente, robo, melhor_individuo)
    
    print("Executando simulação em tempo real...")
    print("A simulação será exibida em uma janela separada.")
    print("Pressione Ctrl+C para fechar a janela quando desejar.")
    simulador.simular() 
