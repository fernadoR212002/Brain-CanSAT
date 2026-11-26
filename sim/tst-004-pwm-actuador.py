"""TST-004. Efecto del PWM sobre el error de rumbo de L3 (motor) y L0 (servo).

Ejecutar desde la raíz con python3 sim/tst-004-pwm-actuador.py.
Sin fuente en raw/: las tensiones de batería, zonas muertas y características
del servo A2 son supuestos de simulación. No son mediciones del actuador.
"""

import csv
import importlib.util
import math
import sys
from pathlib import Path

import numpy as np


RUTA_BASE = Path(__file__).resolve().with_name("diseno-estabilizacion-camara.py")
SALIDA = RUTA_BASE.parent.parent / "derivados/tst-004-pwm-actuador-python.csv"
spec = importlib.util.spec_from_file_location("estabilizacion_camara", RUTA_BASE)
base = importlib.util.module_from_spec(spec)
escritura_previa = sys.dont_write_bytecode
try:
    sys.dont_write_bytecode = True
    spec.loader.exec_module(base)
finally:
    sys.dont_write_bytecode = escritura_previa

T, NSUB, TF = base.T, base.NSUB, base.TF
D2R, PLANT0, UMAX = base.D2R, base.PLANT0, base.UMAX
wrap, body_profile, ref_profile = base.wrap, base.body_profile, base.ref_profile
RST, rst_design, metrics = base.RST, base.rst_design, base.metrics
VBAT_NOM = 7.4
FRAME = 20e-3
P_CENTRO, P_SEMIRRECORRIDO = 1.5e-3, 0.9e-3
CASOS = {
    "B0": dict(bits=math.inf),
    "B1": dict(bits=8),
    "B2": dict(bits=10),
    "B3": dict(bits=11),
    "B4": dict(bits=11, dz=0.3),
    "B5": dict(bits=11, dz=0.6),
    "B6": dict(bits=11, vbat=6.4),
    "B7": dict(bits=11, dz=0.6, dz_hat=0.5),
    "B8": dict(bits=11, dz=0.6, dz_hat=0.7),
    "A0": dict(bits=16, rate_max=600, db=0.5),
    "A1": dict(bits=8, rate_max=600, db=0.5),
    "A2": dict(bits=16, rate_max=260, db=2),
}


def simulate_pwm(ctrl, scenario, *, bits, dz=0.0, dz_hat=0.0, vbat=VBAT_NOM,
                 vbat_hat=VBAT_NOM, rate_max=600, db=0.5, seed=1):
    """simulate() restringida a los dos lazos, con PWM antes de la planta."""
    if ctrl not in ("BI+FF", "servo"):
        raise ValueError(ctrl)
    motor = ctrl == "BI+FF"
    levels = None if bits == math.inf else 2**bits
    t, psib, wb, ab = body_profile(scenario, seed)
    rng = np.random.default_rng(seed + 100)
    dt = T / NSUB
    bias_g, sig_g, sig_m = 0.5 * D2R, 0.1 * D2R, 0.9 * D2R
    q_enc = 2 * np.pi / 4096
    we, ze = 0.5, 0.7
    l1, l2 = 2 * ze * we, we**2
    th = thd = th_cmd = b_hat = 0.0
    psi_hat = None
    Kc, tau = PLANT0["Kc"], PLANT0["tau"]
    if motor:
        rst = RST(*rst_design("BI"))
    srv_div, srv_K = 2, 40.0
    srv_lim, srv_rate, srv_db = 90 * D2R, rate_max * D2R, db * D2R
    log = dict(t=[], e=[], e_ctrl=[], u=[], u_ef=[])
    for k in range(int(round(TF / T))):
        i0 = k * NSUB
        tk = t[i0]
        j = max(i0 - NSUB, 0)
        merr = 1.5 * D2R + 2.0 * D2R * np.sin(2 * np.pi * 0.4 * tk)
        w_meas = wb[j] + bias_g + sig_g * rng.standard_normal()
        psi_mag = psib[j] + merr + sig_m * rng.standard_normal()
        w_meas = np.round(w_meas / (D2R / 16)) * (D2R / 16)
        th_enc = np.round(th / q_enc) * q_enc
        if psi_hat is None:
            psi_hat = psi_mag
        innov = wrap(psi_mag - psi_hat)
        psi_hat += T * (w_meas - b_hat + l1 * innov)
        b_hat += -T * l2 * innov
        w_hat = w_meas - b_hat
        yr = ref_profile(tk)
        psic_true = psib[i0] + th

        if motor:
            y_ctrl = psi_hat + th_enc
            v = rst.step(yr, y_ctrl)
            uff = -w_hat / Kc
            u = float(np.clip(v + uff, -UMAX, UMAX))
            rst.commit(u - uff)
            u_c = u + dz_hat * np.sign(u)
            duty = u_c / vbat_hat
            if levels is None and vbat == vbat_hat:
                u_ap = u_c  # Identidad exacta: evita el redondeo de (u_c / V) * V.
            else:
                d_q = duty if levels is None else round(duty * levels) / levels
                u_ap = vbat * d_q
            u_ef = np.sign(u_ap) * max(abs(u_ap) - dz, 0.0)
            x = np.array([th, thd])
            for i in range(i0, i0 + NSUB):
                a = ab[i]

                def f(x):
                    return np.array([x[1], (Kc * u_ef - x[1]) / tau - a])

                k1 = f(x)
                k2 = f(x + dt / 2 * k1)
                k3 = f(x + dt / 2 * k2)
                k4 = f(x + dt * k3)
                x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            th, thd = x
        else:
            if k % srv_div == 0:
                th_c = np.clip(wrap(yr - psi_hat), -srv_lim, srv_lim)
                if levels is None:  # Control de réplica de L0 sin cuantización.
                    th_cmd = th_c
                else:
                    p = P_CENTRO + (th_c / srv_lim) * P_SEMIRRECORRIDO
                    tick = FRAME / levels
                    p_q = round(p / tick) * tick
                    th_cmd = (p_q - P_CENTRO) / P_SEMIRRECORRIDO * srv_lim
            y_ctrl = psi_hat + th
            u, u_ef = 0.0, np.nan
            for i in range(i0, i0 + NSUB):
                err = th_cmd - th
                rate = 0.0 if abs(err) < srv_db else np.clip(srv_K * err, -srv_rate, srv_rate)
                th += rate * dt
                thd = rate
        log["t"].append(tk)
        log["e"].append(wrap(psic_true - yr))
        log["e_ctrl"].append(wrap(y_ctrl - yr))
        log["u"].append(u)
        log["u_ef"].append(u_ef)
    return {key: np.array(values) for key, values in log.items()}


def verificar(caso, escenario, ctrl, log):
    referencia = base.simulate(ctrl, escenario, seed=1, srv_range=90, srv_div=2)
    ideal = log if caso == "B0" else simulate_pwm(ctrl, escenario, bits=math.inf)
    for key in ("t", "e", "e_ctrl", "u"):
        np.testing.assert_array_equal(ideal[key], referencia[key])
    actual, ref = metrics(log), metrics(referencia)
    print(f"{caso} {escenario}: max_e={actual['max_e']:.9f}°, base={ref['max_e']:.9f}°, "
          f"Δ={actual['max_e'] - ref['max_e']:+.9f}°; "
          f"viol={actual['viol']:.5f}% (base {ref['viol']:.5f}%). "
          "Series t, e, e_ctrl y u idénticas a la base sin cuantización.", flush=True)


def fila(caso, escenario, ctrl, params, log):
    m = metrics(log)
    motor = ctrl == "BI+FF"
    du_ap = np.diff(log["u_ef"][log["t"] >= 5.0]) if motor else None
    return dict(
        actuador="motor" if motor else "servo", caso=caso, escenario=escenario,
        bits=params["bits"], dz_V=params.get("dz", 0.0) if motor else np.nan,
        dz_hat_V=params.get("dz_hat", 0.0),
        vbat_V=params.get("vbat", VBAT_NOM) if motor else np.nan,
        vbat_hat_V=VBAT_NOM if motor else np.nan,
        rate_max_dps=params.get("rate_max", np.nan), db_deg=params.get("db", np.nan),
        max_e_deg=m["max_e"], rms_e_deg=m["rms_e"], viol_pct=m["viol"],
        max_e_ctrl_deg=m["max_ec"], rms_du_mV=m["rms_du"] * 1000 if motor else np.nan,
        rms_du_ap_mV=np.sqrt(np.mean(du_ap**2)) * 1000 if motor else np.nan,
        u_max_V=m["u_max"] if motor else np.nan,
    )


def resolucion():
    apb = 80e6
    print("\nResolución PWM teórica con reloj APB de 80 MHz y batería nominal")
    print("actuador    Hz  bits   tick_µs    °/tick   paso_mV  bits_máx")
    for bits in (8, 10, 12, 14, 16):
        tick_us = FRAME * 1e6 / 2**bits
        print(f"servo       50  {bits:4d} {tick_us:9.5f} {tick_us / 10:9.6f}"
              f"         —  {math.floor(math.log2(apb / 50)):8d}")
    for hz, bits in ((1000, 8), (20000, 8), (20000, 10), (20000, 11)):
        step_mv = VBAT_NOM * 1000 / 2**bits
        print(f"motor    {hz:5d}  {bits:4d}         —         — {step_mv:9.5f}"
              f"  {math.floor(math.log2(apb / hz)):8d}")


def main():
    rows = []
    for caso, params in CASOS.items():
        ctrl = "BI+FF" if caso.startswith("B") else "servo"
        for escenario in ("S1", "S2"):
            log = simulate_pwm(ctrl, escenario, **params)
            if caso in ("B0", "A0"):
                verificar(caso, escenario, ctrl, log)
            rows.append(fila(caso, escenario, ctrl, params, log))

    with SALIDA.open("w", newline="", encoding="utf-8") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow({k: "NaN" if isinstance(v, float) and math.isnan(v) else v
                             for k, v in row.items()})

    print("\n" + " ".join(f"{k:>10}" for k in rows[0]))
    for row in rows:
        print(" ".join(f"{v:10.4f}" if isinstance(v, float) else f"{v:>10}"
                       for v in row.values()))
    resolucion()


if __name__ == "__main__":
    main()
