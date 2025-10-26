from __init__ import *
def run_injector_calculations():

    def compute_Zfu_inj_tc(gamma, Pc, Pup, Pe):
        term1 = (2 * gamma) / (gamma - 1)
        exp1 = (Pc / Pup) ** (2 / gamma)
        exp2 = (Pc / Pup) ** ((gamma + 1) / gamma)
        return term1 * (exp1 - exp2)

    def injector_hole_area(d_mm):
        d_m = d_mm / 1000
        return math.pi * d_m ** 2 / 4

    def mass_flow_per_hole(CD, A, Pup, Z, R, T, Mw):
        return CD * A * Pup * Z / ((R * T / Mw) ** 0.5)

    def number_of_injector_holes(mdot_total, CD, d_mm, Pup, Z, R, T, Mw):
        A = injector_hole_area(d_mm)
        m_dot_per_hole = mass_flow_per_hole(CD, A, Pup, Z, R, T, Mw)
        N = mdot_total / m_dot_per_hole
        return N, m_dot_per_hole

    # --- FUEL-RICH SIDE ---
    mdot_total_fu = 208.333        # total fuel-rich flow (kg/s)
    CD_fu = 0.8
    d_fu_mm = 5
    Pup_fu = 36e6
    Pc = 30e6
    Pe = 1e5
    gamma_fu = 1.1458
    R = 8314
    Mw_fu = 17.4
    T_fu = 765.5

    Z_fu = compute_Zfu_inj_tc(gamma_fu, Pc, Pup_fu, Pe)
    N_fu, mdot_fu_per_hole = number_of_injector_holes(mdot_total_fu, CD_fu, d_fu_mm, Pup_fu, Z_fu, R, T_fu, Mw_fu)

    # --- OXIDIZER-RICH SIDE ---
    CD_ox = 0.8
    Pup_ox = 36e6
    gamma_ox = 1.3176
    Mw_ox = 31.47
    T_ox = 679
    Z_ox = compute_Zfu_inj_tc(gamma_ox, Pc, Pup_ox, Pe)

    # Derived from mixture balance:
    mdot_ratio_ox_to_fu = 0.654   # one oxidizer-rich per one fuel-rich

    # Each set: 1 fuel-rich injector, 4 oxidizer-rich injectors
    mdot_ox_target_per_inj = mdot_fu_per_hole * mdot_ratio_ox_to_fu

    def find_diameter_for_mdot(target_mdot, CD, Pup, Z, R, T, Mw):
        d = 0.1  # initial guess (mm)
        for _ in range(10000):
            A = injector_hole_area(d)
            mdot = mass_flow_per_hole(CD, A, Pup, Z, R, T, Mw)
            if abs(mdot - target_mdot) < 1e-6:
                break
            d *= (target_mdot / mdot) ** 0.5
        return d, mdot

    d_ox_mm, mdot_ox_per_hole = find_diameter_for_mdot(mdot_ox_target_per_inj, CD_ox, Pup_ox, Z_ox, R, T_ox, Mw_ox)

    # Verification of local O/F
    O_F_fr = 0.38
    O_F_or = 41
    F_fr = 1 / (1 + O_F_fr) * mdot_fu_per_hole
    O_fr = O_F_fr * F_fr
    F_or = 1 / (1 + O_F_or) * mdot_ox_per_hole
    O_or = O_F_or * F_or
    OF_local = (O_fr + 4 * O_or) / (F_fr + 4 * F_or)

    print("=== Fuel-Rich Injector ===")
    print(f"Mass flow per hole: {mdot_fu_per_hole:.4f} kg/s")
    print(f"Number of fuel injectors: {N_fu:.1f}")

    print("\n=== Oxidizer-Rich Injector ===")
    print(f"Required mass flow per injector: {mdot_ox_target_per_inj:.4f} kg/s")
    print(f"Calculated oxidizer injector diameter: {d_ox_mm:.3f} mm")
    print(f"Actual mass flow per hole (verified): {mdot_ox_per_hole:.4f} kg/s")

    print(f"\nCheck — Local O/F from 1 FR + 4 OR injectors = {OF_local:.3f}")


run_injector_calculations()