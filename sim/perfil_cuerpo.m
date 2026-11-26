function [psib_data, wb_data, ab_data] = perfil_cuerpo(esc, t, dt, D2R)
% perfil_cuerpo — Giro del cuerpo del PocketQube (S4 de Control/diseno-estabilizacion-camara.md).
% S1: sin giro neto (rigidez de las cuerdas); S2: giro continuo (destorcedor o paracaídas que gira).
% Semilla fija. Lo usan simulink_lazo_camara_l3.m y tst_004_pwm_actuador.m, para que los dos
% vean exactamente el mismo giro del cuerpo. Sin fuente en raw/: los dos escenarios son supuestos.
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
