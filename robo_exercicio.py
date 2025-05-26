import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
import json
import time
import math
import difflib
import copy

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
        self.max_tempo = 1000
        self.meta = self.gerar_meta()
        self.meta_atingida = False
    
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
                dist = np.sqrt(dist_x**2 + dist_y**2)
                
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
                distancia = np.sqrt((x - recurso['x'])**2 + (y - recurso['y'])**2)
                if distancia < raio + 10:  # 10 é o raio do recurso
                    recurso['coletado'] = True
                    recursos_coletados += 1
        return recursos_coletados
    
    def verificar_atingir_meta(self, x, y, raio):
        if not self.meta_atingida:
            distancia = distancia = np.sqrt((x - self.meta['x'])**2 + (y - self.meta['y'])**2)
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
                dist = dist = np.sqrt(dist_x**2 + dist_y**2)
                
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
        self.angulo = 0
        self.velocidade = 0
        self.energia = 100
        self.recursos_coletados = 0
        self.colisoes = 0
        self.distancia_percorrida = 0
        self.tempo_parado = 0
        self.ultima_posicao = (x, y)
        self.meta_atingida = False
        # Novo: contador de passos desde a última coleta
        self.passos_desde_coleta = 0
    
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
        # Reseta o contador
        self.passos_desde_coleta = 0
    
    def mover(self, aceleracao, rotacao, ambiente):
        # 1) Atualiza ângulo e aceleração forçada se parado
        self.angulo += rotacao
        dx = self.x - self.ultima_posicao[0]
        dy = self.y - self.ultima_posicao[1]
        if math.hypot(dx, dy) < 0.1:
            self.tempo_parado += 1
            if self.tempo_parado > 5:
                aceleracao = max(0.2, aceleracao)
                rotacao   = random.uniform(-0.2, 0.2)
        else:
            self.tempo_parado = 0

        # 2) Atualiza velocidade e calcula novo ponto
        self.velocidade = max(0.1, min(5, self.velocidade + aceleracao))
        novo_x = self.x + self.velocidade * math.cos(self.angulo)
        novo_y = self.y + self.velocidade * math.sin(self.angulo)

        # 3) Testa colisão
        if ambiente.verificar_colisao(novo_x, novo_y, self.raio):
            self.colisoes += 1
            self.velocidade = 0.1

            # ==== LÓGICA DE DESVIO DE OBSTÁCULO OU BORDA ====
            mais_prox = None
            menor_dist = float('inf')
            for obs in ambiente.obstaculos:
                cx = obs['x'] + obs['largura']/2
                cy = obs['y'] + obs['altura']/2
                d = math.hypot(self.x - cx, self.y - cy)
                if d < menor_dist:
                    menor_dist = d
                    mais_prox = (cx, cy)

            if mais_prox is not None and menor_dist < float('inf'):
                cx, cy = mais_prox
                dx_obs = self.x - cx
                dy_obs = self.y - cy
                ang_avoid = math.atan2(dy_obs, dx_obs)
                self.angulo = ang_avoid
            else:
                # colisão de borda: inverte direção e dá um pequeno giro aleatório
                self.angulo += math.pi + random.uniform(-0.3, 0.3)
            # ================================================

        else:
            # sem colisão, efetua o movimento
            self.distancia_percorrida += math.hypot(novo_x - self.x, novo_y - self.y)
            self.x, self.y = novo_x, novo_y

        self.ultima_posicao = (self.x, self.y)

        # 4) Coleta recursos e atualiza energia
        coletados_agora = ambiente.verificar_coleta_recursos(self.x, self.y, self.raio)
        self.recursos_coletados += coletados_agora

        if coletados_agora > 0:
            self.passos_desde_coleta = 0
        else:
            self.passos_desde_coleta += 1

        # 5) Verifica meta e consome/recupera energia
        if not self.meta_atingida and ambiente.verificar_atingir_meta(self.x, self.y, self.raio):
            self.meta_atingida = True
            self.energia = min(100, self.energia + 50)

        self.energia -= 0.1 + 0.05 * self.velocidade + 0.1 * abs(rotacao)
        self.energia = max(0, self.energia)
        if coletados_agora > 0:
            self.energia = min(100, self.energia + 20 * coletados_agora)

        return self.energia <= 0

    
    def get_sensores(self, ambiente):
        # recurso mais próximo
        dist_recurso = float('inf')
        rec_prox = None
        for r in ambiente.recursos:
            if not r['coletado']:
                d = np.hypot(self.x - r['x'], self.y - r['y'])
                if d < dist_recurso:
                    dist_recurso, rec_prox = d, r

        # obstáculo mais próximo
        dist_obst = float('inf')
        for o in ambiente.obstaculos:
            cx = o['x'] + o['largura']/2
            cy = o['y'] + o['altura']/2
            dist_obst = min(dist_obst, np.hypot(self.x - cx, self.y - cy))

        # meta
        dist_meta = np.hypot(self.x - ambiente.meta['x'], self.y - ambiente.meta['y'])

        # ângulos
        if rec_prox:
            dx, dy = rec_prox['x'] - self.x, rec_prox['y'] - self.y
            ang_rec = math.atan2(dy, dx) - self.angulo
        else:
            ang_rec = 0.0
        ang_rec = (ang_rec + math.pi) % (2*math.pi) - math.pi

        dxm = ambiente.meta['x'] - self.x
        dym = ambiente.meta['y'] - self.y
        ang_meta = math.atan2(dym, dxm) - self.angulo
        ang_meta = (ang_meta + math.pi) % (2*math.pi) - math.pi

        recursos_rest = sum(1 for r in ambiente.recursos if not r['coletado'])

        # vetor unitário direção à meta
        norm_m = np.hypot(dxm, dym) or 1.0
        dir_meta_x = dxm / norm_m
        dir_meta_y = dym / norm_m

        sensores = {
            'dist_recurso':        dist_recurso,
            'dist_obstaculo':      dist_obst,
            'dist_meta':           dist_meta,
            'angulo_recurso':      ang_rec,
            'angulo_meta':         ang_meta,
            'energia':             self.energia,
            'velocidade':          self.velocidade,
            'meta_atingida':       float(self.meta_atingida),
            'tempo_parado':        self.tempo_parado,
            'recursos_restantes':  recursos_rest,
            'direcao_meta_x':      dir_meta_x,
            'direcao_meta_y':      dir_meta_y,
        }

        # 1) Soma de vetores direção a todos os recursos não coletados
        sum_dx, sum_dy = 0.0, 0.0
        for r in ambiente.recursos:
            if not r['coletado']:
                dx, dy = r['x'] - self.x, r['y'] - self.y
                dist = np.hypot(dx, dy) or 1.0
                sum_dx += dx / dist
                sum_dy += dy / dist
        mag = np.hypot(sum_dx, sum_dy) or 1.0
        sensores['direcao_recursos_x'] = sum_dx / mag
        sensores['direcao_recursos_y'] = sum_dy / mag

        # 2) Contagem de recursos dentro de um cone frontal ±30°
        count_cone = 0
        for r in ambiente.recursos:
            if not r['coletado']:
                dx, dy = r['x'] - self.x, r['y'] - self.y
                ang = math.atan2(dy, dx) - self.angulo
                ang = (ang + math.pi) % (2*math.pi) - math.pi
                if abs(ang) <= math.radians(30):
                    count_cone += 1
        sensores['recursos_cone_frontal'] = count_cone / max(1, len(ambiente.recursos))

        # 3) Passos desde a última coleta (normalizado pelo tempo máximo)
        sensores['passos_desde_coleta'] = self.passos_desde_coleta / ambiente.max_tempo

        return sensores

class Simulador:
    def __init__(self, ambiente, robo, individuo):
        self.ambiente = ambiente
        self.robo = robo
        self.individuo = individuo
        self.frames = []

        plt.style.use('default')
        plt.ion()
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

        # Configurações iniciais da figura
        self.ax.clear()
        self.ax.set_xlim(0, self.ambiente.largura)
        self.ax.set_ylim(0, self.ambiente.altura)
        self.ax.set_title("Simulador de Robô com Programação Genética", fontsize=14)
        self.ax.set_xlabel("X", fontsize=12)
        self.ax.set_ylabel("Y", fontsize=12)
        self.ax.grid(True, linestyle='--', alpha=0.7)

        # Desenhar estáticos
        for obst in self.ambiente.obstaculos:
            self.ax.add_patch(patches.Rectangle(
                (obst['x'], obst['y']),
                obst['largura'], obst['altura'],
                linewidth=1, edgecolor='black', facecolor='#FF9999', alpha=0.7
            ))
        for rec in self.ambiente.recursos:
            if not rec['coletado']:
                self.ax.add_patch(patches.Circle(
                    (rec['x'], rec['y']), 10,
                    linewidth=1, edgecolor='black', facecolor='#99FF99', alpha=0.8
                ))
        self.ax.add_patch(patches.Circle(
            (self.ambiente.meta['x'], self.ambiente.meta['y']),
            self.ambiente.meta['raio'],
            linewidth=2, edgecolor='black', facecolor='#FFFF00', alpha=0.8
        ))

        # Patch inicial do robô e texto de info
        robo_circ = patches.Circle(
            (self.robo.x, self.robo.y), self.robo.raio,
            linewidth=1, edgecolor='black', facecolor='#9999FF', alpha=0.8
        )
        self.ax.add_patch(robo_circ)
        info_text = self.ax.text(
            10, self.ambiente.altura - 50, "",
            fontsize=12,
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', boxstyle='round,pad=0.5')
        )

        plt.draw()
        plt.pause(0.01)

        try:
            while True:
                # === SENSORING e CONTROLE ===
                sensores = self.robo.get_sensores(self.ambiente)

                if sensores['recursos_restantes'] == 0:
                    # força retorno à meta
                    aceleracao = sensores['direcao_meta_x']
                    rotacao    = sensores['angulo_meta']
                else:
                    # uso normal da árvore genética
                    resultado = self.individuo.avaliar(sensores, 'aceleracao')
                    if isinstance(resultado, tuple):
                        aceleracao, rotacao = resultado
                    else:
                        aceleracao = resultado
                        rotacao    = self.individuo.avaliar(sensores, 'rotacao')

                # Normalização dos comandos
                aceleracao = max(-1, min(1, aceleracao))
                rotacao    = max(-0.5, min(0.5, rotacao))

                # Mover robô e verificar fim por energia
                sem_energia = self.robo.mover(aceleracao, rotacao, self.ambiente)

                # === ATUALIZA VISUALIZAÇÃO ===
                self.ax.clear()
                self.ax.set_xlim(0, self.ambiente.largura)
                self.ax.set_ylim(0, self.ambiente.altura)
                self.ax.set_title("Simulador de Robô com Programação Genética", fontsize=14)
                self.ax.set_xlabel("X", fontsize=12)
                self.ax.set_ylabel("Y", fontsize=12)
                self.ax.grid(True, linestyle='--', alpha=0.7)

                # Desenhar estáticos novamente
                for obst in self.ambiente.obstaculos:
                    self.ax.add_patch(patches.Rectangle(
                        (obst['x'], obst['y']),
                        obst['largura'], obst['altura'],
                        linewidth=1, edgecolor='black', facecolor='#FF9999', alpha=0.7
                    ))
                for rec in self.ambiente.recursos:
                    if not rec['coletado']:
                        self.ax.add_patch(patches.Circle(
                            (rec['x'], rec['y']), 10,
                            linewidth=1, edgecolor='black', facecolor='#99FF99', alpha=0.8
                        ))
                self.ax.add_patch(patches.Circle(
                    (self.ambiente.meta['x'], self.ambiente.meta['y']),
                    self.ambiente.meta['raio'],
                    linewidth=2, edgecolor='black', facecolor='#FFFF00', alpha=0.8
                ))

                # Desenhar robô e direção
                robo_circ = patches.Circle(
                    (self.robo.x, self.robo.y), self.robo.raio,
                    linewidth=1, edgecolor='black', facecolor='#9999FF', alpha=0.8
                )
                self.ax.add_patch(robo_circ)
                direcao_x = self.robo.x + self.robo.raio * np.cos(self.robo.angulo)
                direcao_y = self.robo.y + self.robo.raio * np.sin(self.robo.angulo)
                self.ax.plot([self.robo.x, direcao_x], [self.robo.y, direcao_y], 'r-', linewidth=2)

                # Atualizar texto de info
                info_text = self.ax.text(
                    10, self.ambiente.altura - 50,
                    f"Tempo: {self.ambiente.tempo}\n"
                    f"Recursos: {self.robo.recursos_coletados}\n"
                    f"Energia: {self.robo.energia:.1f}\n"
                    f"Colisões: {self.robo.colisoes}\n"
                    f"Distância: {self.robo.distancia_percorrida:.1f}\n"
                    f"Meta atingida: {'Sim' if self.robo.meta_atingida else 'Não'}",
                    fontsize=12,
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', boxstyle='round,pad=0.5')
                )

                plt.draw()
                plt.pause(0.05)

                # Verificar fim da simulação:
                # - sem energia
                # - tempo esgotado
                # - recursos zerados e meta atingida
                if sem_energia or self.ambiente.passo() or (
                    sensores['recursos_restantes'] == 0 and self.robo.meta_atingida):
                    break

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
       
	
    def selecionar_roleta(self):
        total_fit = sum(ind.fitness for ind in self.populacao)
        selecionados = []
        for _ in range(self.tamanho_populacao):
            pick = random.uniform(0, total_fit)
            acumulado = 0.0
            for ind in self.populacao:
                acumulado += ind.fitness
                if acumulado >= pick:
                    selecionados.append(ind)
                    break
        return selecionados
    
    def selecionar(self):
        if self.metodo_selecao == 'roleta':
            return self.selecionar_roleta()

        # seleção por torneio (padrão)
        tamanho_torneio = 3
        selecionados = []
        for _ in range(self.tamanho_populacao):
            torneio = random.sample(self.populacao, tamanho_torneio)
            vencedor = max(torneio, key=lambda x: x.fitness)
            selecionados.append(vencedor)
        return selecionados
    
    def evoluir(self, n_geracoes: int = 50):
        prob_mut_inicial = 0.1   # taxa inicial de mutação
        k = 0.05                 # fator de decaimento exponencial

        for geracao in range(n_geracoes):
            print(f"Geração {geracao+1}/{n_geracoes}")
            # 1) Avalia população e registra melhor fitness
            self.avaliar_populacao()
            # self.historico_fitness.append(self.melhor_fitness)
            print(f"  Melhor fitness: {self.melhor_fitness:.2f} | "
                  f"Média: {self.media_fitness[-1]:.2f} ±{self.std_fitness[-1]:.2f} | "
                  f"Div: {self.diversidade[-1]:.2f}")

            # 2) Calcula elites (mantém self.elite_size definido no __init__)
            if self.elite_size <= 1:
                elite_count = max(1, int(self.elite_size * self.tamanho_populacao))
            else:
                elite_count = int(self.elite_size)
            elites = sorted(self.populacao, key=lambda ind: ind.fitness, reverse=True)[:elite_count]

            # 3) Seleciona pais (torneio ou roleta)
            pais = self.selecionar()

            # 4) Gera nova população, mantendo elites
            nova_pop = elites.copy()
            while len(nova_pop) < self.tamanho_populacao:
                p1, p2 = random.sample(pais, 2)
                filho = p1.crossover(p2)
                # mutação com taxa adaptativa
                prob_mut = prob_mut_inicial * math.exp(-k * geracao)
                filho.mutacao(probabilidade=prob_mut)
                nova_pop.append(filho)

            self.populacao = nova_pop

        return self.melhor_individuo, self.historico_fitness

    def plotar_estatisticas(self, arquivo_png):

        gens = list(range(1, len(self.media_fitness) + 1))
        plt.figure(figsize=(10,6))

        plt.plot(gens, self.historico_fitness, label='Melhor fitness',       linewidth=2)
        plt.plot(gens, self.media_fitness,   label='Média da população',   linestyle='--')
        plt.fill_between(gens,
                         np.array(self.media_fitness) - np.array(self.std_fitness),
                         np.array(self.media_fitness) + np.array(self.std_fitness),
                         color='gray', alpha=0.2, label='± 1 desvio-padrão')

        plt.plot(gens, self.diversidade,     label='Diversidade média',     linestyle=':')

        plt.title('Evolução do Algoritmo Genético')
        plt.xlabel('Geração')
        plt.ylabel('Valor')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(arquivo_png)
        plt.close()
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
