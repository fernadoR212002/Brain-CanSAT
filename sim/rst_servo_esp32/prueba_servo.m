% prueba_servo.m — Mueve el SG90 sin control: centro, izquierda, derecha, centro.
% Usa el mismo firmware. Antes: cerrar la ventana de rst_servo_vivo (libera el puerto).
PUERTO = "/dev/ttyUSB0";
esp = serialport(PUERTO, 921600, "Timeout", 3);
configureTerminator(esp, "LF");
pause(1.5); flush(esp);
pulsos = [1500 1000 2000 1500 1000 2000 1500];   % µs
for p = pulsos
    writeline(esp, sprintf('P%d', p));
    pause(1);
    flush(esp); l = readline(esp); l = readline(esp);
    v = sscanf(char(l), '%f,%f,%f,%f,%f,%f,%f,%f,%f');
    if numel(v) == 9
        fprintf('pedido %d µs -> el ESP32 está sacando %d µs\n', p, v(9));
    else
        fprintf('pedido %d µs -> sin respuesta del ESP32\n', p);
    end
end
clear esp
disp('Fin. El servo debió ir: centro, izquierda, derecha (dos veces) y centro.');
