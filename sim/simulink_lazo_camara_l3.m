% simulink_lazo_camara_l3.m — Construye y corre en Simulink el lazo L3 de la cámara
% (RST con integrador + prealimentación del giróscopo), con cada bloque coloreado por su función.
%
% Nota: Control/diseno-estabilizacion-camara.md (L3, supuestos S1 a S4).
% Es la réplica en Simulink de la ley 'BI+FF' de sim/diseno-estabilizacion-camara.py: misma planta,
% mismos sensores, mismo estimador y mismo RST. El ruido sale de otro generador (rng de MATLAB),
% así que los números se parecen a los de Python pero no son idénticos.
%
% Todos los parámetros son ILUSTRATIVOS (Sin fuente en raw/): todavía no se ha medido la planta.
%
% Cómo se corre (desde la raíz del repo):
%   - En MATLAB: abrir este archivo y pulsar Run (F5). Deja abierto sim/lazo_camara_l3.slx.
%     Para volver a simular a mano: escribir el escenario (escenario = 'S1';), correr de nuevo
%     este script, o pulsar Run en el modelo (usa las variables del workspace base).
%   - En la terminal:  matlab -batch "run('sim/simulink_lazo_camara_l3.m')"
%
% Escribe: sim/lazo_camara_l3.slx (el modelo), derivados/simulink-lazo-camara-l3-metricas.csv,
%          salida/figuras/simulink-lazo-camara-l3.png y salida/figuras/simulink-lazo-camara-l3-modelo.png
%
% El nombre usa guiones bajos porque MATLAB no acepta guiones en nombres de scripts ni de modelos.
%
% Colores (también salen en la leyenda del modelo):
%   verde = referencia · rojo = perturbación (giro del cuerpo) · azul = controlador RST
%   cian = prealimentación · naranja = actuador · magenta = planta · amarillo = sensores
%   violeta = estimador de rumbo · gris = medición y salidas

raiz = fileparts(fileparts(mfilename('fullpath')));
if isempty(raiz), raiz = pwd; end
mdl  = 'lazo_camara_l3';

%% ------------------------------------------------------------ parámetros (los de la nota)
D2R = pi/180; R2D = 180/pi;
T      = 0.01;      % periodo del lazo [s] (100 Hz), base Hardware de Notion (S2)
NSUB   = 20;        % pasos de integración por periodo -> 0,5 ms (igual que el RK4 de Python)
TF     = 60;        % duración [s]
UMAX   = 6;         % saturación del actuador [V] — Sin fuente en raw/: 2S 18650 por puente H (S1)
Kc     = 30;        % ganancia de velocidad [rad/(s·V)] — Sin fuente en raw/: régimen 1 de L-07 (S1)
tau    = 0.1;       % constante de tiempo [s] — Sin fuente en raw/: régimen 1 de L-07 (S1)
Kc_hat = Kc;        % ganancia que usa la prealimentación (L3 sin adaptar)
WN = 20; ZETA = 0.7;            % polos deseados del lazo
bias_g = 0.5*D2R;               % sesgo del giróscopo [rad/s] (S3, supuesto)
sig_g  = 0.1*D2R;               % ruido del giróscopo por muestra (S3)
q_g    = D2R/16;                % cuantización del giróscopo: 16 LSB por °/s (L-10, no validado)
sig_m  = 0.9*D2R;               % ruido del rumbo magnético por muestra (S3, LIS3MDL en Monterey)
q_enc  = 2*pi/4096;             % codificador de 12 bits
we = 0.5; ze = 0.7; l1 = 2*ze*we; l2 = we^2;   % observador (ψ, b): filtro complementario

if ~exist('escenario', 'var'), escenario = 'S2'; end   % escenario del modelo guardado

%% ------------------------------------------------------------ diseño RST (diseño B + integrador)
p  = exp(-T/tau);
b1 = Kc*(T - tau*(1-p));  b0 = Kc*(tau*(1-p) - T*p);
A  = [1, -(1+p), p];      B  = [b1, b0];
sp = -ZETA*WN + 1i*WN*sqrt(1-ZETA^2);
Am = real(poly([exp(sp*T), exp(conj(sp)*T)]));
ao = exp(-2*WN*T);  Ao = conv([1 -ao], [1 -ao]);
Aint = conv(A, [1 -1]);                       % A·(z-1)
rhs  = conv(Am, Ao);                          % polinomio característico deseado (grado 4)
M = [[0 Aint]', [0 b1 b0 0 0]', [0 0 b1 b0 0]', [0 0 0 b1 b0]'];   % incógnitas: r, s2, s1, s0
lead = [Aint 0];
x = M(2:end, :) \ (rhs(2:end) - lead(2:end))';
R  = conv([1 x(1)], [1 -1]);                  % R = (z-1)(z+r)
S  = x(2:4)';
Km = polyval(Am, 1)/polyval(B, 1);
Tp = Km*Ao;
fprintf('RST:  R = [%s]\n      S = [%s]\n      T = [%s]\n', num2str(R, '%.4f  '), ...
        num2str(S, '%.4f  '), num2str(Tp, '%.4f  '));

%% ------------------------------------------------------------ referencia y giro del cuerpo
dt = T/NSUB;  t = (0:dt:TF+T)';
sref = min(max((t - 30)/1, 0), 1);
ref_data = [t, (90*D2R)*(0.5 - 0.5*cos(pi*sref))];       % giro de 90° a los 30 s (C11), 1 s

%% ------------------------------------------------------------ modelo de Simulink
construir_modelo(mdl, raiz);
fprintf('Modelo construido.\n');

%% ------------------------------------------------------------ simulación de S1 y S2
escenarios = {'S1', 'S2'};
filas = {};
figure('Name', 'Lazo L3 en Simulink', 'Color', 'w', 'Position', [100 100 900 620]);
for n = 1:2
    [psib_data, wb_data, ab_data] = perfil_cuerpo(escenarios{n}, t, dt, D2R);
    psi0 = psib_data(1, 2) + 1.5*D2R;  wb0 = wb_data(1, 2);  psib0 = psib_data(1, 2);
    assignin('base', 'psib_data', psib_data); assignin('base', 'wb_data', wb_data);
    assignin('base', 'ab_data', ab_data);     assignin('base', 'psi0', psi0);
    assignin('base', 'wb0', wb0);             assignin('base', 'psib0', psib0);
    fprintf('Simulando %s...\n', escenarios{n});
    out = sim(mdl);
    tt = out.e_deg.Time;  e = squeeze(out.e_deg.Data);  ec = squeeze(out.ec_deg.Data);
    u  = squeeze(out.u_V.Data);
    m  = (tt >= 5) & ~((tt >= 30) & (tt < 32));
    du = diff(u(tt >= 5));
    met = [max(abs(e(m))), sqrt(mean(e(m).^2)), 100*mean(abs(e(m)) > 10), ...
           max(abs(ec(m))), 1000*sqrt(mean(du.^2)), max(abs(u(tt >= 5)))];
    filas(end+1, :) = [{'L3_simulink', escenarios{n}}, num2cell(met)]; %#ok<SAGROW>
    fprintf('%s: máx |e| = %.2f°, RMS = %.2f°, %% > 10° = %.1f, máx |e control| = %.2f°, RMS Δu = %.1f mV, máx |u| = %.2f V\n', ...
            escenarios{n}, met);
    subplot(2, 1, n);
    plot(tt, e, 'Color', [0.11 0.37 0.83]); hold on;
    plot(tt, ec, 'Color', [0.85 0.33 0.10]);
    yline([-10 10], '--k', 'C8: ±10°');  xline(30, ':k', 'giro de 90°');
    grid on; ylim([-12 12]); ylabel('Error (°)');
    title(sprintf('%s · máx |e| = %.2f°, máx |e control| = %.2f°', escenarios{n}, met(1), met(4)));
    legend('e = ψ_c − ψ_{ref} (real)', 'e control = ψ̂_c − ψ_{ref}', 'Location', 'southeast');
end
xlabel('Tiempo (s)');

tabla = cell2table(filas, 'VariableNames', {'ley', 'escenario', 'max_e_deg', 'rms_e_deg', ...
    'viol_pct', 'max_e_ctrl_deg', 'rms_du_mV', 'u_max_V'});
writetable(tabla, fullfile(raiz, 'derivados', 'simulink-lazo-camara-l3-metricas.csv'));
exportgraphics(gcf, fullfile(raiz, 'salida', 'figuras', 'simulink-lazo-camara-l3.png'), 'Resolution', 150);

% deja el modelo listo con el escenario pedido
[psib_data, wb_data, ab_data] = perfil_cuerpo(escenario, t, dt, D2R);
psi0 = psib_data(1, 2) + 1.5*D2R;  wb0 = wb_data(1, 2);  psib0 = psib_data(1, 2);
try
    print(['-s' mdl], '-dpng', '-r150', fullfile(raiz, 'salida', 'figuras', 'simulink-lazo-camara-l3-modelo.png'));
catch err
    fprintf('No se pudo exportar la imagen del modelo: %s\n', err.message);
end
save_system(mdl, fullfile(raiz, 'sim', [mdl '.slx']));
if usejava('desktop'), open_system(mdl); end
fprintf('Listo: modelo en sim/%s.slx (escenario %s en el workspace).\n', mdl, escenario);


%% ============================================================ funciones locales
function [psib_data, wb_data, ab_data] = perfil_cuerpo(esc, t, dt, D2R)
% Giro del cuerpo (S4 de la nota), con semilla fija. S1: sin giro neto; S2: giro continuo.
rng(1);
if strcmp(esc, 'S1')
    wt = 2*pi*0.4; zt = 0.15;
    x = zeros(size(t)); v = zeros(size(t));
    for i = 2:numel(t)
        v(i) = v(i-1) + (-wt^2*x(i-1) - 2*zt*wt*v(i-1))*dt + sqrt(dt)*randn;
        x(i) = x(i-1) + v(i)*dt;
    end
    sc = (10*D2R)/std(x); x = x*sc; v = v*sc;
    wb = (40*D2R)*(2*pi*0.3)*cos(2*pi*0.3*t) + (15*D2R)*(2*pi*1.1)*cos(2*pi*1.1*t + 1) + v;
    psib = (40*D2R)*sin(2*pi*0.3*t) + (15*D2R)*sin(2*pi*1.1*t + 1) + x;
else
    tou = 0.5; sig = 15*D2R; g = zeros(size(t));
    for i = 2:numel(t)
        g(i) = g(i-1) - g(i-1)/tou*dt + sig*sqrt(2*dt/tou)*randn;
    end
    spin = (30 + 60*min(max(t - 5, 0), 1))*D2R;           % 30 -> 90 °/s al abrir paneles
    spin(t < 5) = 30*D2R;
    wb = spin + (20*D2R)*(2*pi*0.5)*cos(2*pi*0.5*t) + g;
    psib = cumsum(wb)*dt;
end
ab = gradient(wb, dt);
psib_data = [t, psib];  wb_data = [t, wb];  ab_data = [t, ab];
end

function construir_modelo(mdl, raiz)
% Arma el diagrama de bloques con un color por función.
C = struct( ...
    'ref',  '[0.72, 0.90, 0.72]', ...   % verde: referencia
    'pert', '[1.00, 0.70, 0.70]', ...   % rojo: perturbación
    'ctrl', '[0.66, 0.80, 1.00]', ...   % azul: controlador RST
    'ff',   '[0.68, 0.95, 0.95]', ...   % cian: prealimentación
    'act',  '[1.00, 0.82, 0.55]', ...   % naranja: actuador
    'plan', '[0.95, 0.74, 0.95]', ...   % magenta: planta
    'sens', '[1.00, 1.00, 0.62]', ...   % amarillo: sensores
    'est',  '[0.82, 0.74, 1.00]', ...   % violeta: estimador
    'med',  '[0.87, 0.87, 0.87]');      % gris: medición y salidas

if bdIsLoaded(mdl), close_system(mdl, 0); end
archivo = fullfile(raiz, 'sim', [mdl '.slx']);
if exist(archivo, 'file'), delete(archivo); end
new_system(mdl);
set_param(mdl, 'Solver', 'ode4', 'FixedStep', 'T/NSUB', 'StopTime', 'TF', ...
    'SaveOutput', 'off', 'SaveTime', 'off', 'ReturnWorkspaceOutputs', 'on');

% ---------------- REFERENCIA
b = blk(mdl, 'simulink/Sources/From Workspace', sprintf('REFERENCIA\npsi_ref (C8, C11)'), C.ref, ...
    'VariableName', 'ref_data', 'Interpolate', 'on', 'OutputAfterFinalValue', 'Holding final value');
ref = b;

% ---------------- PERTURBACIÓN: giro del cuerpo
sub = sprintf('PERTURBACIÓN\ngiro del cuerpo (S4)');
P = subsis(mdl, sub, C.pert, {}, {'psi_b', 'w_b', 'alfa_b'});
for k = 1:3
    nom = {'psib_data', 'wb_data', 'ab_data'};
    f = blk(P.path, 'simulink/Sources/From Workspace', nom{k}, C.pert, 'VariableName', nom{k}, ...
        'Interpolate', 'on', 'OutputAfterFinalValue', 'Holding final value');
    une(P.path, f, 1, P.o(k), 1);
end

% ---------------- CONTROLADOR RST con integrador y anti-windup
sub = sprintf('CONTROLADOR\nRST con integrador\nR u = T psi_ref - S psi_c');
K = subsis(mdl, sub, C.ctrl, {'psi_ref', 'psi_c_est', 'u_rst_aplicada'}, {'u_rst'});
fT = blk(K.path, 'simulink/Discrete/Discrete Filter', 'T(z)', C.ctrl, 'Numerator', 'Tp', 'Denominator', '1', 'SampleTime', 'T');
fS = blk(K.path, 'simulink/Discrete/Discrete Filter', 'S(z)', C.ctrl, 'Numerator', 'S', 'Denominator', '1', 'SampleTime', 'T');
d1 = blk(K.path, 'simulink/Discrete/Unit Delay', 'z^-1', C.ctrl, 'InitialCondition', '0', 'SampleTime', 'T');
fR = blk(K.path, 'simulink/Discrete/Discrete Filter', 'R(z) - z^2', C.ctrl, 'Numerator', 'R(2:3)', 'Denominator', '1', 'SampleTime', 'T');
sK = blk(K.path, 'simulink/Math Operations/Sum', 'suma RST', C.ctrl, 'Inputs', '+--', 'IconShape', 'rectangular');
une(K.path, K.i(1), 1, fT, 1); une(K.path, K.i(2), 1, fS, 1);
une(K.path, K.i(3), 1, d1, 1); une(K.path, d1, 1, fR, 1);
une(K.path, fT, 1, sK, 1); une(K.path, fS, 1, sK, 2); une(K.path, fR, 1, sK, 3);
une(K.path, sK, 1, K.o(1), 1);

% ---------------- PREALIMENTACIÓN del giróscopo
ff = blk(mdl, 'simulink/Math Operations/Gain', sprintf('PREALIMENTACIÓN\nu_ff = -w_b_est por 1 sobre Kc'), C.ff, 'Gain', '-1/Kc_hat');

% ---------------- suma de control y anti-windup
su = blk(mdl, 'simulink/Math Operations/Sum', sprintf('CONTROL\nu_rst + u_ff'), C.ctrl, 'Inputs', '++');
aw = blk(mdl, 'simulink/Math Operations/Sum', sprintf('CONTROL anti-windup\nu - u_ff'), C.ctrl, 'Inputs', '+-');

% ---------------- ACTUADOR
act = blk(mdl, 'simulink/Discontinuities/Saturation', sprintf('ACTUADOR\npuente H, |u| <= 6 V'), C.act, ...
    'UpperLimit', 'UMAX', 'LowerLimit', '-UMAX');

% ---------------- PLANTA: motor + cámara
sub = sprintf('PLANTA\nmotor + cámara\ntau th'''' + th'' = Kc u - tau psi_b''''');
G = subsis(mdl, sub, C.plan, {'u', 'alfa_b', 'psi_b'}, {'theta', 'psi_c'});
mx = blk(G.path, 'simulink/Signal Routing/Mux', 'Mux', C.plan, 'Inputs', '2');
ss = blk(G.path, 'simulink/Continuous/State-Space', 'motor + cámara', C.plan, ...
    'A', '[0 1; 0 -1/tau]', 'B', '[0 0; Kc/tau -1]', 'C', '[1 0]', 'D', '[0 0]');
sp = blk(G.path, 'simulink/Math Operations/Sum', 'psi_c = psi_b + theta', C.plan, 'Inputs', '++');
une(G.path, G.i(1), 1, mx, 1); une(G.path, G.i(2), 1, mx, 2); une(G.path, mx, 1, ss, 1);
une(G.path, ss, 1, G.o(1), 1); une(G.path, ss, 1, sp, 2); une(G.path, G.i(3), 1, sp, 1);
une(G.path, sp, 1, G.o(2), 1);

% ---------------- SENSORES
sub = sprintf('SENSORES\ngiróscopo, magnetómetro\ny codificador');
Sn = subsis(mdl, sub, C.sens, {'w_b', 'psi_b', 'theta'}, {'w_med', 'psi_mag', 'theta_enc'});
% giróscopo: muestreo, una muestra de latencia, sesgo, ruido y cuantización
z1 = blk(Sn.path, 'simulink/Discrete/Zero-Order Hold', 'muestreo giro', C.sens, 'SampleTime', 'T');
d2 = blk(Sn.path, 'simulink/Discrete/Unit Delay', 'latencia giro', C.sens, 'InitialCondition', 'wb0', 'SampleTime', 'T');
bg = blk(Sn.path, 'simulink/Sources/Constant', 'sesgo b_g', C.sens, 'Value', 'bias_g', 'SampleTime', 'T');
ng = blk(Sn.path, 'simulink/Sources/Random Number', 'ruido giro', C.sens, 'Mean', '0', 'Variance', 'sig_g^2', 'Seed', '101', 'SampleTime', 'T');
sg = blk(Sn.path, 'simulink/Math Operations/Sum', 'suma giro', C.sens, 'Inputs', '+++', 'IconShape', 'rectangular');
qg = blk(Sn.path, 'simulink/Discontinuities/Quantizer', '16 LSB por grado por s', C.sens, 'QuantizationInterval', 'q_g');
une(Sn.path, Sn.i(1), 1, z1, 1); une(Sn.path, z1, 1, d2, 1); une(Sn.path, d2, 1, sg, 1);
une(Sn.path, bg, 1, sg, 2); une(Sn.path, ng, 1, sg, 3); une(Sn.path, sg, 1, qg, 1); une(Sn.path, qg, 1, Sn.o(1), 1);
% magnetómetro: muestreo, latencia, error de calibración e inclinación, ruido, envoltura a ±180°
z2 = blk(Sn.path, 'simulink/Discrete/Zero-Order Hold', 'muestreo mag', C.sens, 'SampleTime', 'T');
d3 = blk(Sn.path, 'simulink/Discrete/Unit Delay', 'latencia mag', C.sens, 'InitialCondition', 'psib0', 'SampleTime', 'T');
me = blk(Sn.path, 'simulink/Sources/Sine Wave', sprintf('error calibración 1,5°\n+ inclinación 2° a 0,4 Hz'), C.sens, ...
    'Amplitude', '2*D2R', 'Bias', '1.5*D2R', 'Frequency', '2*pi*0.4', 'Phase', '0', 'SampleTime', 'T');
nm = blk(Sn.path, 'simulink/Sources/Random Number', 'ruido mag', C.sens, 'Mean', '0', 'Variance', 'sig_m^2', 'Seed', '102', 'SampleTime', 'T');
sm = blk(Sn.path, 'simulink/Math Operations/Sum', 'suma mag', C.sens, 'Inputs', '+++', 'IconShape', 'rectangular');
wm = blk(Sn.path, 'simulink/User-Defined Functions/Fcn', 'envolver ±180°', C.sens, 'Expression', 'atan2(sin(u(1)),cos(u(1)))');
une(Sn.path, Sn.i(2), 1, z2, 1); une(Sn.path, z2, 1, d3, 1); une(Sn.path, d3, 1, sm, 1);
une(Sn.path, me, 1, sm, 2); une(Sn.path, nm, 1, sm, 3); une(Sn.path, sm, 1, wm, 1); une(Sn.path, wm, 1, Sn.o(2), 1);
% codificador de 12 bits
z3 = blk(Sn.path, 'simulink/Discrete/Zero-Order Hold', 'muestreo cod', C.sens, 'SampleTime', 'T');
qe = blk(Sn.path, 'simulink/Discontinuities/Quantizer', 'codificador 12 bits', C.sens, 'QuantizationInterval', 'q_enc');
une(Sn.path, Sn.i(3), 1, z3, 1); une(Sn.path, z3, 1, qe, 1); une(Sn.path, qe, 1, Sn.o(3), 1);

% ---------------- ESTIMADOR de rumbo (observador psi, b = filtro complementario)
sub = sprintf('ESTIMADOR\nobservador (psi_b, b_g)\nfiltro complementario');
E = subsis(mdl, sub, C.est, {'w_med', 'psi_mag'}, {'psi_b_est', 'w_b_est'});
dp = blk(E.path, 'simulink/Discrete/Unit Delay', 'psi_est(k-1)', C.est, 'InitialCondition', 'psi0', 'SampleTime', 'T');
db = blk(E.path, 'simulink/Discrete/Unit Delay', 'b_est(k-1)', C.est, 'InitialCondition', '0', 'SampleTime', 'T');
si = blk(E.path, 'simulink/Math Operations/Sum', 'innovación', C.est, 'Inputs', '+-');
wi = blk(E.path, 'simulink/User-Defined Functions/Fcn', 'envolver innov', C.est, 'Expression', 'atan2(sin(u(1)),cos(u(1)))');
g1 = blk(E.path, 'simulink/Math Operations/Gain', 'l1', C.est, 'Gain', 'l1');
g2 = blk(E.path, 'simulink/Math Operations/Gain', '-T l2', C.est, 'Gain', '-T*l2');
sd = blk(E.path, 'simulink/Math Operations/Sum', 'w - b + l1 innov', C.est, 'Inputs', '+-+', 'IconShape', 'rectangular');
gT = blk(E.path, 'simulink/Math Operations/Gain', 'T', C.est, 'Gain', 'T');
sp2 = blk(E.path, 'simulink/Math Operations/Sum', 'psi_est(k)', C.est, 'Inputs', '++');
sb = blk(E.path, 'simulink/Math Operations/Sum', 'b_est(k)', C.est, 'Inputs', '++');
sw = blk(E.path, 'simulink/Math Operations/Sum', 'w_b_est = w - b', C.est, 'Inputs', '+-');
une(E.path, E.i(2), 1, si, 1); une(E.path, dp, 1, si, 2); une(E.path, si, 1, wi, 1);
une(E.path, E.i(1), 1, sd, 1); une(E.path, db, 1, sd, 2); une(E.path, wi, 1, g1, 1); une(E.path, g1, 1, sd, 3);
une(E.path, sd, 1, gT, 1); une(E.path, gT, 1, sp2, 1); une(E.path, dp, 1, sp2, 2); une(E.path, sp2, 1, dp, 1);
une(E.path, wi, 1, g2, 1); une(E.path, g2, 1, sb, 1); une(E.path, db, 1, sb, 2); une(E.path, sb, 1, db, 1);
une(E.path, E.i(1), 1, sw, 1); une(E.path, sb, 1, sw, 2);
une(E.path, sp2, 1, E.o(1), 1); une(E.path, sw, 1, E.o(2), 1);

pc = blk(mdl, 'simulink/Math Operations/Sum', sprintf('ESTIMADOR\npsi_c_est = psi_b_est + theta_enc'), C.est, 'Inputs', '++');

% ---------------- MEDICIÓN y salidas
se  = blk(mdl, 'simulink/Math Operations/Sum', sprintf('MEDICIÓN\ne = psi_c - psi_ref'), C.med, 'Inputs', '+-');
we_ = blk(mdl, 'simulink/User-Defined Functions/Fcn', sprintf('MEDICIÓN\nenvolver e, a grados'), C.med, 'Expression', '180/pi*atan2(sin(u(1)),cos(u(1)))');
sc_ = blk(mdl, 'simulink/Math Operations/Sum', sprintf('MEDICIÓN\ne control = psi_c_est - psi_ref'), C.med, 'Inputs', '+-');
wc_ = blk(mdl, 'simulink/User-Defined Functions/Fcn', sprintf('MEDICIÓN\nenvolver e control'), C.med, 'Expression', '180/pi*atan2(sin(u(1)),cos(u(1)))');
sco = blk(mdl, 'simulink/Sinks/Scope', sprintf('MEDICIÓN\nerror (°) real y de control'), C.med, 'NumInputPorts', '2');
scu = blk(mdl, 'simulink/Sinks/Scope', sprintf('MEDICIÓN\nu (V)'), C.med);
t1 = blk(mdl, 'simulink/Sinks/To Workspace', 'e_deg', C.med, 'VariableName', 'e_deg', 'SaveFormat', 'Timeseries', 'SampleTime', 'T');
t2 = blk(mdl, 'simulink/Sinks/To Workspace', 'ec_deg', C.med, 'VariableName', 'ec_deg', 'SaveFormat', 'Timeseries', 'SampleTime', 'T');
t3 = blk(mdl, 'simulink/Sinks/To Workspace', 'u_V', C.med, 'VariableName', 'u_V', 'SaveFormat', 'Timeseries', 'SampleTime', 'T');

% ---------------- conexiones del nivel superior (con nombre de señal)
une(mdl, ref, 1, K.h, 1, 'psi_ref');
une(mdl, pc, 1, K.h, 2, 'psi_c estimado');
une(mdl, aw, 1, K.h, 3, 'u_rst aplicada');
une(mdl, K.h, 1, su, 1, 'u_rst');
une(mdl, ff, 1, su, 2, 'u_ff');
une(mdl, su, 1, act, 1, 'u pedida');
une(mdl, act, 1, G.h, 1, 'u (V)');
une(mdl, act, 1, aw, 1); une(mdl, ff, 1, aw, 2);
une(mdl, act, 1, scu, 1); une(mdl, act, 1, t3, 1);
une(mdl, P.h, 3, G.h, 2, 'alfa_b');
une(mdl, P.h, 1, G.h, 3, 'psi_b');
une(mdl, P.h, 2, Sn.h, 1, 'w_b');
une(mdl, P.h, 1, Sn.h, 2);
une(mdl, G.h, 1, Sn.h, 3, 'theta');
une(mdl, Sn.h, 1, E.h, 1, 'w medida');
une(mdl, Sn.h, 2, E.h, 2, 'psi_mag');
une(mdl, E.h, 1, pc, 1, 'psi_b estimado');
une(mdl, Sn.h, 3, pc, 2, 'theta_enc');
une(mdl, E.h, 2, ff, 1, 'w_b estimado');
une(mdl, G.h, 2, se, 1, 'psi_c real'); une(mdl, ref, 1, se, 2);
une(mdl, se, 1, we_, 1); une(mdl, we_, 1, sco, 1, 'e (°)'); une(mdl, we_, 1, t1, 1);
une(mdl, pc, 1, sc_, 1); une(mdl, ref, 1, sc_, 2);
une(mdl, sc_, 1, wc_, 1); une(mdl, wc_, 1, sco, 2, 'e control (°)'); une(mdl, wc_, 1, t2, 1);

% ---------------- orden automático y leyenda de colores
fprintf('Bloques conectados; ordenando el diagrama...\n');
for s = {P.path, K.path, G.path, Sn.path, E.path, mdl}
    try, Simulink.BlockDiagram.arrangeSystem(s{1}); catch err, fprintf('  arrangeSystem: %s\n', err.message); end
end
fprintf('Diagrama ordenado; leyenda...\n');
pos = cell2mat(get_param(find_system(mdl, 'SearchDepth', 1, 'Type', 'block'), 'Position'));
x0 = min(pos(:, 1));  y0 = max(pos(:, 4)) + 40;
ley = {'ref', 'Referencia'; 'pert', 'Perturbación (giro del cuerpo)'; 'ctrl', 'Controlador RST y anti-windup'; ...
       'ff', 'Prealimentación del giróscopo'; 'act', 'Actuador (saturación)'; 'plan', 'Planta: motor + cámara'; ...
       'sens', 'Sensores'; 'est', 'Estimador de rumbo'; 'med', 'Medición y salidas'};
tit = Simulink.Annotation(mdl, 'Lazo L3 de la cámara · colores por función (Control/diseno-estabilizacion-camara.md)');
tit.Position = [x0, y0, x0 + 600, y0 + 20];  tit.FontWeight = 'bold';
for k = 1:size(ley, 1)
    col = floor((k-1)/3); fil = mod(k-1, 3);
    a = Simulink.Annotation(mdl, ['   ' ley{k, 2} '   ']);
    a.Position = [x0 + 260*col, y0 + 30 + 28*fil, x0 + 260*col + 240, y0 + 30 + 28*fil + 22];
    a.BackgroundColor = C.(ley{k, 1});
    a.DropShadow = 'on';
end
end

function h = blk(sys, lib, nombre, color, varargin)
% Agrega un bloque con nombre y color (fondo) y aplica sus parámetros.
h = add_block(lib, [sys '/' nombre], 'MakeNameUnique', 'on');
set_param(h, 'BackgroundColor', color, 'ForegroundColor', 'black');
if ~isempty(varargin), set_param(h, varargin{:}); end
end

function S = subsis(sys, nombre, color, entradas, salidas)
% Subsistema con puertos nombrados. S.h: el bloque (para conectarlo afuera, por número de puerto);
% S.i y S.o: sus Inport y Outport internos (para conectar adentro); S.path: su ruta.
S.h = add_block('built-in/Subsystem', [sys '/' nombre]);
set_param(S.h, 'BackgroundColor', color, 'ForegroundColor', 'black');
S.path = getfullname(S.h);
S.i = zeros(1, numel(entradas)); S.o = zeros(1, numel(salidas));
for k = 1:numel(entradas)
    S.i(k) = add_block('built-in/Inport', [S.path '/' entradas{k}]);
    set_param(S.i(k), 'BackgroundColor', color);
end
for k = 1:numel(salidas)
    S.o(k) = add_block('built-in/Outport', [S.path '/' salidas{k}]);
    set_param(S.o(k), 'BackgroundColor', color);
end
end

function une(sys, src, sp, dst, dp, etiqueta)
% Conecta el puerto de salida sp de src con el de entrada dp de dst (por manejadores).
ps = get_param(src, 'PortHandles');  pd = get_param(dst, 'PortHandles');
l = add_line(sys, ps.Outport(sp), pd.Inport(dp), 'autorouting', 'smart');
if nargin > 5, set_param(l, 'Name', etiqueta); end
end
