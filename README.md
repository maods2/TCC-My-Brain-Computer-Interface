# TCC-My-Brain-Computer-Interface

### 1. PROPOSTA

Neste presente Trabalho de Conclusão de Curso, primeiramente é desenvolvido e proposto o projeto de um circuito de Eletroencefalograma (EEG) de baixo custo. Em seguida, sinais cerebrais são registrados e analisados, submetendo-os às principais técnicas de pré-processamento, extração de características e classificação de sinais, existentes na área. Essas técnicas são utilizadas como ferramentas a fim de contornar as dificuldades de se lidar com os sinais de baixa intensidade e com muito ruído. Esse trabalho tem como o objetivo abordar essas principais técnicas trazendo uma interação entre diferentes metodologias, aplicadas a uma ICC de baixo custo e de apenas um canal, explorando os resultados de performance em modo offline.

### 2. METODOLOGIA

#### A. Design de um Circuito EEG de Baixo Custo
Neste presente projeto, devido a intenção de desenvolver uma proposta simples e de fácil desenvolvimento e reprodução quando comparado com outros modelos, foi escolhida a implementação de um circuito de EEG de apenas um canal, com a configuração bipolar, usando eletrodos passivos. Os dois terminais do amplificador de instrumentação são utilizados para aquisição de sinal, em conjunto com os eletrodos, e mais um eletrodo é utilizado para ser a referência da terra virtual do sistema.
![circ logo](/pic/circ.PNG)
O circuito apresenta três estágios de amplificação e quatro estágios de filtragem. No primeiro estágio de amplificação é empregado o amplificador de instrumentação AD620AN, que irá mensurar a diferença de potencial entre dois eletrodos, e por ter a característica de alta rejeição de modo em comum (CMRR), apresentará uma melhor rejeição do ruído da linha de 60 Hz. Entre suas portas 1 e 8 é inserido um resistor de 330Ω, que lhe proporciona um ganho de 150x.
Após o primeiro estágio de amplificação se encontra um capacitor de acoplamento de 1uF, responsável por bloquear sinais de corrente contínua, seguido de um filtro passa altas ativo de 0,1 Hz com um ganho variável de 1 à 4x, que tem a função de filtrar alguns componentes de baixa frequência que estão incorporados no sinal EEG, devido à alguns artefatos. Para o amplificador ativo é utilizado o amplificador operacional CA3140.
No próximo estágio se encontra um filtro passa-baixa RC passivo de 159 Hz. Esta frequência de corte foi escolhida para preservar componentes importantes de atividades cerebrais, que estão dispostas abaixo dos 100 Hz.
Ao sinal de saída do filtro RC, novamente é aplicado um filtro passa-alta ativo de 0,72 Hz com um ganho fixo de 61x, onde o objetivo outra vez é cortar componentes de muito baixa frequência presentes no sistema.
Por último, é aplicado outro filtro passa-baixa passivo RC de 48,2 Hz, dessa vez com objetivo de atenuar principalmente o ruído de linha de 60 Hz.
O circuito completo possui um alto ganho, justificável pela baixa amplitude presente nos sinais de EEG (≅20 microvolts), que varia de 9.150 à 36.600 vezes. A banda de frequências que passa pelo circuito sem ser atenuada, está entre 0,72 Hz e 48,2 Hz. Para que a atividade elétrica cerebral seja posteriormente analisada em um notebook, a saída do circuito analógico é acoplada com uma entrada analógica 0 de um Arduino Uno, para que o microcontrolador Atmega328 converta o sinal de analógico para digital, em seguida enviando os dados para o notebook pela porta serial. No código embarcado no Arduino é empregado um delay de 5 ms, para que assim o sinal seja amostrado com uma frequência de 200 Hz.

#### B. Aquisição de dados




#### C. Pré-processamento, Extração de Características e Classificação
