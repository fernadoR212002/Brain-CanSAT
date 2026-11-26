function rst_servo_vivo(modo, puerto)
% rst_servo_vivo — El RST del lazo L3 (el mismo de Simulink) mueve el servo de la cámara con el
% giróscopo y el magnetómetro reales del BNO055.
%
%   rst_servo_vivo            en vivo con el ESP32 (pulsar Run). Para parar: cerrar la ventana o Ctrl+C.
%   rst_servo_vivo('prueba')  sin hardware: una base simulada que oscila, para ver que el código responde.
%   rst_servo_vivo('vivo', "COM7")   en vivo con otro puerto.
%
% Cadena:
%   BNO055 (gz, mx, my) -> ESP32 -> USB -> MATLAB: estimador + RST + motor virtual -> pulso (µs)
%   -> USB -> ESP32 -> PWM de 50 Hz en el GPIO 18 -> servo -> cámara
%
% El RST sale de sim/simulink_lazo_camara_l3.m (mismos R, S, T, Kc, tau, T = 10 ms y observador).
%
% Por qué hay un «motor virtual»: el servo es de posición (recibe un ángulo), pero el RST se diseñó
% para un motor (recibe tensión y la integra en ángulo): Kc/(s(tau s + 1)). Para usar el MISMO RST
% sin rediseñarlo, su salida u (V) pasa por ese modelo del motor, y el ángulo que sale es el que se
% le pide al servo. Así el RST ve exactamente la planta para la que se diseñó.
%
% Magnetómetro: solo entra al estimador cuando el BNO055 lo da por calibrado (CAL_MAG_MIN). Antes,
% el rumbo sale solo del giróscopo. Cuando entra, se corre el marco de referencia entero y la cámara
% no salta. El firmware guarda la calibración en el ESP32 cuando llega a 3/3.
%
% Conexiones y firmware: firmware/src/main.cpp (cargarlo antes con PlatformIO). No guarda datos.
%
% Montaje: el BNO055 va plano, pegado a la BASE (no a la cámara) y LEJOS del servo SG90 (10 cm o
% más): el imán de su motor y su corriente mueven el campo magnético. El SG90 va en la base, con 5 V
% de una fuente aparte (tierra común con el ESP32), y la cámara en su brazo. Al girar la base a
% mano, la cámara debe quedarse apuntando igual.

if nargin < 1, modo = 'vivo'; end

% ------------------------------------------------------------ lo que se puede cambiar
PUERTO       = "/dev/ttyUSB0";  % en Windows, por ejemplo "COM7"
BAUDIOS      = 921600;          % el mismo del firmware
SIGNO_SERVO  = +1;    % si al girar la base la cámara gira CON ella (en vez de quedarse quieta): -1
PULSO_CENTRO = 1500;  % µs, servo en el centro
US_POR_GRADO = 40;    % µs por grado. SG90 de 180°: ≈ 0,5 a 2,4 ms de punta a punta (≈ 10,5 µs/°)
TH_LIM       = 75;    % grados máximos a cada lado del centro; si el SG90 zumba en un extremo, bajarlo
CAL_MAG_MIN  = 2;     % calibración mínima del magnetómetro (0 a 3) para usarlo; 4 = no usarlo nunca
PASO_REF     = 45;    % grados que mueve la referencia cada flecha ← o →
VEL_REF      = 90;    % °/s con que se mueve la referencia (el giro de 90° de C11 dura 1 s)

if nargin >= 2, PUERTO = string(puerto); end
D2R = pi/180;  R2D = 180/pi;
cfg = struct('signo', SIGNO_SERVO, 'centro', PULSO_CENTRO, 'us_grado', US_POR_GRADO);
c = iniciar_controlador(TH_LIM*D2R);
fprintf('RST de simulink_lazo_camara_l3.m: T = %g ms, Kc = %g rad/(s·V), tau = %g s\n', ...
    1e3*c.T, c.Kc, c.tau);

if strcmpi(modo, 'prueba')
    prueba_sin_hardware(c, cfg);
    return
end

% ------------------------------------------------------------ conexión con el ESP32
esp = serialport(PUERTO, BAUDIOS, "Timeout", 3);
configureTerminator(esp, "LF");
limpieza = onCleanup(@() cerrar(esp, PULSO_CENTRO));
fprintf('Esperando datos del ESP32 en %s...\n', PUERTO);
pause(1.5);          % si el ESP32 se reinicia al abrir el puerto, arranca el BNO055
flush(esp);

% ------------------------------------------------------------ ventana
fig = figure('Name', 'RST -> servo (en vivo)', 'NumberTitle', 'off', 'Color', 'w', ...
    'KeyPressFcn', @(f, ev) set(f, 'UserData', ev.Key));
ax1 = subplot(2, 1, 1); hold(ax1, 'on'); grid(ax1, 'on');
NPT = 1500;          % 15 s a la vista
hm = animatedline(ax1, 'Color', [0.65 0.65 0.65], 'LineWidth', 0.8, 'MaximumNumPoints', NPT);
hb = animatedline(ax1, 'Color', [0.85 0.20 0.20], 'LineWidth', 1.2, 'MaximumNumPoints', NPT);
hc = animatedline(ax1, 'Color', [0.15 0.45 0.85], 'LineWidth', 1.8, 'MaximumNumPoints', NPT);
hr = animatedline(ax1, 'Color', [0.10 0.60 0.30], 'LineWidth', 1.2, 'LineStyle', '--', 'MaximumNumPoints', NPT);
legend(ax1, {'rumbo del magnetómetro', 'base (estimada)', 'cámara = base + servo', 'referencia'}, ...
    'Location', 'northwest');
ylabel(ax1, 'Rumbo desde el arranque (°)');
tit = title(ax1, '');
ax2 = subplot(2, 1, 2); hold(ax2, 'on'); grid(ax2, 'on');
hs = animatedline(ax2, 'Color', [0.95 0.45 0.10], 'LineWidth', 1.5, 'MaximumNumPoints', NPT);
yline(ax2, [-TH_LIM TH_LIM], ':', 'Color', [0.4 0.4 0.4]);
ylim(ax2, [-95 95]);
ylabel(ax2, 'Ángulo pedido al servo (°)'); xlabel(ax2, 'Tiempo (s)');
title(ax2, '← → mueven la referencia 45° · espacio = centrar · cerrar la ventana para parar', ...
    'FontWeight', 'normal');

% ------------------------------------------------------------ lazo
ref = 0; ref_obj = 0;           % rad, referencia relativa al rumbo del arranque
n = 0; t0_ms = NaN; t_ant = NaN; perdidas = 0; n_seg = 0; hz = 0; tic_hz = tic;
pulso = PULSO_CENTRO; cal = [0 0 0]; usar_mag = false; Bmod = NaN;
buf = zeros(6, 0);              % puntos pendientes de dibujar
resto = ''; t_dibujo = tic; t_dato = tic;
disp('Lazo corriendo. Gira la base a mano: la cámara debe quedarse apuntando igual.');
while isgraphics(fig)
    nb = esp.NumBytesAvailable;
    if nb == 0
        if toc(t_dato) > 3
            warning('No llegan datos del ESP32 (¿firmware cargado?, ¿puerto %s?).', PUERTO);
            t_dato = tic;
        end
        pause(0.002);            % cede el paso: teclas y cierre de la ventana
        continue
    end
    t_dato = tic;
    % lee TODO lo que llegó de una vez y procesa cada muestra (así no se pierde ninguna)
    txt = [resto, read(esp, nb, "char")];
    fin = find(txt == newline);
    n_antes = n;  ini = 1;
    for k = 1:numel(fin)
        procesar(txt(ini:fin(k) - 1));
        ini = fin(k) + 1;
    end
    resto = txt(ini:end);
    if numel(resto) > 500, resto = ''; end
    if n > n_antes
        writeline(esp, sprintf('P%d', pulso));      % una orden con la muestra más reciente
    end

    if ~isgraphics(fig), break; end      % se cerró la ventana
    % teclas
    tecla = fig.UserData;
    if ~isempty(tecla)
        fig.UserData = '';
        switch tecla
            case 'rightarrow', ref_obj = ref_obj + PASO_REF*D2R;
            case 'leftarrow',  ref_obj = ref_obj - PASO_REF*D2R;
            case 'space',      ref_obj = c.psi - c.psi0;   % la cámara apunta a donde apunta la base
        end
    end

    % dibujo a 10 Hz
    if toc(t_dibujo) >= 0.1 && ~isempty(buf)
        t_dibujo = tic;
        addpoints(hm, buf(1, :), buf(6, :)); addpoints(hb, buf(1, :), buf(2, :));
        addpoints(hc, buf(1, :), buf(3, :)); addpoints(hr, buf(1, :), buf(4, :));
        addpoints(hs, buf(1, :), buf(5, :));
        tt = buf(1, end);
        xlim(ax1, [tt - 15, tt + 0.5]); xlim(ax2, [tt - 15, tt + 0.5]);
        if toc(tic_hz) >= 1, hz = n_seg/toc(tic_hz); n_seg = 0; tic_hz = tic; end
        est_mag = 'IGNORADO, solo giróscopo';
        if c.mag_activo, est_mag = 'EN USO'; elseif usar_mag, est_mag = 'alineando'; end
        tit.String = sprintf(['mag. %s (cal. %d/3, |B| %.0f µT) · %.0f Hz · perdidas %d   |   ' ...
            'cámara %.0f° · servo %.0f° (%d µs)'], ...
            est_mag, cal(3), Bmod, hz, perdidas, buf(3, end), buf(5, end), pulso);
        buf = zeros(6, 0);
        drawnow limitrate     % nunca frena el lazo: si la pantalla está ocupada, salta el cuadro
    end
    pause(0.001)              % atiende el cierre de la ventana y las teclas
end

    function procesar(s)
        v = sscanf(s, '%f,%f,%f,%f,%f,%f,%f,%f,%f');
        if numel(v) ~= 9
            s = strtrim(s);
            if startsWith(s, '#'), disp(s); end      % mensajes del firmware
            return
        end
        t_ms = v(1);
        if isnan(t0_ms), t0_ms = t_ms; end
        if ~isnan(t_ant) && t_ms - t_ant > 15, perdidas = perdidas + round((t_ms - t_ant)/10) - 1; end
        t_ant = t_ms;
        cal = v(6:8).';
        Bmod = norm(v(3:5));
        usar_mag = cal(3) >= CAL_MAG_MIN;
        % referencia con velocidad limitada
        paso_r = VEL_REF*D2R*c.T;
        ref = ref + min(max(ref_obj - ref, -paso_r), paso_r);
        [c, pulso] = paso_control(c, v(2), v(3), v(4), ref, cfg, usar_mag);
        n = n + 1; n_seg = n_seg + 1;
        buf(:, end + 1) = [(t_ms - t0_ms)/1e3; (c.psi - c.psi0)*R2D; (c.psi + c.x(1) - c.psi0)*R2D; ...
                           ref*R2D; c.x(1)*R2D; (c.psi + envolver(c.psi_mag - c.psi) - c.psi0)*R2D];
    end
end

% ================================================================ controlador
function c = iniciar_controlador(th_lim)
prm = parametros_simulink();
c.T = prm.T;  c.Kc = prm.Kc_hat;  c.tau = prm.tau;  c.UMAX = prm.UMAX;
c.R = prm.R;  c.S = prm.S;  c.Tp = prm.Tp;  c.l1 = prm.l1;  c.l2 = prm.l2;
% motor virtual Kc/(s(tau s+1)) discretizado con retención de orden cero (el mismo B/A del diseño)
p = exp(-c.T/c.tau);
c.Phi = [1, c.tau*(1 - p); 0, p];
c.Gam = c.Kc*[c.T - c.tau*(1 - p); 1 - p];
c.th_lim = th_lim;
c.x = [0; 0];                 % [theta; theta'] del motor virtual = ángulo pedido al servo
c.psi = NaN; c.psi0 = NaN; c.psi_mag = NaN; c.b = 0; c.w = 0;
c.mag_activo = false; c.al = [0 0 0];   % alineación inicial con el magnetómetro: [Σsin, Σcos, n]
c.rh = zeros(1, 3); c.yh = zeros(1, 3); c.uah = zeros(1, 2);
end

function prm = parametros_simulink()
% Corre simulink_lazo_camara_l3.m solo hasta el diseño del RST y devuelve sus variables.
raiz = fileparts(fileparts(fileparts(mfilename('fullpath'))));
solo_parametros = true; %#ok<NASGU>
run(fullfile(raiz, 'sim', 'simulink_lazo_camara_l3.m'));
f = [tempname, '.mat'];
save(f);
prm = load(f);
delete(f);
end

function [c, pulso] = paso_control(c, gz_dps, mx, my, ref, cfg, usar_mag)
% Un periodo T: estimador de rumbo (observador psi, b), RST + prealimentación, motor virtual, pulso.
w_med     = gz_dps*pi/180;
c.psi_mag = atan2(-my, mx);       % rumbo con z hacia arriba, positivo antihorario (igual que gz)
if isnan(c.psi)                   % primera muestra: todo en reposo apuntando al rumbo inicial
    c.psi = c.psi_mag; c.psi0 = c.psi_mag;
    c.rh(:) = c.psi_mag; c.yh(:) = c.psi_mag;
end
% ESTIMADOR (filtro complementario de simulink_lazo_camara_l3.m)
innov = 0;                        % sin magnetómetro confiable: solo el giróscopo
if usar_mag && c.mag_activo
    innov = envolver(c.psi_mag - c.psi);
elseif usar_mag
    % el magnetómetro recién entra: durante 1 s se promedia su diferencia con el giróscopo (media
    % circular, 100 muestras) y luego se corre todo el marco (base, referencia e historias del RST)
    % ese promedio. La salida del RST no cambia y la cámara no salta. Con una sola muestra, su
    % ruido (≈ 1°) quedaría fijo para siempre en la referencia.
    q = envolver(c.psi_mag - c.psi);
    c.al = c.al + [sin(q), cos(q), 1];
    if c.al(3) >= 100
        d = atan2(c.al(1), c.al(2));
        c.psi = c.psi + d;  c.psi0 = c.psi0 + d;  c.rh = c.rh + d;  c.yh = c.yh + d;
        c.mag_activo = true;
    end
else
    c.mag_activo = false;  c.al = [0 0 0];
end
c.psi = c.psi + c.T*(w_med - c.b + c.l1*innov);
c.b   = c.b - c.T*c.l2*innov;
c.w   = w_med - c.b;
% RST:  R u = T psi_ref - S psi_c_est,  con psi_c_est = psi_b_est + theta
r = c.psi0 + ref;
y = c.psi + c.x(1);
k = round((y - r)/(2*pi));        % rumbo equivalente más cercano: nunca persigue una vuelta entera
if k ~= 0
    c.psi0 = c.psi0 + 2*pi*k;  c.rh = c.rh + 2*pi*k;  r = r + 2*pi*k;
end
c.rh = [r, c.rh(1:2)];  c.yh = [y, c.yh(1:2)];
u_rst = c.Tp*c.rh.' - c.S*c.yh.' - c.R(2:3)*c.uah.';
u_ff  = -c.w/c.Kc;                                  % PREALIMENTACIÓN del giróscopo
u     = min(max(u_rst + u_ff, -c.UMAX), c.UMAX);    % saturación ±UMAX
c.uah = [u - u_ff, c.uah(1)];                       % anti-windup: lo que de verdad se aplicó
% MOTOR VIRTUAL -> ángulo del servo
c.x = c.Phi*c.x + c.Gam*u;
if abs(c.x(1)) > c.th_lim                           % tope del servo: el motor virtual se detiene
    c.x = [sign(c.x(1))*c.th_lim; 0];
end
pulso = round(cfg.centro + cfg.signo*c.x(1)*180/pi*cfg.us_grado);
pulso = min(max(pulso, 600), 2400);
end

function a = envolver(a)
a = atan2(sin(a), cos(a));
end

function cerrar(esp, centro)
try
    writeline(esp, sprintf('P%d', centro));
    pause(0.05);
catch
end
delete(esp);
disp('Puerto cerrado; servo al centro.');
end

% ================================================================ prueba sin hardware
function prueba_sin_hardware(c, cfg)
% Base que oscila como si la giraras a mano, giróscopo con sesgo y ruido, servo con retardo de
% 50 ms y 600 °/s. Los primeros 5 s el magnetómetro está sin calibrar (25° corrido, se ignora);
% después entra calibrado. Mide el rumbo real de la cámara contra el de su arranque.
D2R = pi/180;  T = c.T;  N = round(30/T);
rng(7);
t = (0:N-1)*T;
psib = 40*D2R + 30*D2R*sin(2*pi*0.25*t) + 10*D2R*sin(2*pi*0.8*t + 1);     % rumbo de la base
wb   = 30*D2R*2*pi*0.25*cos(2*pi*0.25*t) + 10*D2R*2*pi*0.8*cos(2*pi*0.8*t + 1);
ref_obj = -30*D2R*(t >= 15);                                               % giro de -30° a los 15 s
H = 26.8;                                                                  % µT, campo horizontal
th_srv = 0; ref = 0; e = zeros(1, N); th_log = zeros(1, N);
for k = 1:N
    cal_ok = t(k) >= 5;
    err_mag = 25*D2R*~cal_ok;
    gz = (wb(k) + 0.5*D2R + 0.1*D2R*randn)/D2R;                            % °/s, con sesgo
    mx =  H*cos(psib(k) + err_mag) + 0.4*randn;  my = -H*sin(psib(k) + err_mag) + 0.4*randn;
    ref = ref + min(max(ref_obj(k) - ref, -90*D2R*T), 90*D2R*T);
    [c, pulso] = paso_control(c, gz, mx, my, ref, cfg, cal_ok);
    th_cmd = cfg.signo*(pulso - cfg.centro)/cfg.us_grado*D2R;              % lo que entiende el servo
    for j = 1:10                                                           % servo físico, 1 ms
        th_srv = th_srv + min(max((th_cmd - th_srv)/0.05, -600*D2R), 600*D2R)*T/10;
    end
    e(k) = envolver(psib(k) + th_srv - (psib(1) + ref));
    th_log(k) = th_srv;
end
m = t >= 3 & ~(t >= 15 & t < 16.5);
fprintf('Prueba sin hardware (30 s, base ±40°, magnetómetro calibrado desde 5 s, giro de -30° a 15 s):\n');
fprintf('  rumbo de la cámara contra su arranque: máx %.2f°, rms %.2f° (C8 pide < 10°)\n', ...
    max(abs(e(m)))/D2R, rms(e(m))/D2R);
fprintf('  servo: de %.0f° a %.0f°\n', min(th_log)/D2R, max(th_log)/D2R);
if ~batchStartupOptionUsed
    figure('Name', 'Prueba sin hardware', 'Color', 'w');
    subplot(2, 1, 1); plot(t, (psib - psib(1))/D2R, t, (psib + th_log - psib(1))/D2R, t, ref_obj/D2R, '--');
    grid on; ylabel('Rumbo (°)'); legend('base', 'cámara', 'referencia');
    subplot(2, 1, 2); plot(t, e/D2R); grid on; ylabel('Error de la cámara (°)'); xlabel('Tiempo (s)');
end
end
