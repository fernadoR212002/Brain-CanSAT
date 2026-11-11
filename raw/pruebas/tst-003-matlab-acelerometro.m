% Prueba del acelerómetro del BNO055 (proyecto PlatformIO: Prueba_Acelerometro)
% Trama esperada de la ESP32: t_ms,ax,ay,az   (m/s², incluye la gravedad)

% Limpieza de entorno
clear all; close all; clc;

% Configurar la conexión (Verifica tu número de puerto)
puerto = "COM7"; % <-- CAMBIA ESTO A TU PUERTO REAL
baudios = 115200;
N = 5000;        % Muestras a capturar (~250 s a 20 Hz)
g = 9.80665;     % Gravedad estándar (m/s²), solo como referencia

esp32 = serialport(puerto, baudios);
configureTerminator(esp32, "CR/LF");
flush(esp32); % Limpiar datos viejos

% Preparar la ventana de la gráfica
figure('Name', 'Caracterización BNO055 - Acelerómetro');

subplot(2,1,1);
h_x = animatedline('Color', 'r', 'LineWidth', 1.5, 'DisplayName', 'a_x');
h_y = animatedline('Color', 'g', 'LineWidth', 1.5, 'DisplayName', 'a_y');
h_z = animatedline('Color', 'b', 'LineWidth', 1.5, 'DisplayName', 'a_z');
legend; grid on;
title('Aceleración del GY-BNO055 en Tiempo Real');
xlabel('Tiempo (s)'); ylabel('Aceleración (m/s^2)');
ylim([-20 20]);

subplot(2,1,2);
h_n = animatedline('Color', 'k', 'LineWidth', 1.5, 'DisplayName', '|a|');
yline(g, '--m', 'g', 'DisplayName', 'g = 9.81 m/s^2');
legend; grid on;
title('Magnitud de la aceleración (quieto debe dar ≈ g)');
xlabel('Tiempo (s)'); ylabel('|a| (m/s^2)');
ylim([0 20]);

disp("Recibiendo telemetría... Mueve el sensor.");

datos = nan(N, 4); % Columnas: t (s), ax, ay, az
k = 0;
t0 = NaN;

for i = 1:N
    if ~isgraphics(h_x) % Si cierras la ventana, detener el bucle
        break;
    end

    trama = readline(esp32);
    if isempty(trama) % Tiempo de espera agotado
        continue;
    end

    % Omitir mensajes de arranque de la ESP32
    if contains(trama, "boot") || contains(trama, "mode:") || contains(trama, "Error")
        disp(trama);
        continue;
    end

    % Convertir el CSV a números
    valores = str2double(split(trama, ','));

    % Si la trama es válida (4 números reales), guardar y graficar
    if numel(valores) == 4 && ~any(isnan(valores))
        if isnan(t0), t0 = valores(1); end
        t = (valores(1) - t0) / 1000; % ms -> s desde la primera muestra
        a = valores(2:4)';

        k = k + 1;
        datos(k, :) = [t, a];

        addpoints(h_x, t, a(1));
        addpoints(h_y, t, a(2));
        addpoints(h_z, t, a(3));
        addpoints(h_n, t, norm(a));
        drawnow limitrate; % Actualizar gráfica de forma eficiente
    end
end

clear esp32;
datos = datos(1:k, :);
disp("Captura finalizada: " + k + " muestras.");

% Resumen estadístico (útil con el sensor quieto)
if k > 1
    media = mean(datos(:, 2:4));
    desv  = std(datos(:, 2:4));
    fprintf('Media  [ax ay az] = [%8.4f %8.4f %8.4f] m/s^2\n', media);
    fprintf('Desv.  [ax ay az] = [%8.4f %8.4f %8.4f] m/s^2\n', desv);
    fprintf('|a| media = %.4f m/s^2 (g = %.4f)\n', mean(vecnorm(datos(:, 2:4), 2, 2)), g);
    fprintf('Frecuencia de muestreo real = %.2f Hz\n', (k - 1) / (datos(end, 1) - datos(1, 1)));

    % Guardar los datos en CSV junto a este script
    archivo = "acelerometro_" + string(datetime('now', 'Format', 'yyyy-MM-dd_HHmmss')) + ".csv";
    tabla = array2table(datos, 'VariableNames', {'t_s', 'ax_ms2', 'ay_ms2', 'az_ms2'});
    writetable(tabla, archivo);
    disp("Datos guardados en " + archivo);
end
