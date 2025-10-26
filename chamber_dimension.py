import math
def calculate_chamber_dimensions():
    m_z          = 53.12        # total mass flow (kg/s)
    deltaP_inj   = 1.2e6        # injector ΔP = 12 bar

    C_smd        = 2.5          # empirical constant
    gamma_gas    = 1.1301       # from CEA
    Cstar        = 1837.0       # m/s
    p_c_val      = 60e5         # Pa (60 bar)

    rho_o        = 1140.0       # oxidiser density (kg/m^3)
    sigma_LOX    = 0.013        # N/m
    rho_LOX      = 1140.0       # kg/m³
    k_LOX        = 1327.8       # To be found s/m^2 
    D_pipe_LOX   = 0.4          # m

    rho_f        = 423.0        # fuel density (kg/m^3)
    sigma_LCH4   = 0.017        # N/m
    rho_LCH4     = 423.0        # kg/m³
    k_LCH4       = 376.34       # To be found s/m^2
    D_pipe_LCH4  = 0.4          # m

    L_star_CC    = 76.2886      # To be found
    D_chamber    = 4            # m
    # SMD calculations

    SMD_LOX_m   = C_smd * math.sqrt(sigma_LOX / rho_LOX) * (deltaP_inj ** (-0.25))
    SMD_LCH4_m  = C_smd * math.sqrt(sigma_LCH4 / rho_LCH4) * (deltaP_inj ** (-0.25))
    SMD_LOX_um  = SMD_LOX_m * 1e6
    SMD_LCH4_um = SMD_LCH4_m * 1e6
    t_res_LOX   = (k_LOX * SMD_LOX_m * SMD_LOX_m)/0.7
    t_res_LCH4  = (k_LCH4 * SMD_LCH4_m * SMD_LCH4_m)/0.7
    L_star_LOX  = Cstar * t_res_LOX
    L_star_LCH4 = Cstar * t_res_LCH4
    A_t_LOX     = (math.pi * D_pipe_LOX * D_pipe_LOX)/4
    A_t_LCH4     = (math.pi * D_pipe_LCH4 * D_pipe_LCH4)/4
    D_chamber_LOX   = 2 * (((t_res_LOX * A_t_LOX * 3 * Cstar) / (4 * math.pi)) ** (1/3))
    D_chamber_LCH4   = 2 * (((t_res_LCH4 * A_t_LCH4 * 3 * Cstar) / (4 * math.pi)) ** (1/3))

    # Main Combustion Chamber 

    A_t = Cstar * m_z / p_c_val
    L_CC = (4 * A_t * L_star_CC) / (math.pi * D_chamber * D_chamber)

    # PRINT 

    print("\n=== Gas Generator Dimensions ===")
    print(f"Diameter of Gas Generator LOX    : {D_chamber_LOX:.6g}")
    print(f"SMD LOX (microns)                : {SMD_LOX_um:.6g}")
    print(f"Diameter of Gas Generator LCH4   : {D_chamber_LCH4:.6g}")
    print(f"SMD LCH4 (microns)               : {SMD_LCH4_um:.6g}")

    print("\n=== Main Combustion Chamber Dimensions ===")
    print(f"Chamber Length (m)            : {L_CC:.6g}")


    print("\n(End)\n")

calculate_chamber_dimensions()