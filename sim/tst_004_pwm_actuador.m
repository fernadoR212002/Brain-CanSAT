% tst_004_pwm_actuador.m — TST-004, parte de simulación: ¿la salida PWM del ESP32 al actuador de la
% cámara da o no da para C8 (|psi_c - psi_ref| < 10°)?
%
% Nota: Pruebas/tst-004-salida-pwm-actuador.md · Diseño del lazo: Control/diseno-estabilizacion-camara.md
% Réplica independiente en Python (Codex): sim/tst-004-pwm-actuador.py
%
% Compara los dos actuadores posibles, con los supuestos S1 a S4 de la nota de diseño:
%   B) Motor DC + puente H con el RST L3, en Simulink (sim/lazo_camara_l3.slx). El PWM es un ciclo
%      útil d = u/Vbat. Se varían los bits del ciclo útil, la zona muerta del motor (con y sin
%      compensación en el firmware) y una batería descargada que el firmware no mide.
%   A) Servo de hobby de posición (Futaba 180°, pulso de 0,6 a 2,4 ms, tramas de 50 Hz) con L0, en
%      código MATLAB. El PWM es una POSICIÓN y el servo cierra su propio lazo: el RST no aplica.
%      Modelo del servo igual al de sim/diseno-estabilizacion-camara.py (velocidad K·error, limitada,
%      con banda muerta).
% Además escribe la tabla de resolución del PWM del ESP32 (periférico LEDC).
%
% Todos los parámetros son ILUSTRATIVOS (Sin fuente en raw/): ni el motor ni el servo se han medido,
% y la documentación del LEDC de Espressif no está en raw/.
%
% Se corre desde la raíz del repo:  matlab -batch "run('sim/tst_004_pwm_actuador.m')"
% Necesita sim/lazo_camara_l3.slx con el bloque «ACTUADOR PWM» (lo arma sim/simulink_lazo_camara_l3.m).
%
% Escribe: derivados/tst-004-pwm-resolucion.csv, derivados/tst-004-pwm-actuador-metricas.csv y
%          salida/figuras/tst-004-pwm-actuador.png

raiz = fileparts(fileparts(mfilename('fullpath')));
if isempty(raiz), raiz = pwd; end
addpath(fullfile(raiz, 'sim'));
solo_parametros = true;                                     % parámetros, RST y referencia, sin simular
run(fullfile(raiz, 'sim', 'simulink_lazo_camara_l3.m'));
mdl = 'lazo_camara_l3';

%% ------------------------------------------------------------ parámetros del PWM
F_APB     = 80e6;     % reloj del LEDC [Hz] — Sin fuente en raw/: documentación de Espressif
BITS_LEDC = 20;       % bits máximos del LEDC del ESP32 clásico — Sin fuente en raw/ (el ESP32-S3 tiene menos)
F_SERVO   = 50;       % tramas del servo de hobby [Hz]
PULSO_MIN = 0.6e-3;   % s, pulso para -90° (0° mecánicos) — dado por el líder, sin hoja de datos
PULSO_MAX = 2.4e-3;   % s, pulso para +90° (180° mecánicos)
PULSO_C   = (PULSO_MIN + PULSO_MAX)/2;
LIM_SRV   = 90*D2R;   % recorrido del servo: ±90° alrededor del centro
K_SRV     = 40;       % ganancia del lazo interno del servo [1/s] (la de diseno-estabilizacion-camara.py)
VBAT_NOM  = 7.4;      % V — Sin fuente en raw/: 2S 18650 nominal

%% ------------------------------------------------------------ 1. resolución del PWM del ESP32
us_grado = 1e6*(PULSO_MAX - PULSO_MIN)/180;                 % 10 µs por grado
res = {};
for N = [8 10 12 14 16]
    tick = 1e6/F_SERVO/2^N;
    res(end+1, :) = {'servo', F_SERVO, N, min(BITS_LEDC, floor(log2(F_APB/F_SERVO))), tick, tick/us_grado, NaN}; %#ok<SAGROW>
end
for c = [1e3 8; 20e3 8; 20e3 10; 20e3 11]'
    res(end+1, :) = {'motor', c(1), c(2), min(BITS_LEDC, floor(log2(F_APB/c(1)))), 1e6/c(1)/2^c(2), NaN, ...
                     1000*VBAT_NOM/2^c(2)}; %#ok<SAGROW>
end
tres = cell2table(res, 'VariableNames', {'actuador', 'f_pwm_Hz', 'bits', 'bits_max', 'tick_us', ...
    'grados_por_tick', 'paso_mV'});
writetable(tres, fullfile(raiz, 'derivados', 'tst-004-pwm-resolucion.csv'));
fprintf('\nResolución del PWM (LEDC a %.0f MHz; servo de %.0f µs por grado; batería de %.1f V)\n', ...
        F_APB/1e6, us_grado, VBAT_NOM);
disp(tres);

%% ------------------------------------------------------------ casos
% Compensación de zona muerta en el firmware: u_c = u + DZ_HAT·sign(u), antes del ciclo útil.
%        caso  nombre                                     bits  zona muerta [V]  compensa [V]  Vbat real  Vbat firmware
casosB = {'B0', 'ideal',                                   Inf,  0,    0,    7.4, 7.4;
          'B1', '8 bits (analogWrite por defecto)',          8,  0,    0,    7.4, 7.4;
          'B2', '10 bits',                                  10,  0,    0,    7.4, 7.4;
          'B3', '11 bits a 20 kHz',                         11,  0,    0,    7.4, 7.4;
          'B4', '11 bits + zona muerta 0,3 V',              11,  0.3,  0,    7.4, 7.4;
          'B5', '11 bits + zona muerta 0,6 V',              11,  0.6,  0,    7.4, 7.4;
          'B6', '11 bits, batería 6,4 V sin medir',         11,  0,    0,    6.4, 7.4;
          'B7', 'zona muerta 0,6 V compensada con 0,5 V',   11,  0.6,  0.5,  7.4, 7.4;
          'B8', 'zona muerta 0,6 V compensada con 0,7 V',   11,  0.6,  0.7,  7.4, 7.4};
%        caso  nombre                                bits  vel. máx [°/s]  banda muerta [°]
casosA = {'A0', 'servo 16 bits, 600 °/s, 0,5°',        16,  600, 0.5;
          'A1', 'servo 8 bits, 600 °/s, 0,5°',          8,  600, 0.5;
          'A2', 'servo 16 bits, 260 °/s, 2° (lento)',  16,  260, 2.0};

load_system(fullfile(raiz, 'sim', [mdl '.slx']));
if isempty(find_system(mdl, 'SearchDepth', 1, 'Regexp', 'on', 'Name', '^ACTUADOR PWM'))
    error('sim/%s.slx no tiene el bloque ACTUADOR PWM: correr antes sim/simulink_lazo_camara_l3.m', mdl);
end

prm = struct('T', T, 'NSUB', NSUB, 'TF', TF, 'D2R', D2R, 'R2D', R2D, 'bias_g', bias_g, 'sig_g', sig_g, ...
           'q_g', q_g, 'sig_m', sig_m, 'l1', l1, 'l2', l2, 'ref', ref_data(:, 2), 't', t, 'dt', dt, ...
           'F_SERVO', F_SERVO, 'PULSO_C', PULSO_C, 'MEDIO', (PULSO_MAX - PULSO_MIN)/2, ...
           'LIM', LIM_SRV, 'K', K_SRV);

filas = {};  traza = struct();
escenarios = {'S1', 'S2'};
for n = 1:2
    esc = escenarios{n};
    [psib_data, wb_data, ab_data] = perfil_cuerpo(esc, t, dt, D2R);
    psi0 = psib_data(1, 2) + 1.5*D2R;  wb0 = wb_data(1, 2);  psib0 = psib_data(1, 2);
    % --- B: motor + puente H con el RST L3 (Simulink)
    for c = 1:size(casosB, 1)
        [cs, nom, nb, udz, dzh, vb, vbh] = casosB{c, :};
        PWM_BITS = nb;  U_DZ = udz;  DZ_HAT = dzh;  VBAT = vb;  VBAT_HAT = vbh;   % el modelo los lee del workspace
        fprintf('Simulando %s %s (%s)...\n', esc, cs, nom);
        out = sim(mdl);
        tt = out.e_deg.Time;  e = squeeze(out.e_deg.Data);  ec = squeeze(out.ec_deg.Data);
        u = squeeze(out.u_V.Data);  uap = squeeze(out.u_pwm_V.Data);
        sat = 100*mean(abs(u(tt >= 5)) >= UMAX - 1e-9);
        met = metricas(tt, e, ec, u, uap, sat);
        filas(end+1, :) = [{'motor_rst_l3', cs, nom, esc, nb, udz, dzh, vb, vbh, NaN, NaN}, num2cell(met)]; %#ok<SAGROW>
        traza.(esc).(cs) = struct('t', tt, 'e', e, 'u', u, 'uap', uap);
    end
    % --- A: servo de hobby con L0 (código MATLAB)
    for c = 1:size(casosA, 1)
        [cs, nom, nb, vmax, db] = casosA{c, :};
        fprintf('Simulando %s %s (%s)...\n', esc, cs, nom);
        [tt, e, ec, tope] = sim_servo(psib_data(:, 2), wb_data(:, 2), nb, vmax*D2R, db*D2R, prm);
        met = metricas(tt, e, ec, nan(size(tt)), nan(size(tt)), tope);
        filas(end+1, :) = [{'servo_l0', cs, nom, esc, nb, NaN, NaN, NaN, NaN, vmax, db}, num2cell(met)]; %#ok<SAGROW>
        traza.(esc).(cs) = struct('t', tt, 'e', e);
    end
end

tabla = cell2table(filas, 'VariableNames', {'actuador', 'caso', 'descripcion', 'escenario', 'bits', ...
    'dz_V', 'dz_hat_V', 'vbat_V', 'vbat_hat_V', 'rate_max_dps', 'db_deg', 'max_e_deg', 'rms_e_deg', 'viol_pct', ...
    'max_e_ctrl_deg', 'rms_du_mV', 'rms_du_ap_mV', 'u_max_V', 'sat_pct'});
writetable(tabla, fullfile(raiz, 'derivados', 'tst-004-pwm-actuador-metricas.csv'));
fprintf('\nMétricas (t >= 5 s, sin la ventana de 30 a 32 s del giro de C11). C8: máx |e| < 10°\n');
disp(tabla(:, {'actuador', 'caso', 'escenario', 'max_e_deg', 'rms_e_deg', 'viol_pct', 'max_e_ctrl_deg', ...
    'rms_du_ap_mV', 'sat_pct'}));
for k = 1:height(tabla)
    v = 'da';  if tabla.max_e_deg(k) >= 10, v = 'NO da'; end
    fprintf('%-13s %s %s: máx |e| = %6.2f° -> %s\n', tabla.actuador{k}, tabla.caso{k}, tabla.escenario{k}, ...
            tabla.max_e_deg(k), v);
end

%% ------------------------------------------------------------ figura
% Un color fijo por caso en todos los paneles (paleta de referencia); los escenarios, en grises.
azul = [37 125 224]/255;  naranja = [244 114 48]/255;  aqua = [0 184 148]/255;  violeta = [106 76 226]/255;
gris = [0.40 0.40 0.40];  gS1 = [0.30 0.30 0.30];  gS2 = [0.68 0.68 0.68];
col = struct('B0', azul, 'B1', violeta, 'B5', naranja, 'B7', aqua, 'A0', azul, 'A2', naranja);
fig = figure('Name', 'TST-004 · salida PWM al actuador', 'Color', 'w', 'Position', [80 80 1100 800]);
tl = tiledlayout(fig, 2, 2, 'TileSpacing', 'compact', 'Padding', 'compact');
title(tl, 'TST-004 · ¿La salida PWM del ESP32 da para C8? (simulación, supuestos S1 a S4)', 'FontWeight', 'bold');

ax = nexttile(tl, 1);  hold(ax, 'on');
for sp = {{'B0', 'ideal'}, {'B5', 'zona muerta 0,6 V'}, {'B7', 'compensada con 0,5 V'}}
    s = traza.S1.(sp{1}{1});
    plot(ax, s.t, s.e, 'Color', col.(sp{1}{1}), 'LineWidth', 1, 'DisplayName', [sp{1}{1} ' · ' sp{1}{2}]);
end
yline(ax, [-10 10], '--', 'Color', gris, 'HandleVisibility', 'off');
grid(ax, 'on'); ylim(ax, [-30 30]); xlim(ax, [0 TF]); xlabel(ax, 'Tiempo (s)'); ylabel(ax, 'Error de rumbo (°)');
title(ax, 'B · Motor DC con el RST L3 · S1 (sin giro neto)');
legend(ax, 'Location', 'southoutside', 'Orientation', 'horizontal', 'Box', 'off');

ax = nexttile(tl, 2);  hold(ax, 'on');
for sp = {{'B0', 'ideal'}, {'B1', '8 bits'}, {'B5', 'zona muerta 0,6 V'}}
    s = traza.S1.(sp{1}{1});  w = s.t >= 10 & s.t <= 12;
    stairs(ax, s.t(w), s.uap(w), 'Color', col.(sp{1}{1}), 'LineWidth', 1, 'DisplayName', [sp{1}{1} ' · ' sp{1}{2}]);
end
grid(ax, 'on'); xlabel(ax, 'Tiempo (s)'); ylabel(ax, 'Tensión aplicada al motor (V)');
title(ax, 'B · Tensión que entrega el PWM · 2 s de S1');
legend(ax, 'Location', 'southoutside', 'Orientation', 'horizontal', 'Box', 'off');

ax = nexttile(tl, 3);  hold(ax, 'on');
for sp = {{'A0', 'servo 600 °/s'}, {'A2', 'servo 260 °/s, banda de 2°'}}
    s = traza.S1.(sp{1}{1});
    plot(ax, s.t, s.e, 'Color', col.(sp{1}{1}), 'LineWidth', 1, 'DisplayName', [sp{1}{1} ' · ' sp{1}{2}]);
end
yline(ax, [-10 10], '--', 'Color', gris, 'HandleVisibility', 'off');
xline(ax, 30, ':', 'giro de 90°', 'Color', gris, 'HandleVisibility', 'off');
grid(ax, 'on'); xlim(ax, [0 TF]); ylim(ax, [-100 100]); xlabel(ax, 'Tiempo (s)'); ylabel(ax, 'Error de rumbo (°)');
title(ax, 'A · Servo de hobby de 180° con L0 · S1 (sin giro neto)');
legend(ax, 'Location', 'southoutside', 'Orientation', 'horizontal', 'Box', 'off');

ax = nexttile(tl, 4);  hold(ax, 'on');
etq = unique(tabla.caso, 'stable');  nc = numel(etq);
m1 = zeros(nc, 1);  m2 = m1;
for k = 1:nc
    m1(k) = tabla.max_e_deg(strcmp(tabla.caso, etq{k}) & strcmp(tabla.escenario, 'S1'));
    m2(k) = tabla.max_e_deg(strcmp(tabla.caso, etq{k}) & strcmp(tabla.escenario, 'S2'));
end
y = (nc:-1:1)';                                         % el primer caso arriba
b = barh(ax, y, [min(m1, 40) min(m2, 40)], 'grouped', 'EdgeColor', 'none');
b(1).FaceColor = gS1;  b(2).FaceColor = gS2;
for k = find(max(m1, m2) > 40)'                         % barras recortadas: el valor, al lado
    text(ax, 40.8, y(k), sprintf('%.0f° · %.0f°', m1(k), m2(k)), 'FontSize', 8, 'Color', gris);
end
xline(ax, 10, '--', 'C8: 10°', 'Color', gris, 'LabelVerticalAlignment', 'top', ...
      'LabelOrientation', 'horizontal', 'HandleVisibility', 'off');
yticks(ax, 1:nc);  yticklabels(ax, flip(etq));  ylim(ax, [0.4 nc + 0.6]);
grid(ax, 'on'); xlim(ax, [0 52]); xticks(ax, 0:10:40);
xlabel(ax, 'Máximo |error| (°); barras recortadas a 40°');
legend(ax, {'S1', 'S2'}, 'Location', 'southoutside', 'Orientation', 'horizontal', 'Box', 'off');
title(ax, 'Máximo error por caso (B: motor con RST · A: servo)');
exportgraphics(fig, fullfile(raiz, 'salida', 'figuras', 'tst-004-pwm-actuador.png'), 'Resolution', 150);
close_system(mdl, 0);
fprintf('Listo: derivados/tst-004-*.csv y salida/figuras/tst-004-pwm-actuador.png\n');


%% ============================================================ funciones locales
function met = metricas(tt, e, ec, u, uap, sat)
% Mismas métricas que simulink_lazo_camara_l3.m, más el RMS de la tensión aplicada y la saturación.
m = (tt >= 5) & ~((tt >= 30) & (tt < 32));
du = diff(u(tt >= 5));  dua = diff(uap(tt >= 5));
if numel(sat) > 1, sat = 100*mean(sat(tt >= 5)); end
met = [max(abs(e(m))), sqrt(mean(e(m).^2)), 100*mean(abs(e(m)) > 10), max(abs(ec(m))), ...
       1000*sqrt(mean(du.^2)), 1000*sqrt(mean(dua.^2)), max(abs(u(tt >= 5))), sat];
end

function [tt, e, ec, tope] = sim_servo(psib, wb, nbits, vmax, db, p)
% Servo de hobby con L0: theta_cmd = wrap(psi_ref - psi_b estimado), a ±90°, como pulso de
% 1,5 ms ± 0,9 ms con nbits a 50 Hz. Mismos sensores y estimador que el lazo de Simulink.
% tope: la orden pedida pasa de ±90° (el servo está en su tope) en esa muestra.
wrap = @(a) atan2(sin(a), cos(a));
rng(101);
Nk = round(p.TF/p.T);  div = round(1/(p.F_SERVO*p.T));   % 2 muestras del lazo por trama
tick = 1/p.F_SERVO/2^nbits;
tt = zeros(Nk, 1); e = tt; ec = tt; tope = false(Nk, 1);
th = 0; th_cmd = 0; psi_hat = []; b_hat = 0; tope_k = false;
for k = 0:Nk-1
    i0 = k*p.NSUB + 1;  j = max(i0 - p.NSUB, 1);  tk = p.t(i0);
    merr = 1.5*p.D2R + 2*p.D2R*sin(2*pi*0.4*tk);
    w_meas  = wb(j) + p.bias_g + p.sig_g*randn;
    psi_mag = psib(j) + merr + p.sig_m*randn;
    w_meas  = round(w_meas/p.q_g)*p.q_g;
    if isempty(psi_hat), psi_hat = psi_mag; end
    innov   = wrap(psi_mag - psi_hat);
    psi_hat = psi_hat + p.T*(w_meas - b_hat + p.l1*innov);
    b_hat   = b_hat - p.T*p.l2*innov;
    yr = p.ref(i0);
    psic = psib(i0) + th;
    if mod(k, div) == 0                                  % nueva trama de 50 Hz
        c = wrap(yr - psi_hat);  tope_k = abs(c) > p.LIM;
        pul = p.PULSO_C + min(max(c, -p.LIM), p.LIM)/p.LIM*p.MEDIO;
        pul = round(pul/tick)*tick;                      % ancho de pulso con nbits
        th_cmd = (pul - p.PULSO_C)/p.MEDIO*p.LIM;
    end
    tt(k+1) = tk;  e(k+1) = wrap(psic - yr)*p.R2D;  ec(k+1) = wrap(psi_hat + th - yr)*p.R2D;
    tope(k+1) = tope_k;
    for i = 1:p.NSUB                                     % lazo interno del servo
        err = th_cmd - th;
        if abs(err) < db, rate = 0; else, rate = min(max(p.K*err, -vmax), vmax); end
        th = th + rate*p.dt;
    end
end
end
