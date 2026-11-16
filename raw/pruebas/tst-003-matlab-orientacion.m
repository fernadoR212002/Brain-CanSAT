% Prueba de orientación del BNO055 (proyecto PlatformIO: Prueba_MATLAB)
% Trama esperada de la ESP32: t_ms,yaw,roll,pitch,cal_sys,cal_gir,cal_acel,cal_mag
% Ángulos en grados; calibración de 0 (sin calibrar) a 3 (calibrado).

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
figure('Name', 'Caracterización BNO055 - Orientación');

subplot(2,1,1);
h_x = animatedline('Color', 'r', 'LineWidth', 1.5, 'DisplayName', 'Yaw (Z-axis)');
h_y = animatedline('Color', 'g', 'LineWidth', 1.5, 'DisplayName', 'Roll (Y-axis)');
h_z = animatedline('Color', 'b', 'LineWidth', 1.5, 'DisplayName', 'Pitch (X-axis)');
legend; grid on;
title('Dinámica del GY-BNO055 en Tiempo Real');
xlabel('Tiempo (s)'); ylabel('Grados (°)');
ylim([-180 360]);

% Estado de calibración interno del BNO055 (0 a 3)
subplot(2,1,2);
h_cs = animatedline('Color', 'k', 'LineWidth', 1.5, 'DisplayName', 'Sistema');
h_cg = animatedline('Color', 'r', 'LineWidth', 1.5, 'DisplayName', 'Giróscopo');
h_ca = animatedline('Color', 'g', 'LineWidth', 1.5, 'DisplayName', 'Acelerómetro');
h_cm = animatedline('Color', 'b', 'LineWidth', 1.5, 'DisplayName', 'Magnetómetro');
legend('Location', 'southeast'); grid on;
title('Estado de calibración (3 = calibrado)');
xlabel('Tiempo (s)'); ylabel('Nivel');
ylim([-0.2 3.2]); yticks(0:3);

disp("Recibiendo telemetría... Mueve el sensor.");

datos = nan(N, 8); % Columnas: t (s), yaw, roll, pitch, cal_sys, cal_gir, cal_acel, cal_mag
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

    % Si la trama es válida (8 números reales), guardar y graficar
    if numel(valores) == 8 && ~any(isnan(valores))
        if isnan(t0), t0 = valores(1); end
        t = (valores(1) - t0) / 1000; % ms -> s desde la primera muestra

        k = k + 1;
        datos(k, :) = [t, valores(2:8)'];

        addpoints(h_x, t, valores(2));
        addpoints(h_y, t, valores(3));
        addpoints(h_z, t, valores(4));
        addpoints(h_cs, t, valores(5));
        addpoints(h_cg, t, valores(6));
        addpoints(h_ca, t, valores(7));
        addpoints(h_cm, t, valores(8));
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
    fprintf('Media  [yaw roll pitch] = [%8.3f %8.3f %8.3f] grados\n', media);
    fprintf('Desv.  [yaw roll pitch] = [%8.3f %8.3f %8.3f] grados\n', desv);
    fprintf('Calibración final [sis gir acel mag] = [%d %d %d %d]\n', datos(end, 5:8));
    fprintf('Frecuencia de muestreo real = %.2f Hz\n', (k - 1) / (datos(end, 1) - datos(1, 1)));
    % Ojo: la media del yaw no tiene sentido si cruza 0/360°.

    % Guardar los datos en CSV junto a este script
    archivo = "orientacion_" + string(datetime('now', 'Format', 'yyyy-MM-dd_HHmmss')) + ".csv";
    tabla = array2table(datos, 'VariableNames', ...
        {'t_s', 'yaw_deg', 'roll_deg', 'pitch_deg', 'cal_sys', 'cal_gir', 'cal_acel', 'cal_mag'});
    writetable(tabla, archivo);
    disp("Datos guardados en " + archivo);
end
