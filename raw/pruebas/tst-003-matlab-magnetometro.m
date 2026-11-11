% Prueba del magnetómetro del BNO055 (proyecto PlatformIO: Prueba_Magnetometro)
% Trama esperada de la ESP32: t_ms,mx,my,mz   (µT, sin calibrar)

% Limpieza de entorno
clear all; close all; clc;

% Configurar la conexión (Verifica tu número de puerto)
puerto = "COM7"; % <-- CAMBIA ESTO A TU PUERTO REAL
baudios = 115200;
N = 5000;        % Muestras a capturar (~250 s a 20 Hz)

esp32 = serialport(puerto, baudios);
configureTerminator(esp32, "CR/LF");
flush(esp32); % Limpiar datos viejos

% Preparar la ventana de la gráfica
figure('Name', 'Caracterización BNO055 - Magnetómetro');

subplot(2,2,[1 2]);
h_x = animatedline('Color', 'r', 'LineWidth', 1.5, 'DisplayName', 'm_x');
h_y = animatedline('Color', 'g', 'LineWidth', 1.5, 'DisplayName', 'm_y');
h_z = animatedline('Color', 'b', 'LineWidth', 1.5, 'DisplayName', 'm_z');
h_n = animatedline('Color', 'k', 'LineWidth', 1.5, 'DisplayName', '|B|');
legend; grid on;
title('Campo magnético del GY-BNO055 en Tiempo Real');
xlabel('Tiempo (s)'); ylabel('Campo (\muT)');
ylim([-100 100]);

% Plano horizontal: al girar el sensor plano, los puntos deben trazar un
% círculo. Si el círculo no está centrado en (0,0) hay hierro duro (offset);
% si es una elipse, hay hierro blando.
subplot(2,2,3);
h_xy = animatedline('Color', 'm', 'LineStyle', 'none', 'Marker', '.', 'MarkerSize', 6);
grid on; axis equal;
title('m_x vs m_y (gira el sensor plano)');
xlabel('m_x (\muT)'); ylabel('m_y (\muT)');
xlim([-100 100]); ylim([-100 100]);

% Rumbo magnético sin nivelar (válido solo con el sensor horizontal)
subplot(2,2,4);
h_r = animatedline('Color', [0.85 0.45 0], 'LineWidth', 1.5);
grid on;
title('Rumbo magnético sin calibrar (sensor plano)');
xlabel('Tiempo (s)'); ylabel('Rumbo (°)');
ylim([0 360]);

disp("Recibiendo telemetría... Gira el sensor despacio en todas las direcciones.");

datos = nan(N, 4); % Columnas: t (s), mx, my, mz
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
        m = valores(2:4)';

        k = k + 1;
        datos(k, :) = [t, m];

        rumbo = mod(atan2d(m(2), m(1)), 360);

        addpoints(h_x, t, m(1));
        addpoints(h_y, t, m(2));
        addpoints(h_z, t, m(3));
        addpoints(h_n, t, norm(m));
        addpoints(h_xy, m(1), m(2));
        addpoints(h_r, t, rumbo);
        drawnow limitrate; % Actualizar gráfica de forma eficiente
    end
end

clear esp32;
datos = datos(1:k, :);
disp("Captura finalizada: " + k + " muestras.");

% Resumen estadístico
if k > 1
    M = datos(:, 2:4);
    media = mean(M);
    desv  = std(M);
    fprintf('Media  [mx my mz] = [%8.3f %8.3f %8.3f] uT\n', media);
    fprintf('Desv.  [mx my mz] = [%8.3f %8.3f %8.3f] uT\n', desv);
    fprintf('|B| media = %.3f uT\n', mean(vecnorm(M, 2, 2)));

    % Estimación simple de hierro duro: centro del rango de cada eje.
    % Solo es válida si se giró el sensor en todas las direcciones.
    offset = (max(M) + min(M)) / 2;
    fprintf('Offset de hierro duro estimado [mx my mz] = [%8.3f %8.3f %8.3f] uT\n', offset);
    fprintf('Frecuencia de muestreo real = %.2f Hz\n', (k - 1) / (datos(end, 1) - datos(1, 1)));

    % Guardar los datos en CSV junto a este script
    archivo = "magnetometro_" + string(datetime('now', 'Format', 'yyyy-MM-dd_HHmmss')) + ".csv";
    tabla = array2table(datos, 'VariableNames', {'t_s', 'mx_uT', 'my_uT', 'mz_uT'});
    writetable(tabla, archivo);
    disp("Datos guardados en " + archivo);
end
