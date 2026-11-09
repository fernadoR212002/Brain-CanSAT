"""
diseno-estabilizacion-camara.py — Comparativa de leyes de control para el lazo de rumbo de la cámara
(C8, C11, PQ15–PQ18) y prueba de identificabilidad en vuelo.
Nota: Control/diseno-estabilizacion-camara.md · Modelo: Control/modelo-rumbo-espacio-estados.md

Planta (modelo reducido L_a -> 0 de la nota del modelo, sección 4):
    tau*th_dd + th_d = Kc*u - tau*psib_dd ,   psic = psib + th
Leyes: L0 servo de hobby · L1a/L1b RST sin integrador (cancela / conserva el cero de muestreo)
       L2 RST + integrador · L3 L2 + prealimentación del giróscopo · L4 cascada (IMU en la cámara)
       L5 L3 con Kc estimada en vuelo (RLS escalar).

Todos los parámetros son ILUSTRATIVOS (Sin fuente en raw/): todavía no se ha medido nada.
Semilla fija. Escribe derivados/diseno-estabilizacion-camara-*.csv y salida/figuras/diseno-estabilizacion-camara-*.png.
Se corre desde la raíz del repo:  python3 sim/diseno-estabilizacion-camara.py   (≈ 1 min)
"""
import numpy as np

D2R, R2D = np.pi/180, 180/np.pi
wrap = lambda a: (a + np.pi) % (2*np.pi) - np.pi

# ------------------------------------------------------------------ parámetros
T      = 0.01          # periodo del lazo [s] (100 Hz) — base Hardware de Notion (raw/datos/notion-hardware-2026-10-25.md)
NSUB   = 20            # pasos de integración por periodo -> dt = 0.5 ms
TF     = 60.0          # duración [s]
UMAX   = 6.0           # saturación del actuador [V] — Sin fuente en raw/: supuesto 2S 18650 por puente H
PLANT0 = dict(Kc=30.0, tau=0.1)        # Sin fuente en raw/: régimen 1 del ejemplo L-07 (ilustrativo, falta identificar el servo)
WN, ZETA = 20.0, 0.7                   # polos dominantes deseados del lazo (modelo de referencia)

# ------------------------------------------------------------------ herramientas RST
def zoh_plant(Kc, tau, T):
    """G(z) = (b1 z + b0)/((z-1)(z-p)) de Kc/(s(tau s+1)) con ZOH."""
    p  = np.exp(-T/tau)
    b1 = Kc*(T - tau*(1-p))
    b0 = Kc*(tau*(1-p) - T*p)
    return np.array([1.0, -(1+p), p]), np.array([b1, b0])

def disc_poles(wn, zeta, T):
    s = -zeta*wn + 1j*wn*np.sqrt(1-zeta**2)
    return np.real(np.poly([np.exp(s*T), np.exp(np.conj(s)*T)]))

def dioph(A, B, rhs, nR1, nS):
    """Resuelve A*R1 + B*S = rhs, R1 mónico de grado nR1, S de grado nS (coef. descendentes)."""
    n = len(rhs)
    cols = []
    for i in range(1, nR1+1):                      # coeficientes no líderes de R1
        e = np.zeros(nR1+1); e[i] = 1
        c = np.convolve(A, e); cols.append(np.pad(c, (n-len(c), 0)))
    for i in range(nS+1):
        e = np.zeros(nS+1); e[i] = 1
        c = np.convolve(B, e); cols.append(np.pad(c, (n-len(c), 0)))
    M = np.array(cols).T
    lead = np.convolve(A, np.r_[1.0, np.zeros(nR1)]); lead = np.pad(lead, (n-len(lead), 0))
    x = np.linalg.solve(M[1:], (rhs - lead)[1:])  # el coeficiente líder ya cuadra (mónico)
    return np.r_[1.0, x[:nR1]], x[nR1:]

def rst_design(kind, plant=PLANT0, wn=None, zeta=None, ao=None):
    """Devuelve (R, S, T) del RST para el lazo de la cámara.
    kind: 'A'  = diseño del curso (cancela el cero de muestreo), sin integrador
          'B'  = conserva el cero (B+ = 1), sin integrador
          'BI' = conserva el cero + acción integral (R con factor z-1)"""
    wn = wn or WN; zeta = zeta or ZETA
    ao = ao if ao is not None else np.exp(-2*wn*T)      # polos del observador ~2x más rápidos
    A, B = zoh_plant(plant['Kc'], plant['tau'], T)
    Am   = disc_poles(wn, zeta, T)
    if kind == 'A':
        b1, b0 = B
        R  = np.array([1.0, b0/b1])                       # R = B+
        S  = (Am[1:] - A[1:]) / b1                        # s1, s0
        # B_m: discretizar G_m(s) = wn^2/(s^2+2 zeta wn s+wn^2) (lo que hace el curso)
        from scipy.signal import cont2discrete
        num, den, _ = cont2discrete(([wn**2], [1, 2*zeta*wn, wn**2]), T, method='zoh')
        Bm = np.ravel(num)[-2:]
        Tp = Bm / b1
    elif kind == 'B':
        Ao = np.array([1.0, -ao])
        R, S = dioph(A, B, np.convolve(Am, Ao), nR1=1, nS=1)
        Km = np.polyval(Am, 1) / np.polyval(B, 1)
        Tp = Km*Ao
    elif kind == 'BI':
        Ao = np.convolve([1.0, -ao], [1.0, -ao])
        Aint = np.convolve(A, [1.0, -1.0])                # A·(z-1)
        R1, S = dioph(Aint, B, np.convolve(Am, Ao), nR1=1, nS=2)
        R = np.convolve(R1, [1.0, -1.0])                  # R = (z-1)·R1
        Km = np.polyval(Am, 1) / np.polyval(B, 1)
        Tp = Km*Ao
    return R, S, Tp

class RST:
    """Ley R u = T yr - S y en ecuación en diferencias:
         u(k) = sum T_i yr(k-i) - sum S_i y(k-i) - sum_{i>=1} R_i u(k-i)
    Anti-windup: la recursión usa la u YA SATURADA (equivale a A_aw = z^n, como el PI incremental)."""
    def __init__(self, R, S, Tp):
        n = len(R)                                   # grad(R) >= grad(S), grad(T): controlador causal
        pad = lambda p: np.pad(np.asarray(p, float), (n-len(p), 0))
        self.R, self.S, self.T = pad(R), pad(S), pad(Tp)
        self.yr = np.zeros(n); self.y = np.zeros(n); self.u = np.zeros(n)
    def step(self, yr, y):
        self.yr = np.r_[yr, self.yr[:-1]]; self.y = np.r_[y, self.y[:-1]]
        return self.T @ self.yr - self.S @ self.y - self.R[1:] @ self.u[:-1]
    def commit(self, u_aplicada):
        self.u = np.r_[u_aplicada, self.u[:-1]]

# ------------------------------------------------------------------ perturbación del cuerpo
def body_profile(scenario, seed=1):
    """Devuelve psib, wb, ab en la malla fina. scenario 'S1' (oscilación torsional, sin giro neto)
    o 'S2' (giro continuo + oscilación). Más un componente aleatorio tipo ráfaga (OU)."""
    dt = T/NSUB; t = np.arange(0, TF+T, dt)
    rng = np.random.default_rng(seed)
    if scenario == 'S1':
        # sin giro neto (rigidez de las cuerdas, k_r > 0): oscilación torsional + oscilador amortiguado
        # excitado por ruido (par aerodinámico aleatorio). El rumbo queda ACOTADO.
        wt, zt = 2*np.pi*0.4, 0.15
        x = np.zeros_like(t); v = np.zeros_like(t)
        for i in range(1, len(t)):
            v[i] = v[i-1] + (-wt**2*x[i-1] - 2*zt*wt*v[i-1])*dt + np.sqrt(dt)*rng.standard_normal()
            x[i] = x[i-1] + v[i]*dt
        sc_ = (10*D2R)/x.std(); x *= sc_; v *= sc_          # desviación típica del componente aleatorio: 10°
        wb = (40*D2R)*(2*np.pi*0.3)*np.cos(2*np.pi*0.3*t) \
           + (15*D2R)*(2*np.pi*1.1)*np.cos(2*np.pi*1.1*t + 1) + v
        psib0 = (40*D2R)*np.sin(2*np.pi*0.3*t) + (15*D2R)*np.sin(2*np.pi*1.1*t + 1) + x
        return t, psib0, wb, np.gradient(wb, dt)
    else:
        # con destorcedor o paracaídas que gira: giro continuo + oscilación + ráfagas (OU en la velocidad)
        tou, sig = 0.5, 15*D2R
        g = np.zeros_like(t)
        for i in range(1, len(t)):
            g[i] = g[i-1] - g[i-1]/tou*dt + sig*np.sqrt(2*dt/tou)*rng.standard_normal()
        spin = np.where(t < 5, 30, 30 + 60*np.clip(t-5, 0, 1))*D2R          # 30 -> 90 °/s al abrir paneles
        wb = spin + (20*D2R)*(2*np.pi*0.5)*np.cos(2*np.pi*0.5*t) + g
    psib = np.cumsum(wb)*dt
    ab = np.gradient(wb, dt)
    return t, psib, wb, ab

def ref_profile(tk):
    """Rumbo pedido: 0° y giro de 90° a los 30 s (C11), suavizado (rampa coseno de 1 s)."""
    s = np.clip((tk-30.0)/1.0, 0, 1)
    return (90*D2R)*(0.5 - 0.5*np.cos(np.pi*s))

# ------------------------------------------------------------------ simulación
def simulate(ctrl, scenario, plant=PLANT0, Kc_hat=None, seed=1, mag_err=True, tswitch=None, plant2=None,
             srv_range=90, srv_div=2, srv_K=40.0):
    """ctrl: 'servo' | 'A' | 'B' | 'BI' | 'BI+FF' | 'BI+FFa' | 'cascada'
    'BI+FFa' = prealimentación con Kc estimada en vuelo (RLS escalar sobre señales filtradas).
    plant: planta verdadera (el diseño siempre usa PLANT0).  plant2/tswitch: cambio de planta en vuelo."""
    Kc_hat = Kc_hat or PLANT0['Kc']
    t, psib, wb, ab = body_profile(scenario, seed)
    rng = np.random.default_rng(seed+100)
    dt = T/NSUB; N = int(round(TF/T))
    # --- sensores (supuestos; ver tabla de la nota)
    bias_g = 0.5*D2R                 # sesgo del giróscopo (supuesto; L-10 a L-15, no validados)
    sig_g  = 0.1*D2R                 # ruido del giróscopo por muestra
    sig_m  = 0.9*D2R                 # ruido del rumbo por muestra: LIS3MDL en Monterey (derivados/caracterizacion-sensores.csv)
    q_enc  = 2*np.pi/4096            # codificador de 12 bits (multivuelta por software)
    # --- estimador de rumbo (observador ψ, b = filtro complementario): polos s^2 + l1 s + l2
    we, ze = 0.5, 0.7; l1, l2 = 2*ze*we, we**2
    th, thd = 0.0, 0.0               # estado de la cámara relativo al cuerpo
    hist_th, hist_thd = [0.0], [0.0] # historial en los instantes de muestreo (para la latencia)
    psi_hat, b_hat = None, 0.0
    if ctrl in ('A', 'B', 'BI', 'BI+FF', 'BI+FFa'):
        rst = RST(*rst_design('BI' if ctrl.startswith('BI') else ctrl))
    # RLS escalar de Kc:  v_f ≈ Kc·u_f  (v = velocidad relativa del codificador; filtro pasabajos 1 rad/s)
    a_f = np.exp(-1.0*T); vf = uf = 0.0; Pk, lam_k = 1e3, 0.999
    th_prev, u_prev = 0.0, 0.0
    Kc_est = Kc_hat
    Kp_r, Ti_r, Kpsi = 0.1, PLANT0['tau'], 8.0          # cascada: PI de velocidad + P de ángulo
    integ = 0.0
    th_cmd, srv_lim, srv_rate, srv_db = 0.0, srv_range*D2R, 600*D2R, 0.5*D2R   # servo de hobby
    log = dict(t=[], e=[], e_ctrl=[], u=[], th=[], thq=[], w=[], kc=[])
    u = 0.0
    for k in range(N):
        i0 = k*NSUB; tk = t[i0]
        Kc, tau = (plant2['Kc'], plant2['tau']) if (tswitch is not None and tk >= tswitch) \
                  else (plant['Kc'], plant['tau'])
        # ---------- medición: la IMU entrega el dato de la muestra anterior (1 muestra de latencia)
        j = max(i0 - NSUB, 0); kj = max(k-1, 0)
        merr = (1.5*D2R + 2.0*D2R*np.sin(2*np.pi*0.4*tk)) if mag_err else 0.0
        if ctrl != 'cascada':                             # IMU en el CUERPO
            w_meas  = wb[j] + bias_g + sig_g*rng.standard_normal()
            psi_mag = psib[j] + merr + sig_m*rng.standard_normal()
        else:                                             # IMU en la CÁMARA: mide ψc = ψb + θ
            w_meas  = wb[j] + hist_thd[kj] + bias_g + sig_g*rng.standard_normal()
            psi_mag = psib[j] + hist_th[kj] + merr + sig_m*rng.standard_normal()
        w_meas = np.round(w_meas/(D2R/16))*(D2R/16)       # 16 LSB por °/s
        th_enc = np.round(th/q_enc)*q_enc
        # ---------- estimador de rumbo (del cuerpo, o de la cámara en 'cascada')
        if psi_hat is None:
            psi_hat = psi_mag
        innov = wrap(psi_mag - psi_hat)
        psi_hat += T*(w_meas - b_hat + l1*innov)
        b_hat   += -T*l2*innov
        w_hat = w_meas - b_hat
        yr = ref_profile(tk)
        psic_true = psib[i0] + th
        # ---------- ley de control
        if ctrl == 'servo':
            if k % srv_div == 0:                          # tramas PWM: 50 Hz (srv_div=2) o 100 Hz (1)
                th_cmd = np.clip(wrap(yr - psi_hat), -srv_lim, srv_lim)
            u = 0.0; y_ctrl = psi_hat + th
        elif ctrl == 'cascada':
            wc_ref = Kpsi*wrap(yr - psi_hat) + (ref_profile(tk+T) - yr)/T
            ew = wc_ref - w_hat
            u_uns = Kp_r*(ew + integ/Ti_r)
            u = float(np.clip(u_uns, -UMAX, UMAX))
            if abs(u_uns) < UMAX: integ += T*ew           # anti-windup (integración condicional)
            y_ctrl = psi_hat
        else:
            y_ctrl = psi_hat + th_enc                     # ψc estimado = ψb estimado + codificador
            v = rst.step(yr, y_ctrl)
            if ctrl == 'BI+FFa':                          # adaptar SOLO la ganancia identificable
                vf = a_f*vf + (1-a_f)*(th_enc - th_prev)/T
                uf = a_f*uf + (1-a_f)*u_prev
                g = Pk*uf/(lam_k + uf*Pk*uf); Kc_est += g*(vf - uf*Kc_est); Pk = (Pk - g*uf*Pk)/lam_k
                Kc_est = float(np.clip(Kc_est, 5.0, 200.0))     # proyección: signo y rango conocidos
            uff = -w_hat/(Kc_est if ctrl == 'BI+FFa' else Kc_hat) if ctrl in ('BI+FF', 'BI+FFa') else 0.0
            u = float(np.clip(v + uff, -UMAX, UMAX))
            rst.commit(u - uff)
            th_prev, u_prev = th_enc, u
        # ---------- planta (RK4, u retenida = ZOH)
        if ctrl == 'servo':
            for i in range(i0, i0+NSUB):                  # servo no retro-conducible: ignora ψb''
                err = th_cmd - th
                rate = 0.0 if abs(err) < srv_db else np.clip(srv_K*err, -srv_rate, srv_rate)
                th += rate*dt; thd = rate
        else:
            x = np.array([th, thd])
            for i in range(i0, i0+NSUB):
                a = ab[i]
                f = lambda x: np.array([x[1], (Kc*u - x[1])/tau - a])
                k1 = f(x); k2 = f(x+dt/2*k1); k3 = f(x+dt/2*k2); k4 = f(x+dt*k3)
                x = x + dt/6*(k1+2*k2+2*k3+k4)
            th, thd = x
        hist_th.append(th); hist_thd.append(thd)
        log['t'].append(tk); log['e'].append(wrap(psic_true - yr))
        log['e_ctrl'].append(wrap(y_ctrl - yr)); log['u'].append(u); log['th'].append(th)
        log['thq'].append(th_enc); log['w'].append(w_meas); log['kc'].append(Kc_est if ctrl == 'BI+FFa' else np.nan)
    return {k_: np.array(v_) for k_, v_ in log.items()}

def metrics(L, t0=5.0, turn=(30.0, 32.0)):
    """C8: error de rumbo REAL de la cámara (ψc - ψref) fuera de la ventana del giro comandado (C11).
    t_giro: tiempo desde el comando hasta que el error de CONTROL queda < 2° (el error real nunca baja
    del piso del estimador)."""
    tt = L['t']
    m = (tt >= t0) & ~((tt >= turn[0]) & (tt < turn[1]))
    e = np.abs(L['e'][m])*R2D
    ec = np.abs(L['e_ctrl'][m])*R2D
    du = np.diff(L['u'][tt >= t0])
    w = (tt >= turn[0]) & (tt < turn[0] + 5)
    bad = np.where(np.abs(L['e_ctrl'][w])*R2D > 2)[0]
    t_giro = (tt[w][bad[-1]] - turn[0] + T) if len(bad) and bad[-1] < w.sum()-1 else \
             (0.0 if not len(bad) else np.nan)
    return dict(max_e=e.max(), rms_e=np.sqrt(np.mean(e**2)), viol=100*np.mean(e > 10),
                max_ec=ec.max(), rms_du=np.sqrt(np.mean(du**2)), u_max=np.abs(L['u'][tt >= t0]).max(),
                t_giro=t_giro)


# ------------------------------------------------------------------ identificabilidad en vuelo
def rls(Y, Phi, lam=0.99):
    n = Phi.shape[1]; P = 1e3*np.eye(n); th = np.zeros(n); th[2] = 0.01   # b1 ≠ 0 con su signo
    H = []
    for y, phi in zip(Y, Phi):
        K = P @ phi/(lam + phi @ P @ phi); th = th + K*(y - phi @ th); P = (P - np.outer(K, phi @ P))/lam
        H.append(th.copy())
    return np.array(H)

def ident_6p(th, u, w, k0=1000):
    """ARX extendido: θ(k) = -a1 θ(k-1) - a0 θ(k-2) + b1 u(k-1) + b0 u(k-2) + c1 ω(k-1) + c0 ω(k-2)
    (el giro del cuerpo ω entra como ENTRADA MEDIDA; sin ese regresor el RLS queda sesgado)."""
    k = np.arange(2, len(th))
    Phi = np.c_[-th[k-1], -th[k-2], u[k-1], u[k-2], w[k-1], w[k-2]]
    est = rls(th[k], Phi)[k0:].mean(axis=0)
    M = Phi[k0:]/np.linalg.norm(Phi[k0:], axis=0)
    a0, b1, b0 = est[1], est[2], est[3]
    Kc = (b1 + b0)/(T*(1 - a0)); tau = -T/np.log(a0) if 0 < a0 < 1 else np.nan
    return np.linalg.cond(M.T @ M), Kc, tau

def kc_hat(L, wc=1.0, lam=0.999):
    v = np.r_[0, np.diff(L['thq'])]/T; u = np.r_[0, L['u'][:-1]]
    a = np.exp(-wc*T); vf = uf = 0.0; P, K = 1e3, 10.0; H = []
    for vk, uk in zip(v, u):
        vf = a*vf + (1-a)*vk; uf = a*uf + (1-a)*uk
        g = P*uf/(lam + uf*P*uf); K += g*(vf - uf*K); P = (P - g*uf*P)/lam; H.append(K)
    return np.array(H)

def identificabilidad():
    """(a) lazo abierto + SBPA valida la estructura; (b) en lazo cerrado los regresores quedan colineales;
    (c) la ganancia de velocidad Kc sí es identificable."""
    filas = []
    t, psib, wb, ab = body_profile('S2')
    w_avg = lambda n: np.array([wb[i*NSUB:(i+1)*NSUB].mean() for i in range(n)])   # ω equivalente ZOH
    N = int(TF/T)
    rng = np.random.default_rng(3)
    u = np.repeat(rng.choice([-0.2, 0.2], N//2 + 1), 2)[:N]
    th = np.zeros(N); x = np.zeros(2); dt = T/NSUB
    for k in range(N):
        th[k] = x[0]
        for i in range(k*NSUB, (k+1)*NSUB):
            f = lambda x: np.array([x[1], (30*u[k] - x[1])/0.1 - ab[i]])
            k1 = f(x); k2 = f(x+dt/2*k1); k3 = f(x+dt/2*k2); k4 = f(x+dt*k3); x = x + dt/6*(k1+2*k2+2*k3+k4)
    c, Kc, tau = ident_6p(th, u, w_avg(N))
    filas.append(('a_lazo_abierto_SBPA', c, Kc, tau, np.nan))
    for ctrl, name in (('BI', 'b_lazo_cerrado_L2'), ('BI+FF', 'b_lazo_cerrado_L3')):
        L = simulate(ctrl, 'S2')
        c, Kc, tau = ident_6p(L['th'], L['u'], w_avg(len(L['t'])))
        r = np.corrcoef(L['u'][500:], w_avg(len(L['t']))[500:])[0, 1]
        filas.append((name, c, Kc, tau, r))
    for scn in ('S1', 'S2'):
        for pl in (dict(Kc=21, tau=0.1), dict(Kc=30, tau=0.1), dict(Kc=60, tau=0.5)):
            L = simulate('BI+FF', scn, plant=pl); H = kc_hat(L)
            filas.append((f"c_Kc_escalar_{scn}_Kc{pl['Kc']}_tau{pl['tau']}", np.nan, H[L['t'] > 35].mean(), np.nan, np.nan))
    return filas

if __name__ == '__main__':
    import csv, os
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    os.makedirs('derivados', exist_ok=True); os.makedirs('salida/figuras', exist_ok=True)
    pre = 'diseno-estabilizacion-camara'
    print('Diseños RST (planta nominal Kc=30, tau=0.1 s; T=0.01 s; wn=20 rad/s, zeta=0.7):')
    for kind in ('A', 'B', 'BI'):
        R, S, Tp = rst_design(kind)
        print(f'  {kind:2s} R={np.round(R, 4)}  S={np.round(S, 3)}  T={np.round(Tp, 3)}')
    A, B = zoh_plant(**PLANT0, T=T)
    print(f'  cero de muestreo z0 = {-B[1]/B[0]:.4f}')
    ctrls = [('servo', 'L0 servo ±90° 50 Hz', dict(srv_range=90)), ('servo', 'L0 servo ±180° 50 Hz', dict(srv_range=180)),
             ('A', 'L1a RST cancela el cero', {}), ('B', 'L1b RST conserva el cero', {}),
             ('BI', 'L2 RST + integrador', {}), ('BI+FF', 'L3 L2 + FF giróscopo', {}),
             ('cascada', 'L4 cascada IMU en cámara', {}), ('BI+FFa', 'L5 L3 con Kc adaptada', {})]
    logs = {}
    with open(f'derivados/{pre}-metricas.csv', 'w', newline='') as fcsv:
        wr = csv.writer(fcsv)
        wr.writerow(['escenario', 'ley', 'max_e_deg', 'rms_e_deg', 'pct_t_mayor_10deg', 'max_e_ctrl_deg', 'rms_du_mV'])
        for scn in ('S1', 'S2'):
            print(f'\n=== Escenario {scn} ===')
            print(f"  {'ley':26s} {'max|e|°':>7s} {'rms e°':>6s} {'%>10°':>6s} {'max|ec|°':>8s} {'rmsΔu mV':>8s}")
            for c, name, kw in ctrls:
                L = simulate(c, scn, **kw); m = metrics(L); logs[(scn, name)] = L
                print(f"  {name:26s} {m['max_e']:7.2f} {m['rms_e']:6.2f} {m['viol']:6.1f} {m['max_ec']:8.2f} {m['rms_du']*1000:8.1f}")
                wr.writerow([scn, name, f"{m['max_e']:.3f}", f"{m['rms_e']:.3f}", f"{m['viol']:.2f}", f"{m['max_ec']:.3f}", f"{m['rms_du']*1000:.2f}"])
    print('\n=== Robustez (S2): planta real distinta de la de diseño ===')
    with open(f'derivados/{pre}-robustez.csv', 'w', newline='') as fcsv:
        wr = csv.writer(fcsv); wr.writerow(['planta_real', 'ley', 'max_e_deg', 'max_e_ctrl_deg', 'Kc_estimada'])
        for name, pl in [('Kc=30 tau=0.1', dict(Kc=30, tau=0.1)), ('Kc=21 tau=0.1', dict(Kc=21, tau=0.1)),
                         ('Kc=60 tau=0.1', dict(Kc=60, tau=0.1)), ('Kc=60 tau=0.5', dict(Kc=60, tau=0.5))]:
            for c in ('BI+FF', 'BI+FFa'):
                L = simulate(c, 'S2', plant=pl); m = metrics(L)
                kc_ = np.nanmean(L['kc'][L['t'] > 35]) if c == 'BI+FFa' else np.nan
                ley = 'L3' if c == 'BI+FF' else 'L5'
                print(f"  {name:14s} {ley}  max|e|={m['max_e']:5.2f}°  max|e_ctrl|={m['max_ec']:5.2f}°" + (f"  Kc^={kc_:6.2f}" if c == 'BI+FFa' else ''))
                wr.writerow([name, ley, f"{m['max_e']:.3f}", f"{m['max_ec']:.3f}", '' if np.isnan(kc_) else f'{kc_:.2f}'])
    print('\n=== Identificabilidad en vuelo ===')
    with open(f'derivados/{pre}-identificabilidad.csv', 'w', newline='') as fcsv:
        wr = csv.writer(fcsv); wr.writerow(['experimento', 'cond_PhiTPhi', 'Kc_estimada', 'tau_estimada_s', 'corr_u_wb'])
        for nombre, c, Kc, tau, r in identificabilidad():
            print(f"  {nombre:34s} cond={c:9.2e}  Kc^={Kc:6.2f}  tau^={tau:6.3f}  corr(u,ωb)={r:+.2f}")
            fmt = lambda v, f: '' if np.isnan(v) else format(v, f)
            wr.writerow([nombre, fmt(c, '.3e'), fmt(Kc, '.3f'), fmt(tau, '.4f'), fmt(r, '.3f')])
    # figura: error real de la cámara en S2 (L1b, L2, L3) y voltaje L1a vs L1b
    fig, ax = plt.subplots(2, 1, figsize=(10, 7))
    for name, col in (('L1b RST conserva el cero', 'tab:orange'), ('L2 RST + integrador', 'tab:blue'), ('L3 L2 + FF giróscopo', 'tab:green')):
        L = logs[('S2', name)]; ax[0].plot(L['t'], L['e']*R2D, color=col, lw=0.8, label=name)
    ax[0].axhline(10, color='k', ls='--', lw=0.8); ax[0].axhline(-10, color='k', ls='--', lw=0.8)
    ax[0].set_ylabel('error de rumbo de la cámara [°]'); ax[0].set_ylim(-15, 15); ax[0].legend(loc='upper right'); ax[0].grid(alpha=.3)
    ax[0].axvspan(30, 32, color='gray', alpha=0.2, label='giro comandado de 90° (C11): no cuenta para C8')
    ax[0].legend(loc='upper right', fontsize=8)
    ax[0].set_title('Escenario S2 (giro continuo) · límites de C8 en ±10°'); ax[0].set_xlabel('t [s]')
    for name, col in (('L1a RST cancela el cero', 'tab:red'), ('L1b RST conserva el cero', 'tab:orange')):
        L = logs[('S2', name)]; ax[1].plot(L['t'], L['u'], color=col, lw=0.6, label=name)
    ax[1].set_xlim(40, 42); ax[1].set_ylabel('u [V]'); ax[1].set_xlabel('t [s]'); ax[1].legend(loc='upper right'); ax[1].grid(alpha=.3)
    ax[1].set_title('Zumbido del cero cancelado (detalle de 2 s)')
    ax[0].set_xlim(0, 60)
    fig.tight_layout(); fig.savefig(f'salida/figuras/{pre}.png', dpi=120)
    print(f'\nEscribe derivados/{pre}-metricas.csv, -robustez.csv, -identificabilidad.csv y salida/figuras/{pre}.png')
