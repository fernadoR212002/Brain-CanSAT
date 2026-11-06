% servo-prueba-futaba.m — Prueba de banco del servomotor de la cámara (MATLAB).
%
% Lleva el servo a los dos extremos (0 y 180 grados) y luego lo deja en `angulo`.
% Imprime el ancho de pulso que corresponde a ese ángulo.
%
% Parámetros: los da el líder de control (mensaje del 2026-11-05). No vienen de una
% hoja de datos del servo; el rango de pulso 0.6–2.4 ms está por confirmar.
%
% Dependencia: la función servo_futaba vive en el brain de tesis del líder
% (Brain-Thesis/code/EXP-005/servo), fuera de este repositorio. Ajustar addpath
% a la ruta local de cada máquina.
%
% Para moverlo sin volver a correr todo, en la Command Window:
%   angulo = 120; writePosition(s, angulo / recorrido)

clear a s

addpath('/home/angelrevelo/Documents/Brain-Thesis/code/EXP-005/servo')

pulsoMin = 0.6e-3;   % s, pulso para 0 grados
pulsoMax = 2.4e-3;   % s, pulso para el recorrido completo
recorrido = 180;     % grados

angulo = 90;         % grados, posición final

s = servo_futaba(pulsoMin = pulsoMin, pulsoMax = pulsoMax, inicio = 0.5);

writePosition(s, 0);
pause(1.5);
writePosition(s, 1);
pause(1.5);

writePosition(s, min(max(angulo / recorrido, 0), 1));
fprintf('Servo en %.0f grados (pulso de %.2f ms)\n', angulo, ...
    1000 * (pulsoMin + (angulo / recorrido) * (pulsoMax - pulsoMin)));
