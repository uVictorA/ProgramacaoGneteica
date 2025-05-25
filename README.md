🧬 Otimização de Algoritmo Genético para Simulação de Robôs


Este repositório contém a implementação e evolução de um algoritmo genético aplicado à simulação de um robô em ambiente com obstáculos, recursos e metas. O projeto passa por uma série de melhorias funcionais e estruturais que visam aumentar a eficiência da navegação e a inteligência da tomada de decisões do agente simulado.

🔍 Visão Geral
O projeto foi desenvolvido com foco em:

Melhorar a autonomia e a eficiência do robô no ambiente simulado.

Aumentar a expressividade das árvores genéticas.

Reduzir comportamentos improdutivos (loops, travamentos, decisões aleatórias).

Permitir análise visual e estatística da performance do algoritmo ao longo das gerações.

⚙️ Principais Funcionalidades e Alterações
🤖 Controle do Robô
Implementação de lógica de desvio de obstáculos baseada na posição relativa.

Sistema de recuperação de movimento em caso de travamento.

Contador de inatividade para reações adaptativas.

🧠 Sensores Inteligentes
Vetores de direção para recursos e metas.

Detecção de densidade de recursos no campo de visão.

Estatísticas sobre coleta e tempo parado.

🧪 Simulação Aprimorada
Terminação automática ao atingir meta ou esgotar recursos.

Estratégias de fallback para navegação inteligente.

🌳 Árvores Genéticas Expressivas
Novos operadores condicionais (if_then_else), lógicos (and, or, not) e de navegação (goto_meta).

Suporte completo à mutação e recombinação de estruturas condicionais.

📊 Métricas e Análise
Histórico completo de fitness, diversidade genética e variância.

Plotagem de gráficos para visualização da convergência e desempenho.

📈 Estratégias Evolutivas
Seleção por torneio ou roleta.

Elitismo configurável.

Mutação com taxa adaptativa.

Avaliação com recompensas densificadas (shaping).
