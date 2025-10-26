from __init__ import *

class engine_obsolete_2:
    def __init__(self,engine_name,override_inputs=True):
        self.engine_name=engine_name
        self.input_file="input files/engines/"+engine_name+".json"
        self.output_file="output files/engines/"+engine_name+".txt"
        with open(self.input_file) as file:
            self.data = json.load(file)
        self.read_fuel_data()

        if override_inputs:
            self.override_inputs()
        self.R_pb=[0.1,10]
        self.R_pbf=1
        self.R_pbo=1
        self.R=self.data["oxidiser by fuel"]

        self.m_z=self.data["m_z"]
        self.A_t=self.data["A_t"]
        self.p_f1=self.data["fuel tank pressure"]
        self.p_o1=self.data["oxidiser tank pressure"]
        self.p_c=self.m_z*self.cstar(self.R)/self.A_t

        self.eta_tf=self.data["fuel rich turbine efficiency"]
        self.eta_to=self.data["oxidiser rich turbine efficiency"]
        self.eta_pf=self.data["fuel pump efficiency"]
        self.eta_po=self.data["oxidiser pump efficiency"]
        
        self.rho_o=self.data["oxidiser density"]
        self.rho_f=self.data["fuel density"]
        self.p_pbf=self.data["fuel rich preburner pressure"]
        
        
        self.R_0=8.314
        
        self.ho=1e-1
        self.hf=1e-1

        self.C_ff=0.14       # Pressure drop loss coefficient between the fuel pump and the fuel-rich preburner
        self.C_oo=0.14       # Pressure drop loss coefficient between the oxidizer pump and the oxidizer-rich preburner
        self.C_f1=0.63       # Pressure drop loss coefficient between the fuel pump and fuel injector of the fuel-rich preburner
        self.C_o1=0       # Pressure drop loss coefficient between the oxidizer pump and oxidizer injector of the oxidizer-rich preburner
        self.C_f2=0       # Pressure drop loss coefficient between the fuel-rich preburner and the fuel-rich turbine
        self.C_o2=0       # Pressure drop loss coefficient between the oxidizer-rich preburner and the oxidizer-rich turbine
        self.C_f3=0.14       # Pressure drop loss coefficient between the fuel-rich turbine and the combustion chamber
        self.C_o3=0.43       # Pressure drop loss coefficient between the oxidizer-rich turbine and the combustion chamber
        #self.C_f4=0        Pressure drop loss coefficient between the fuel-rich preburner and the oxidizer-rich preburner
        #self.C_o4=0        Pressure drop loss coefficient between the oxidizer-rich preburner and the fuel-rich preburner
        self.C_fo=0.14       # Pressure drop loss coefficient between the oxidizer pump and the fuel-rich preburner
        self.C_of=0.45       # Pressure drop loss coefficient between the fuel pump and the oxidizer-rich preburner

        self.p_pbo=(1+self.C_fo)*self.p_pbf/(1+self.C_oo)

        self.max_residual=0

        self.symbols = ["D_E", "Isp", "Thrust", "p_c", "m_f", "m_o", "m_tf", "m_to", "m_ff", "m_fo", "m_of", "m_oo", "p_f2", "p_o2", "p_f3", "p_o3", "p_f4", "p_o4", "pi_tf", "pi_to", "delta_p_f", "delta_p_o", "P_f", "P_o", "g_f", "g_o", "gamma_pbf", "gamma_pbo", "M_pbf", "M_pbo", "T_pbf", "T_pbo", "R_pbf", "R_pbo"]

    def override_inputs(self):
        self.data["m_z"]=self.data["Thrust"]/self.isp(self.data["oxidiser by fuel"])
        self.data["A_t"]=self.data["m_z"]*self.cstar(self.data["oxidiser by fuel"])/self.data["p_c"]

    
    def read_fuel_data(self):
        self.fuel_data=np.genfromtxt("data files/LOXMETHANE cleaned.txt")[1:].T
        self.fuel_data_heads=["O/F","temp","isp","mw","cstar","gamma"]
           
    def temperature(self,R):
        ratios=self.fuel_data[0]
        ans=self.fuel_data[1]
        if ratios[0]<=R:
            return ans[0]
        for i in range(1,len(ratios)-1):
            if ratios[i]<=R:
                return (ans[i+1]-ans[i])/(ratios[i+1]-ratios[i])*(R-ratios[i])+ans[i]
        return ans[len(ratios)-1]  

    def isp(self,R):
        ratios=self.fuel_data[0]
        ans=self.fuel_data[2]
        if ratios[0]<=R:
            return ans[0]
        for i in range(1,len(ratios)-1):
            if ratios[i]<=R:
                return (ans[i+1]-ans[i])/(ratios[i+1]-ratios[i])*(R-ratios[i])+ans[i]
        return ans[len(ratios)-1]    
      
    def mol_w(self,R):
        ratios=self.fuel_data[0]
        ans=self.fuel_data[3]/1000
        if ratios[0]<=R:
            return ans[0]
        for i in range(1,len(ratios)-1):
            if ratios[i]<=R:
                return (ans[i+1]-ans[i])/(ratios[i+1]-ratios[i])*(R-ratios[i])+ans[i]
        return ans[len(ratios)-1]   

    def cstar(self,R):
        ratios=self.fuel_data[0]
        ans=self.fuel_data[4]
        if ratios[0]<=R:
            return ans[0]
        for i in range(1,len(ratios)-1):
            if ratios[i]<=R:
                return (ans[i+1]-ans[i])/(ratios[i+1]-ratios[i])*(R-ratios[i])+ans[i]
        return ans[len(ratios)-1]    
     
    def gamma(self,R):
        ratios=self.fuel_data[0]
        ans=self.fuel_data[5]
        if ratios[0]<=R:
            return ans[0]
        for i in range(1,len(ratios)-1):
            if ratios[i]<=R:
                return (ans[i+1]-ans[i])/(ratios[i+1]-ratios[i])*(R-ratios[i])+ans[i]
        return ans[len(ratios)-1]    
    
    def gas_constant(self,R):
        ratios=self.fuel_data[0]
        ans=self.fuel_data[3]/1000
        if ratios[0]<=R:
            return self.R_0/ans[0]
        for i in range(1,len(ratios)-1):
            if ratios[i]<=R:
                return self.R_0/((ans[i+1]-ans[i])/(ratios[i+1]-ratios[i])*(R-ratios[i])+ans[i])
        return self.R_0/ans[len(ratios)-1]
    
    def exit_diameter(self):

        p_p0=1e5/self.p_c
        gamma=self.gamma(self.R)
        # Define the isentropic pressure ratio function
        def pressure_ratio(M):
            return (1 + 0.5*(gamma -1)*M**2)**(-gamma/(gamma -1))

        # Define function whose root we want: pressure_ratio(M) - p_p0 = 0
        def f(M):
            return pressure_ratio(M) - p_p0

        # Solve for subsonic Mach (M < 1)
        #sol_sub = root_scalar(f, bracket=[1e-5, 1])
        #if not sol_sub.converged:
        #    raise ValueError("Subsonic Mach solving failed")
        #M_sub = sol_sub.root

        # Solve for supersonic Mach (M >1)
        sol_sup = root_scalar(f, bracket=[1.0001, 20])
        if not sol_sup.converged:
            raise ValueError("Supersonic Mach solving failed")
        M_sup = sol_sup.root

        # Area-Mach relation
        def area_ratio(M):
            return (1/M) * ( (2/(gamma+1)*(1 + 0.5*(gamma-1)*M**2)) ) ** ( (gamma+1)/(2*(gamma-1)) )

        #A_Astar_sub = area_ratio(M_sub)
        A_Astar_sup = area_ratio(M_sup)
        A_e=A_Astar_sup*self.A_t
        d_e=(A_e/pi)**0.5*2
        return d_e


    '''
    def c_star(self):
        #self.c_star=((self.data['R_c']*self.data['T_c']/self.data['gamma_c'])**0.5)/(2/(self.data['gamma_c']+1))**((self.data['gamma_c']+1)/2/(self.data['gamma_c']-1))
        return ((self.gas_constant(self.R)*self.temperature(self.R)/self.gamma(self.R))**0.5)/(2/(self.gamma(self.R)+1))**((self.gamma(self.R)+1)/2/(self.gamma(self.R)-1)) 
    
    def delta_p_f(self,R_pbo,R_pbf):
        return (R_pbo-self.R)*(1+R_pbf)/(R_pbo-R_pbf)*(self.eta_tf*self.rho_f*self.eta_pf)*(self.gamma_pbf/(self.gamma_pbf-1))*(self.R_0/self.M_pbf)*self.T_pbf*(1-(1/self.data['pi_tf'])**(self.gamma_pbf-1/self.gamma_pbf))
    
    def delta_p_o(self,R_pbo,R_pbf):
        return (self.R-R_pbf)*(1+R_pbf)/(R_pbo-R_pbf)*(self.eta_to*self.rho_o*self.eta_po)*(self.gamma_pbo/(self.gamma_pbo-1))*(self.R_0/self.M_pbo)*self.T_pbo*(1-(1/self.data['pi_to'])**(self.gamma_pbo-1/self.gamma_pbo))
    '''

    def delta_p_f(self,p_pbf):
        return (1+self.C_ff)*p_pbf+self.C_f1*self.p_c-self.p_f1
    
    def delta_p_o(self,p_pbf):
        return (1+self.C_fo)*p_pbf-self.p_o1

    def pi_tf(self):
        return (self.p_pbf-self.C_f2*self.m_z*self.cstar(self.R)/self.A_t)/(self.m_z*self.cstar(self.R_pbf)/self.A_t*(1+self.C_f3))    

    def pi_to(self):
        return (self.p_pbo-self.C_o2*self.m_z*self.cstar(self.R)/self.A_t)/(self.m_z*self.cstar(self.R_pbf)/self.A_t*(1+self.C_o3))
    
    def Gf(self,R_pbo):
        gamma_pbf=self.gamma(self.R_pbf)
        gamma_pbo=self.gamma(R_pbo)
        M_pbf=self.mol_w(self.R_pbf)
        M_pbo=self.mol_w(R_pbo)
        T_pbf=self.temperature(self.R_pbf)
        T_pbo=self.temperature(R_pbo)
        #print(self.delta_p_f(self.p_pbf_k)/1e5,self.delta_p_o(self.p_pbf_k)/1e5,gamma_pbf,gamma_pbo,M_pbf,M_pbo,T_pbf,T_pbo)
        #c1=self.delta_p_f(R_pbo,self.R_pb[0])/self.eta_tf/self.rho_f/self.eta_pf
        c1=self.delta_p_f(self.p_pbf)/self.eta_tf/self.rho_f/self.eta_pf
        #c2=self.delta_p_o(R_pbo,self.R_pb[0])/self.eta_to/self.rho_o/self.eta_po
        c2=self.delta_p_o(self.p_pbf)/self.eta_to/self.rho_o/self.eta_po
        w_f=gamma_pbf/(gamma_pbf-1)*(self.R_0/M_pbf)*T_pbf*(1-(1/self.pi_tf())**(gamma_pbf-1/gamma_pbf))
        w_o=gamma_pbo/(gamma_pbo-1)*(self.R_0/M_pbo)*T_pbo*(1-(1/self.pi_to())**(gamma_pbo-1/gamma_pbo))
        return (self.R*c2*R_pbo/(1+R_pbo)-self.R*w_o)/(self.R*c2/(1+R_pbo)-w_o)
    
    def Go(self,R_pbf):        
        gamma_pbf=self.gamma(R_pbf)
        gamma_pbo=self.gamma(self.R_pbo)
        M_pbf=self.mol_w(R_pbf)
        M_pbo=self.mol_w(self.R_pbo)
        T_pbf=self.temperature(R_pbf)
        T_pbo=self.temperature(self.R_pbo)
        #c1=self.delta_p_f(R_pbo,self.R_pb[0])/self.eta_tf/self.rho_f/self.eta_pf
        c1=self.delta_p_f(self.p_pbf)/self.eta_tf/self.rho_f/self.eta_pf
        #c2=self.delta_p_o(R_pbo,self.R_pb[0])/self.eta_to/self.rho_o/self.eta_po
        c2=self.delta_p_o(self.p_pbf)/self.eta_to/self.rho_o/self.eta_po
        w_f=gamma_pbf/(gamma_pbf-1)*(self.R_0/M_pbf)*T_pbf*(1-(1/self.pi_tf())**(gamma_pbf-1/gamma_pbf))
        w_o=gamma_pbo/(gamma_pbo-1)*(self.R_0/M_pbo)*T_pbo*(1-(1/self.pi_to())**(gamma_pbo-1/gamma_pbo))
        return (-c1*R_pbf/(1+R_pbf)+self.R*w_f)/(-c1/(1+R_pbf)+w_f)
    
    def objective_function(self,x):
        self.R_pbf=x[0]
        self.R_pbo=x[1]
        errs=self.calculate_all_parameters(finding_eq=True,print_residuals=False)
        return errs    
    
    def inner_convergence2(self):
        x=self.R_pb
        ans=root(self.objective_function,x)
        print(f"Equilibrium Ratios are {ans.x}")
        self.R_pb=ans.x
        self.R_pbf=ans.x[0]
        self.R_pbo=ans.x[1]


    def inner_convergence(self):
        while True:
            Fu=np.array([self.R_pbf-self.Gf(self.R_pbo),
                        self.R_pbo-self.Go(self.R_pbf)])
            J=np.array([
                        [1, (-self.Gf(self.R_pbo+self.ho)+self.Gf(self.R_pbo))/self.ho],
                        [(-self.Go(self.R_pbf+self.hf)+self.Go(self.R_pbf))/self.hf, 1]
                        ])
            delta_R_pb=np.linalg.solve(J,-Fu)
            if np.linalg.norm(delta_R_pb/self.R_pb)<1e-9:
                print(f"{self.p_pbf} has converged")
                break
            self.R_pbf=self.R_pbf+delta_R_pb[0]#*self.hf
            self.R_pbo=self.R_pbo+delta_R_pb[1]#*self.ho
            self.R_pb=[self.R_pbf,self.R_pbo]
            #print(self.R_pb,np.linalg.norm(delta_R_pb/self.R_pb))
        #print(self.R_pbf,self.R_pbo)
        self.R_pbf=0.17
        self.R_pbo=58

    def calculate_all_parameters(self,check_residuals=True,finding_eq=False,print_residuals=False):
        self.max_residual=0
        self.parameters={}
        self.parameters["Exit Diameter"]=self.exit_diameter()#((self.A_t*29.5)/np.pi)**0.5*2
        self.parameters["Isp"]=Isp=self.isp(self.R)
        self.parameters["Thrust"]=Thrust=self.m_z*self.parameters["Isp"]
        self.parameters["chamber pressure"]=p_c=self.m_z*self.cstar(self.R)/self.A_t
        self.parameters["fuel flow rate"]=m_f=self.m_z/(1+self.R)
        self.parameters["oxidiser flow rate"]=m_o=self.m_z/(1+self.R)*self.R
        self.parameters["fuel-rich turbine gas flow rate"]=m_tf=m_f*((self.R_pbo-self.R)*(1+self.R_pbf))/(self.R_pbo-self.R_pbf)
        self.parameters["oxidiser-rich turbine gas flow rate"]=m_to=m_o*((self.R-self.R_pbf) * (1 + self.R_pbo)) / ((self.R_pbo - self.R_pbf) * self.R)
        self.parameters["fuel flow rate of the fuel-rich preburner"]=m_ff=m_tf / (1 + self.R_pbf)
        self.parameters["oxidiser flow rate of the fuel-rich preburner"]=m_fo=m_tf*self.R_pbf / (1 + self.R_pbf)
        self.parameters["fuel flow rate of the oxidiser-rich preburner"]=m_of=m_to / (1 + self.R_pbo)
        self.parameters["oxidiser flow rate of the oxidiser-rich preburner"]=m_oo=m_to*self.R_pbo / (1 + self.R_pbo)
        self.parameters["outlet pressure of the fuel pump"]=p_f2=(self.p_f1 + self.delta_p_f(self.p_pbf))
        self.parameters["outlet pressure of the oxidizer pump"]=p_o2=(self.p_o1 + self.delta_p_o(self.p_pbf))
        self.parameters["inlet pressure of the fuel-rich turbine"]=p_f3=(self.p_pbf - self.C_f2 * p_c)
        self.parameters["inlet pressure of the oxidizer-rich turbine"]=p_o3=(self.p_pbo - self.C_o2 * p_c)
        self.parameters["outlet pressure of the fuel-rich turbine"]=p_f4=p_c * (1 + self.C_f3)
        self.parameters["outlet pressure of the oxidizer-rich turbine"]=p_o4=p_c * (1 + self.C_o3)
        self.parameters["fuel-rich turbine pressure ratio"]=pi_tf=p_f3/p_f4
        self.parameters["oxidizer-rich turbine pressure ratio"]=pi_to=p_o3/p_o4
        self.parameters["fuel pump head"]=delta_p_f=self.delta_p_f(self.p_pbf)
        self.parameters["oxidiser pump head"]=delta_p_o=self.delta_p_o(self.p_pbf)
        self.parameters["fuel turbopump power"]=P_f=m_f*delta_p_f/self.rho_f/self.eta_pf
        self.parameters["oxidiser turbopump power"]=P_o=m_o*delta_p_o/self.rho_o/self.eta_po
        self.parameters["fuel-rich turbine power"]=g_f=m_tf*self.eta_tf*self.gamma(self.R_pbf)/(self.gamma(self.R_pbf)-1)*(self.R_0/self.mol_w(self.R_pbf))*self.temperature(self.R_pbf)*(1-(1/pi_tf)**(self.gamma(self.R_pbf)-1/self.gamma(self.R_pbf)))
        self.parameters["oxidiser-rich turbine power"]=g_o=m_to*self.eta_to*self.gamma(self.R_pbo)/(self.gamma(self.R_pbo)-1)*(self.R_0/self.mol_w(self.R_pbo))*self.temperature(self.R_pbo)*(1-(1/pi_to)**(self.gamma(self.R_pbo)-1/self.gamma(self.R_pbo)))
        self.parameters["gamma in fuel rich preburner"]=gamma_pbf=self.gamma(self.R_pbf)
        self.parameters["gamma in oxidiser rich preburner"]=gamma_pbo=self.gamma(self.R_pbo)
        self.parameters["molecular weight in fuel rich preburner"]=M_pbf=self.mol_w(self.R_pbf)*1e3
        self.parameters["molecular weight in oxidiser rich preburner"]=M_pbo=self.mol_w(self.R_pbo)*1e3
        self.parameters["temperature in fuel rich preburner"]=T_pbf=self.temperature(self.R_pbf)
        self.parameters["temperature in oxidiser rich preburner"]=T_pbo=self.temperature(self.R_pbo)
        self.parameters["fuel rich preburner O/F"]=R_pbf=self.R_pbf
        self.parameters["oxidiser rich preburner O/F"]=R_pbo=self.R_pbo

        if check_residuals:
            eqs=[]
            eqs2=[]
            eqs.append((self.m_z-Thrust/Isp)) #1
            eqs.append((self.m_z-m_f-m_o)) #2
            eqs.append((p_c-self.m_z/self.A_t*self.cstar(self.R))) #3
            #eqs.append((self.F-C_f*self.A_t*P_c)/a)
            eqs.append((m_f-self.m_z/(1+self.R))) #4
            eqs.append((m_f-m_ff-m_of)) #5
            eqs.append((m_o-self.R*m_f)) #6
            eqs.append((m_o-m_fo-m_oo)) #7
            eqs.append((m_ff - m_tf / (1 + R_pbf))) #8
            eqs.append((m_fo - R_pbf * m_tf / (1 + R_pbf))) #9
            eqs.append((m_of - m_to / (1 + R_pbo))) #10
            eqs.append((m_oo - R_pbo * m_to / (1 + R_pbo))) #11
            eqs.append(m_tf - m_f*((R_pbo - self.R) * (1 + R_pbf)) / (R_pbo - R_pbf)) #12
            eqs.append(m_to - m_o*((self.R - R_pbf) * (1 + R_pbo)) / ((R_pbo - R_pbf) * self.R)) #13
            eqs.append((p_f2 - (self.p_f1 + delta_p_f))) #14
            eqs.append((p_o2 - (self.p_o1 + delta_p_o))) #15
            eqs.append((self.p_pbf - (p_f2 - self.C_f1 * p_c) / (1 + self.C_ff))) #16
            eqs.append((self.p_pbo - (p_o2 - self.C_o1 * p_c) / (1 + self.C_oo))) #17
            eqs.append((p_f3 - (self.p_pbf - self.C_f2 * p_c))) #18
            eqs.append((p_o3 - (self.p_pbo - self.C_o2 * p_c))) #19
            eqs.append((p_f4 - p_c * (1 + self.C_f3))) #20
            eqs.append((p_o4 - p_c * (1 + self.C_o3))) #21
            eqs.append(pi_tf - p_f3 / p_f4) #22
            eqs.append(pi_to - p_o3 / p_o4) #23
            eqs.append((delta_p_f-((1+self.C_ff)*self.p_pbf+self.C_f1*p_c-self.p_f1))) #24
            eqs.append((delta_p_o-((1+self.C_oo)*self.p_pbo-self.p_o1))) #25
            eqs.append(pi_tf-(self.p_pbf-self.C_f2*p_c)/(p_c*(1+self.C_f3)))#26
            eqs.append(pi_to-(self.p_pbo-self.C_o2*p_c)/(p_c*(1+self.C_o3))) #27
            eqs.append((p_o2-self.p_pbf*(1+self.C_fo))) #28
            eqs.append((p_o2-self.p_pbo*(1+self.C_oo)))#29
            eqs.append((p_f2-self.p_pbo*(1+self.C_of))/p_f2) #30
            eqs.append((p_f2-(self.p_pbf*(1+self.C_ff)+self.C_f1*p_c))) #31
            eqs.append(P_f-g_f) #32
            #eqs.append(P_f-p_f)
            eqs.append(P_o-g_o) #33
            #eqs.append(P_o-p_o)
            eqs.append(g_f-m_tf*self.eta_tf*self.gamma(self.R_pbf)/(self.gamma(self.R_pbf)-1)*(self.R_0/self.mol_w(self.R_pbf))*self.temperature(self.R_pbf)*(1-(1/pi_tf)**(self.gamma(self.R_pbf)-1/self.gamma(self.R_pbf)))) #34
            eqs.append(g_o-m_to*self.eta_to*self.gamma(self.R_pbo)/(self.gamma(self.R_pbo)-1)*(self.R_0/self.mol_w(self.R_pbo))*self.temperature(self.R_pbo)*(1-(1/pi_to)**(self.gamma(self.R_pbo)-1/self.gamma(self.R_pbo)))) #35
            eqs.append((P_f-m_f*delta_p_f/self.rho_f/self.eta_pf)) #36
            eqs.append((P_o-m_o*delta_p_o/self.rho_o/self.eta_po)) #37
            #eqs.append((delta_p_f-(R_pbo-self.R)*(1+R_pbf)/(R_pbo-R_pbf)*(self.eta_tf*self.rho_f*self.eta_pf)*(self.gamma_pbf/(self.gamma_pbf-1))*(self.R_0/self.M_pbf)*self.T_pbf*(1-(1/pi_tf)**(self.gamma_pbf-1/self.gamma_pbf)))/a)
            #eqs.append((delta_p_o-(self.R-R_pbf)*(1+R_pbf)/(R_pbo-R_pbf)*(self.eta_to*self.rho_o*self.eta_po)*(self.gamma_pbo/(self.gamma_pbo-1))*(self.R_0/self.M_pbo)*self.T_pbo*(1-(1/pi_to)**(self.gamma_pbo-1/self.gamma_pbo)))/a)

            eqs2.append(self.m_z) #1
            eqs2.append(self.m_z) #2
            eqs2.append(self.m_z) #3
            eqs2.append(m_f) #4
            eqs2.append(m_f) #5
            eqs2.append(m_o) #6
            eqs2.append(m_o) #7
            eqs2.append(m_ff) #8
            eqs2.append(m_fo) #9
            eqs2.append(m_of) #10
            eqs2.append(m_oo) #11
            eqs2.append(m_tf) #12
            eqs2.append(m_to) #13
            eqs2.append(p_f2) #14
            eqs2.append(p_o2) #15
            eqs2.append(self.p_pbf) #16
            eqs2.append(self.p_pbo) #17
            eqs2.append(p_f3) #18
            eqs2.append(p_o3) #19
            eqs2.append(p_f4) #20
            eqs2.append(p_o4) #21
            eqs2.append(pi_tf) #22
            eqs2.append(pi_to) #23
            eqs2.append(delta_p_f) #24
            eqs2.append(delta_p_o) #25
            eqs2.append(pi_tf) #26
            eqs2.append(pi_to) #27
            eqs2.append(p_o2) #28
            eqs2.append(p_o2) #29
            eqs2.append(p_f2) #30
            eqs2.append(p_f2) #31
            eqs2.append(P_f) #32
            eqs2.append(P_o) #33
            eqs2.append(g_f) #34
            eqs2.append(g_o) #35
            eqs2.append(P_f) #36
            eqs2.append(P_o) #37

            #eqs.append((delta_p_f-(R_pbo-self.R)*(1+R_pbf)/(R_pbo-R_pbf)*(self.eta_tf*self.rho_f*self.eta_pf)*(self.gamma_pbf/(self.gamma_pbf-1))*(self.R_0/self.M_pbf)*self.T_pbf*(1-(1/pi_tf)**(self.gamma_pbf-1/self.gamma_pbf)))/a)
            #eqs.append((delta_p_o-(self.R-R_pbf)*(1+R_pbf)/(R_pbo-R_pbf)*(self.eta_to*self.rho_o*self.eta_po)*(self.gamma_pbo/(self.gamma_pbo-1))*(self.R_0/self.M_pbo)*self.T_pbo*(1-(1/pi_to)**(self.gamma_pbo-1/self.gamma_pbo)))/a)
            if print_residuals:
                print("Residuals:")

            for i in range(0,len(eqs)):
                if print_residuals:
                    print(f"{i+1} : {round(eqs[i]/eqs2[i]*100,3)}%")
                if np.abs((eqs[i]/eqs2[i]))>self.max_residual:
                    self.max_residual=np.abs((eqs[i]/eqs2[i]))*100
        
        if finding_eq:
            return eqs[31]/eqs2[31],eqs[32]/eqs2[32]

    def get_output(self,print_residual=True):
        sys.stdout = open(self.output_file, 'w')
        print(f"***********************************************  {self.engine_name} ENGINE  ***********************************************")
        print()
        print(f"--- INPUT PARAMETERS ---\n")
        """
        df=pd.DataFrame.from_dict(self.data,orient="index")
        print(df.to_markdown())
        """
        #print("="*70)
        for key in self.data.keys():
            if ("pressure" in key and not("ratio" in key)) or "head" in key:
                print(f"{key} = {round(self.data[key]/1e5,2)} bar")
            elif "m_z" in key:
                print(f"{key} = {round(self.data[key],2)} kg/s")
            elif "A_t" in key:
                print(f"{key} = {round(self.data[key],4)} m^2")
            elif not("Thrust" in key or "p_c" in key):
                print(f"{key} = {self.data[key]}")
            #if not("Thrust" in key or "p_c" in key):
                #print("="*70)
        print()
        print("--- OUTPUT PARAMETERS ---\n")
        i=0
        #print("="*70)
        for key in self.parameters.keys():
            if "Exit Diameter" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key],3)} m")
            elif ("pressure" in key and not("ratio" in key)) or "head" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key]/1e5,2)} bar")
            elif "Isp" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key]/g,2)} s")
            elif "Thrust" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key]/1e3,2)} kN")
            elif "rate" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key],2)} kg/s")
            elif "power" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key]/1e6,2)} MW")
            elif "temperature" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key],2)} K")
            else:
                print(f"{key} ({self.symbols[i]}) ={round(self.parameters[key],3)}")
            i+=1
            ##print("="*70)

        if print_residual:
            print()
            print(f"--- MAX RESIDUAL = {round(self.max_residual,3)}% ---")
        sys.stdout.close()
        sys.stdout = sys.__stdout__

class engine_obsolete:
    def __init__(self,engine_name,override_inputs=True):
        self.engine_name=engine_name
        self.input_file="input files/engines/"+engine_name+".json"
        self.output_file="output files/engines/"+engine_name+".txt"
        with open(self.input_file) as file:
            self.data = json.load(file)
        self.read_fuel_data()

        if override_inputs:
            self.override_inputs()
        self.R_pb=[0.1,10]
        self.R_pbf=1
        self.R_pbo=1
        self.R=self.data["oxidiser by fuel"]

        self.m_z=self.data["m_z"]
        self.A_t=self.data["A_t"]
        self.p_f1=self.data["fuel tank pressure"]
        self.p_o1=self.data["oxidiser tank pressure"]
        self.p_c=self.data["p_c"]

        self.eta_tf=self.data["fuel rich turbine efficiency"]
        self.eta_to=self.data["oxidiser rich turbine efficiency"]
        self.eta_pf=self.data["fuel pump efficiency"]
        self.eta_po=self.data["oxidiser pump efficiency"]
        
        self.rho_o=self.data["oxidiser density"]
        self.rho_f=self.data["fuel density"]
        self.p_pbf=self.data["fuel rich preburner pressure"]
        
        
        self.R_0=8.314
        
        self.ho=1e-1
        self.hf=1e-1

        self.C_ff=0.14       # Pressure drop loss coefficient between the fuel pump and the fuel-rich preburner
        self.C_oo=0.14       # Pressure drop loss coefficient between the oxidizer pump and the oxidizer-rich preburner
        self.C_f1=0.63       # Pressure drop loss coefficient between the fuel pump and fuel injector of the fuel-rich preburner
        self.C_o1=0       # Pressure drop loss coefficient between the oxidizer pump and oxidizer injector of the oxidizer-rich preburner
        self.C_f2=0       # Pressure drop loss coefficient between the fuel-rich preburner and the fuel-rich turbine
        self.C_o2=0       # Pressure drop loss coefficient between the oxidizer-rich preburner and the oxidizer-rich turbine
        self.C_f3=0.14       # Pressure drop loss coefficient between the fuel-rich turbine and the combustion chamber
        self.C_o3=0.43       # Pressure drop loss coefficient between the oxidizer-rich turbine and the combustion chamber
        #self.C_f4=0        Pressure drop loss coefficient between the fuel-rich preburner and the oxidizer-rich preburner
        #self.C_o4=0        Pressure drop loss coefficient between the oxidizer-rich preburner and the fuel-rich preburner
        self.C_fo=0.14       # Pressure drop loss coefficient between the oxidizer pump and the fuel-rich preburner
        self.C_of=0.45       # Pressure drop loss coefficient between the fuel pump and the oxidizer-rich preburner

        self.p_pbo=(1+self.C_fo)*self.p_pbf/(1+self.C_oo)

        self.max_residual=0

        self.symbols = ["D_E", "Isp", "Thrust", "p_c", "m_f", "m_o", "m_tf", "m_to", "m_ff", "m_fo", "m_of", "m_oo", "p_f2", "p_o2", "p_f3", "p_o3", "p_f4", "p_o4", "pi_tf", "pi_to", "delta_p_f", "delta_p_o", "P_f", "P_o", "g_f", "g_o", "gamma_pbf", "gamma_pbo", "M_pbf", "M_pbo", "T_pbf", "T_pbo", "R_pbf", "R_pbo"]

    def override_inputs(self):
        self.data["m_z"]=self.data["Thrust"]/self.isp(self.data["oxidiser by fuel"],self.data["p_c"])
        self.data["A_t"]=self.data["m_z"]*self.cstar(self.data["oxidiser by fuel"],self.data["p_c"])/self.data["p_c"]

    def read_fuel_data(self):
        self.fuel_data=np.genfromtxt("data files/LOXMETHANE.txt")[1:].T
        self.fuel_data_heads=["P","O/F","temp","isp","mw","cstar","gamma"]
           
    def temperature(self,R,P):
        pressures=self.fuel_data[0]*1e5
        ratios=self.fuel_data[1]
        ans=self.fuel_data[2]
        for i in range(1,len(ratios)-1):
            if P>=pressures[i]:
                continue
            else:
                if ratios[i]<=R:
                    return (ans[i+1]-ans[i])/(ratios[i+1]-ratios[i])*(R-ratios[i])+ans[i]
        
    def isp(self,R,P):
        pressures=self.fuel_data[0]*1e5
        ratios=self.fuel_data[1]
        ans=self.fuel_data[3]
        for i in range(1,len(ratios)-1):
            if P>=pressures[i]:
                continue
            else:
                if ratios[i]<=R:
                    return (ans[i+1]-ans[i])/(ratios[i+1]-ratios[i])*(R-ratios[i])+ans[i]
      
    def mol_w(self,R,P):
        pressures=self.fuel_data[0]*1e5
        ratios=self.fuel_data[1]
        ans=self.fuel_data[2]
        for i in range(1,len(ratios)-1):
            if P>=pressures[i]:
                continue
            else:
                if ratios[i]<=R:
                    return (ans[i+1]-ans[i])/(ratios[i+1]-ratios[i])*(R-ratios[i])+ans[i]
                
    def cstar(self,R,P):
        pressures=self.fuel_data[0]*1e5
        ratios=self.fuel_data[1]
        ans=self.fuel_data[5]
        for i in range(1,len(ratios)-1):
            if P>=pressures[i]:
                continue
            else:
                if ratios[i]<=R:
                    return (ans[i+1]-ans[i])/(ratios[i+1]-ratios[i])*(R-ratios[i])+ans[i]
     
    def gamma(self,R,P):
        pressures=self.fuel_data[0]*1e5
        ratios=self.fuel_data[1]
        ans=self.fuel_data[6]
        for i in range(1,len(ratios)-1):
            if P>=pressures[i]:
                continue
            else:
                if ratios[i]<=R:
                    return (ans[i+1]-ans[i])/(ratios[i+1]-ratios[i])*(R-ratios[i])+ans[i]
    
    def gas_constant(self,R,P):
        return self.R_0/self.mol_w(R,P)

    def exit_diameter(self):

        p_p0=1e5/self.p_c
        gamma=self.gamma(self.R,self.p_c)
        # Define the isentropic pressure ratio function
        def pressure_ratio(M):
            return (1 + 0.5*(gamma -1)*M**2)**(-gamma/(gamma -1))

        # Define function whose root we want: pressure_ratio(M) - p_p0 = 0
        def f(M):
            return pressure_ratio(M) - p_p0

        # Solve for subsonic Mach (M < 1)
        #sol_sub = root_scalar(f, bracket=[1e-5, 1])
        #if not sol_sub.converged:
        #    raise ValueError("Subsonic Mach solving failed")
        #M_sub = sol_sub.root

        # Solve for supersonic Mach (M >1)
        sol_sup = root_scalar(f, bracket=[1.0001, 20])
        if not sol_sup.converged:
            raise ValueError("Supersonic Mach solving failed")
        M_sup = sol_sup.root

        # Area-Mach relation
        def area_ratio(M):
            return (1/M) * ( (2/(gamma+1)*(1 + 0.5*(gamma-1)*M**2)) ) ** ( (gamma+1)/(2*(gamma-1)) )

        #A_Astar_sub = area_ratio(M_sub)
        A_Astar_sup = area_ratio(M_sup)
        A_e=A_Astar_sup*self.A_t
        d_e=(A_e/pi)**0.5*2
        return d_e


    '''
    def c_star(self):
        #self.c_star=((self.data['R_c']*self.data['T_c']/self.data['gamma_c'])**0.5)/(2/(self.data['gamma_c']+1))**((self.data['gamma_c']+1)/2/(self.data['gamma_c']-1))
        return ((self.gas_constant(self.R)*self.temperature(self.R)/self.gamma(self.R))**0.5)/(2/(self.gamma(self.R)+1))**((self.gamma(self.R)+1)/2/(self.gamma(self.R)-1)) 
    
    def delta_p_f(self,R_pbo,R_pbf):
        return (R_pbo-self.R)*(1+R_pbf)/(R_pbo-R_pbf)*(self.eta_tf*self.rho_f*self.eta_pf)*(self.gamma_pbf/(self.gamma_pbf-1))*(self.R_0/self.M_pbf)*self.T_pbf*(1-(1/self.data['pi_tf'])**(self.gamma_pbf-1/self.gamma_pbf))
    
    def delta_p_o(self,R_pbo,R_pbf):
        return (self.R-R_pbf)*(1+R_pbf)/(R_pbo-R_pbf)*(self.eta_to*self.rho_o*self.eta_po)*(self.gamma_pbo/(self.gamma_pbo-1))*(self.R_0/self.M_pbo)*self.T_pbo*(1-(1/self.data['pi_to'])**(self.gamma_pbo-1/self.gamma_pbo))
    '''

    def delta_p_f(self,p_pbf):
        return (1+self.C_ff)*p_pbf+self.C_f1*self.p_c-self.p_f1
    
    def delta_p_o(self,p_pbf):
        return (1+self.C_fo)*p_pbf-self.p_o1

    def pi_tf(self):
        return (self.p_pbf-self.C_f2*self.m_z*self.cstar(self.R,self.p_c)/self.A_t)/(self.m_z*self.cstar(self.R_pbf,self.p_pbf)/self.A_t*(1+self.C_f3))    

    def pi_to(self):
        return (self.p_pbo-self.C_o2*self.m_z*self.cstar(self.R,self.p_c)/self.A_t)/(self.m_z*self.cstar(self.R_pbf,self.p_pbf)/self.A_t*(1+self.C_o3))
    
    def Gf(self,R_pbo):
        gamma_pbf=self.gamma(self.R_pbf)
        gamma_pbo=self.gamma(R_pbo)
        M_pbf=self.mol_w(self.R_pbf)
        M_pbo=self.mol_w(R_pbo)
        T_pbf=self.temperature(self.R_pbf)
        T_pbo=self.temperature(R_pbo)
        #print(self.delta_p_f(self.p_pbf_k)/1e5,self.delta_p_o(self.p_pbf_k)/1e5,gamma_pbf,gamma_pbo,M_pbf,M_pbo,T_pbf,T_pbo)
        #c1=self.delta_p_f(R_pbo,self.R_pb[0])/self.eta_tf/self.rho_f/self.eta_pf
        c1=self.delta_p_f(self.p_pbf)/self.eta_tf/self.rho_f/self.eta_pf
        #c2=self.delta_p_o(R_pbo,self.R_pb[0])/self.eta_to/self.rho_o/self.eta_po
        c2=self.delta_p_o(self.p_pbf)/self.eta_to/self.rho_o/self.eta_po
        w_f=gamma_pbf/(gamma_pbf-1)*(self.R_0/M_pbf)*T_pbf*(1-(1/self.pi_tf())**(gamma_pbf-1/gamma_pbf))
        w_o=gamma_pbo/(gamma_pbo-1)*(self.R_0/M_pbo)*T_pbo*(1-(1/self.pi_to())**(gamma_pbo-1/gamma_pbo))
        return (self.R*c2*R_pbo/(1+R_pbo)-self.R*w_o)/(self.R*c2/(1+R_pbo)-w_o)
    
    def Go(self,R_pbf):        
        gamma_pbf=self.gamma(R_pbf)
        gamma_pbo=self.gamma(self.R_pbo)
        M_pbf=self.mol_w(R_pbf)
        M_pbo=self.mol_w(self.R_pbo)
        T_pbf=self.temperature(R_pbf)
        T_pbo=self.temperature(self.R_pbo)
        #c1=self.delta_p_f(R_pbo,self.R_pb[0])/self.eta_tf/self.rho_f/self.eta_pf
        c1=self.delta_p_f(self.p_pbf)/self.eta_tf/self.rho_f/self.eta_pf
        #c2=self.delta_p_o(R_pbo,self.R_pb[0])/self.eta_to/self.rho_o/self.eta_po
        c2=self.delta_p_o(self.p_pbf)/self.eta_to/self.rho_o/self.eta_po
        w_f=gamma_pbf/(gamma_pbf-1)*(self.R_0/M_pbf)*T_pbf*(1-(1/self.pi_tf())**(gamma_pbf-1/gamma_pbf))
        w_o=gamma_pbo/(gamma_pbo-1)*(self.R_0/M_pbo)*T_pbo*(1-(1/self.pi_to())**(gamma_pbo-1/gamma_pbo))
        return (-c1*R_pbf/(1+R_pbf)+self.R*w_f)/(-c1/(1+R_pbf)+w_f)
    
    def objective_function(self,x):
        self.R_pbf=x[0]
        self.R_pbo=x[1]
        errs=self.calculate_all_parameters(finding_eq=True,print_residuals=False,print_max_residual=True)
        return errs    
    
    def inner_convergence2(self):
        x=self.R_pb
        ans=root(self.objective_function,x,tol=1e-8)
        print(f"Equilibrium Ratios are {ans.x}")
        self.R_pb=ans.x
        self.R_pbf=ans.x[0]
        self.R_pbo=ans.x[1]


    def inner_convergence(self):
        while True:
            Fu=np.array([self.R_pbf-self.Gf(self.R_pbo),
                        self.R_pbo-self.Go(self.R_pbf)])
            J=np.array([
                        [1, (-self.Gf(self.R_pbo+self.ho)+self.Gf(self.R_pbo))/self.ho],
                        [(-self.Go(self.R_pbf+self.hf)+self.Go(self.R_pbf))/self.hf, 1]
                        ])
            delta_R_pb=np.linalg.solve(J,-Fu)
            if np.linalg.norm(delta_R_pb/self.R_pb)<1e-9:
                print(f"{self.p_pbf} has converged")
                break
            self.R_pbf=self.R_pbf+delta_R_pb[0]#*self.hf
            self.R_pbo=self.R_pbo+delta_R_pb[1]#*self.ho
            self.R_pb=[self.R_pbf,self.R_pbo]
            #print(self.R_pb,np.linalg.norm(delta_R_pb/self.R_pb))
        #print(self.R_pbf,self.R_pbo)
        self.R_pbf=0.17
        self.R_pbo=58

    def calculate_all_parameters(self,check_residuals=True,finding_eq=False,print_residuals=False,print_max_residual=False):
        print(f"Calculating parameters for {self.engine_name} engine")
        self.max_residual=0
        self.parameters={}
        self.parameters["Exit Diameter"]=self.exit_diameter()#((self.A_t*29.5)/np.pi)**0.5*2
        self.parameters["Isp"]=Isp=self.isp(self.R,self.p_c)
        self.parameters["Thrust"]=Thrust=self.m_z*self.parameters["Isp"]
        self.parameters["chamber pressure"]=p_c=self.m_z*self.cstar(self.R,self.p_c)/self.A_t
        self.parameters["fuel flow rate"]=m_f=self.m_z/(1+self.R)
        self.parameters["oxidiser flow rate"]=m_o=self.m_z/(1+self.R)*self.R
        self.parameters["fuel-rich turbine gas flow rate"]=m_tf=m_f*((self.R_pbo-self.R)*(1+self.R_pbf))/(self.R_pbo-self.R_pbf)
        self.parameters["oxidiser-rich turbine gas flow rate"]=m_to=m_o*((self.R-self.R_pbf) * (1 + self.R_pbo)) / ((self.R_pbo - self.R_pbf) * self.R)
        self.parameters["fuel flow rate of the fuel-rich preburner"]=m_ff=m_tf / (1 + self.R_pbf)
        self.parameters["oxidiser flow rate of the fuel-rich preburner"]=m_fo=m_tf*self.R_pbf / (1 + self.R_pbf)
        self.parameters["fuel flow rate of the oxidiser-rich preburner"]=m_of=m_to / (1 + self.R_pbo)
        self.parameters["oxidiser flow rate of the oxidiser-rich preburner"]=m_oo=m_to*self.R_pbo / (1 + self.R_pbo)
        self.parameters["outlet pressure of the fuel pump"]=p_f2=(self.p_f1 + self.delta_p_f(self.p_pbf))
        self.parameters["outlet pressure of the oxidizer pump"]=p_o2=(self.p_o1 + self.delta_p_o(self.p_pbf))
        self.parameters["inlet pressure of the fuel-rich turbine"]=p_f3=(self.p_pbf - self.C_f2 * p_c)
        self.parameters["inlet pressure of the oxidizer-rich turbine"]=p_o3=(self.p_pbo - self.C_o2 * p_c)
        self.parameters["outlet pressure of the fuel-rich turbine"]=p_f4=p_c * (1 + self.C_f3)
        self.parameters["outlet pressure of the oxidizer-rich turbine"]=p_o4=p_c * (1 + self.C_o3)
        self.parameters["fuel-rich turbine pressure ratio"]=pi_tf=p_f3/p_f4
        self.parameters["oxidizer-rich turbine pressure ratio"]=pi_to=p_o3/p_o4
        self.parameters["fuel pump head"]=delta_p_f=self.delta_p_f(self.p_pbf)
        self.parameters["oxidiser pump head"]=delta_p_o=self.delta_p_o(self.p_pbf)
        self.parameters["fuel turbopump power"]=P_f=m_f*delta_p_f/self.rho_f/self.eta_pf
        self.parameters["oxidiser turbopump power"]=P_o=m_o*delta_p_o/self.rho_o/self.eta_po
        self.parameters["fuel-rich turbine power"]=g_f=m_tf*self.eta_tf*self.gamma(self.R_pbf,self.p_pbf)/(self.gamma(self.R_pbf,self.p_pbf)-1)*(self.R_0/self.mol_w(self.R_pbf,self.p_pbf))*self.temperature(self.R_pbf,self.p_pbf)*(1-(1/pi_tf)**(self.gamma(self.R_pbf,self.p_pbf)-1/self.gamma(self.R_pbf,self.p_pbf)))
        self.parameters["oxidiser-rich turbine power"]=g_o=m_to*self.eta_to*self.gamma(self.R_pbo,self.p_pbo)/(self.gamma(self.R_pbo,self.p_pbo)-1)*(self.R_0/self.mol_w(self.R_pbo,self.p_pbo))*self.temperature(self.R_pbo,self.p_pbo)*(1-(1/pi_to)**(self.gamma(self.R_pbo,self.p_pbo)-1/self.gamma(self.R_pbo,self.p_pbo)))
        self.parameters["gamma in fuel rich preburner"]=gamma_pbf=self.gamma(self.R_pbf,self.p_pbf)
        self.parameters["gamma in oxidiser rich preburner"]=gamma_pbo=self.gamma(self.R_pbo,self.p_pbo)
        self.parameters["molecular weight in fuel rich preburner"]=M_pbf=self.mol_w(self.R_pbf,self.p_pbf)*1e3
        self.parameters["molecular weight in oxidiser rich preburner"]=M_pbo=self.mol_w(self.R_pbo,self.p_pbo)*1e3
        self.parameters["temperature in fuel rich preburner"]=T_pbf=self.temperature(self.R_pbf,self.p_pbf)
        self.parameters["temperature in oxidiser rich preburner"]=T_pbo=self.temperature(self.R_pbo,self.p_pbo)
        self.parameters["fuel rich preburner O/F"]=R_pbf=self.R_pbf
        self.parameters["oxidiser rich preburner O/F"]=R_pbo=self.R_pbo

        if check_residuals:
            eqs=[]
            eqs2=[]
            eqs.append((self.m_z-Thrust/Isp)) #1
            eqs.append((self.m_z-m_f-m_o)) #2
            eqs.append((p_c-self.m_z/self.A_t*self.cstar(self.R,self.p_c))) #3
            #eqs.append((self.F-C_f*self.A_t*P_c)/a)
            eqs.append((m_f-self.m_z/(1+self.R))) #4
            eqs.append((m_f-m_ff-m_of)) #5
            eqs.append((m_o-self.R*m_f)) #6
            eqs.append((m_o-m_fo-m_oo)) #7
            eqs.append((m_ff - m_tf / (1 + R_pbf))) #8
            eqs.append((m_fo - R_pbf * m_tf / (1 + R_pbf))) #9
            eqs.append((m_of - m_to / (1 + R_pbo))) #10
            eqs.append((m_oo - R_pbo * m_to / (1 + R_pbo))) #11
            eqs.append(m_tf - m_f*((R_pbo - self.R) * (1 + R_pbf)) / (R_pbo - R_pbf)) #12
            eqs.append(m_to - m_o*((self.R - R_pbf) * (1 + R_pbo)) / ((R_pbo - R_pbf) * self.R)) #13
            eqs.append((p_f2 - (self.p_f1 + delta_p_f))) #14
            eqs.append((p_o2 - (self.p_o1 + delta_p_o))) #15
            eqs.append((self.p_pbf - (p_f2 - self.C_f1 * p_c) / (1 + self.C_ff))) #16
            eqs.append((self.p_pbo - (p_o2 - self.C_o1 * p_c) / (1 + self.C_oo))) #17
            eqs.append((p_f3 - (self.p_pbf - self.C_f2 * p_c))) #18
            eqs.append((p_o3 - (self.p_pbo - self.C_o2 * p_c))) #19
            eqs.append((p_f4 - p_c * (1 + self.C_f3))) #20
            eqs.append((p_o4 - p_c * (1 + self.C_o3))) #21
            eqs.append(pi_tf - p_f3 / p_f4) #22
            eqs.append(pi_to - p_o3 / p_o4) #23
            eqs.append((delta_p_f-((1+self.C_ff)*self.p_pbf+self.C_f1*p_c-self.p_f1))) #24
            eqs.append((delta_p_o-((1+self.C_oo)*self.p_pbo-self.p_o1))) #25
            eqs.append(pi_tf-(self.p_pbf-self.C_f2*p_c)/(p_c*(1+self.C_f3)))#26
            eqs.append(pi_to-(self.p_pbo-self.C_o2*p_c)/(p_c*(1+self.C_o3))) #27
            eqs.append((p_o2-self.p_pbf*(1+self.C_fo))) #28
            eqs.append((p_o2-self.p_pbo*(1+self.C_oo)))#29
            eqs.append((p_f2-self.p_pbo*(1+self.C_of))/p_f2) #30
            eqs.append((p_f2-(self.p_pbf*(1+self.C_ff)+self.C_f1*p_c))) #31
            eqs.append(P_f-g_f) #32
            #eqs.append(P_f-p_f)
            eqs.append(P_o-g_o) #33
            #eqs.append(P_o-p_o)
            eqs.append(g_f-m_tf*self.eta_tf*self.gamma(self.R_pbf,self.p_pbf)/(self.gamma(self.R_pbf,self.p_pbf)-1)*(self.R_0/self.mol_w(self.R_pbf,self.p_pbf))*self.temperature(self.R_pbf,self.p_pbf)*(1-(1/pi_tf)**(self.gamma(self.R_pbf,self.p_pbf)-1/self.gamma(self.R_pbf,self.p_pbf)))) #34
            eqs.append(g_o-m_to*self.eta_to*self.gamma(self.R_pbo,self.p_pbo)/(self.gamma(self.R_pbo,self.p_pbo)-1)*(self.R_0/self.mol_w(self.R_pbo,self.p_pbo))*self.temperature(self.R_pbo,self.p_pbo)*(1-(1/pi_to)**(self.gamma(self.R_pbo,self.p_pbo)-1/self.gamma(self.R_pbo,self.p_pbo)))) #35
            eqs.append((P_f-m_f*delta_p_f/self.rho_f/self.eta_pf)) #36
            eqs.append((P_o-m_o*delta_p_o/self.rho_o/self.eta_po)) #37
            #eqs.append((delta_p_f-(R_pbo-self.R)*(1+R_pbf)/(R_pbo-R_pbf)*(self.eta_tf*self.rho_f*self.eta_pf)*(self.gamma_pbf/(self.gamma_pbf-1))*(self.R_0/self.M_pbf)*self.T_pbf*(1-(1/pi_tf)**(self.gamma_pbf-1/self.gamma_pbf)))/a)
            #eqs.append((delta_p_o-(self.R-R_pbf)*(1+R_pbf)/(R_pbo-R_pbf)*(self.eta_to*self.rho_o*self.eta_po)*(self.gamma_pbo/(self.gamma_pbo-1))*(self.R_0/self.M_pbo)*self.T_pbo*(1-(1/pi_to)**(self.gamma_pbo-1/self.gamma_pbo)))/a)

            eqs2.append(self.m_z) #1
            eqs2.append(self.m_z) #2
            eqs2.append(self.m_z) #3
            eqs2.append(m_f) #4
            eqs2.append(m_f) #5
            eqs2.append(m_o) #6
            eqs2.append(m_o) #7
            eqs2.append(m_ff) #8
            eqs2.append(m_fo) #9
            eqs2.append(m_of) #10
            eqs2.append(m_oo) #11
            eqs2.append(m_tf) #12
            eqs2.append(m_to) #13
            eqs2.append(p_f2) #14
            eqs2.append(p_o2) #15
            eqs2.append(self.p_pbf) #16
            eqs2.append(self.p_pbo) #17
            eqs2.append(p_f3) #18
            eqs2.append(p_o3) #19
            eqs2.append(p_f4) #20
            eqs2.append(p_o4) #21
            eqs2.append(pi_tf) #22
            eqs2.append(pi_to) #23
            eqs2.append(delta_p_f) #24
            eqs2.append(delta_p_o) #25
            eqs2.append(pi_tf) #26
            eqs2.append(pi_to) #27
            eqs2.append(p_o2) #28
            eqs2.append(p_o2) #29
            eqs2.append(p_f2) #30
            eqs2.append(p_f2) #31
            eqs2.append(P_f) #32
            eqs2.append(P_o) #33
            eqs2.append(g_f) #34
            eqs2.append(g_o) #35
            eqs2.append(P_f) #36
            eqs2.append(P_o) #37

            #eqs.append((delta_p_f-(R_pbo-self.R)*(1+R_pbf)/(R_pbo-R_pbf)*(self.eta_tf*self.rho_f*self.eta_pf)*(self.gamma_pbf/(self.gamma_pbf-1))*(self.R_0/self.M_pbf)*self.T_pbf*(1-(1/pi_tf)**(self.gamma_pbf-1/self.gamma_pbf)))/a)
            #eqs.append((delta_p_o-(self.R-R_pbf)*(1+R_pbf)/(R_pbo-R_pbf)*(self.eta_to*self.rho_o*self.eta_po)*(self.gamma_pbo/(self.gamma_pbo-1))*(self.R_0/self.M_pbo)*self.T_pbo*(1-(1/pi_to)**(self.gamma_pbo-1/self.gamma_pbo)))/a)
            if print_residuals:
                print("Residuals:")

            for i in range(0,len(eqs)):
                if print_residuals:
                    print(f"{i+1} : {round(eqs[i]/eqs2[i]*100,3)}%")
                if np.abs((eqs[i]/eqs2[i]))*100>self.max_residual:
                    self.max_residual=np.abs((eqs[i]/eqs2[i]))*100
        if print_max_residual:
            print(f"Max Residual = {round(self.max_residual,3)}%")

        if finding_eq:
            return eqs[31]/eqs2[31],eqs[32]/eqs2[32]

    def get_output(self,print_residual=True):
        sys.stdout = open(self.output_file, 'w')
        print(f"***********************************************  {self.engine_name} ENGINE  ***********************************************")
        print()
        print(f"--- INPUT PARAMETERS ---\n")
        """
        df=pd.DataFrame.from_dict(self.data,orient="index")
        print(df.to_markdown())
        """
        #print("="*70)
        for key in self.data.keys():
            if ("pressure" in key and not("ratio" in key)) or "head" in key:
                print(f"{key} = {round(self.data[key]/1e5,2)} bar")
            elif "m_z" in key:
                print(f"{key} = {round(self.data[key],2)} kg/s")
            elif "A_t" in key:
                print(f"{key} = {round(self.data[key],4)} m^2")
            elif not("Thrust" in key or "p_c" in key):
                print(f"{key} = {self.data[key]}")
            #if not("Thrust" in key or "p_c" in key):
                #print("="*70)
        print()
        print("--- OUTPUT PARAMETERS ---\n")
        i=0
        #print("="*70)
        for key in self.parameters.keys():
            if "Exit Diameter" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key],3)} m")
            elif ("pressure" in key and not("ratio" in key)) or "head" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key]/1e5,2)} bar")
            elif "Isp" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key]/g,2)} s")
            elif "Thrust" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key]/1e3,2)} kN")
            elif "rate" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key],2)} kg/s")
            elif "power" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key]/1e6,2)} MW")
            elif "temperature" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key],2)} K")
            else:
                print(f"{key} ({self.symbols[i]}) ={round(self.parameters[key],3)}")
            i+=1
            ##print("="*70)

        if print_residual:
            print()
            print(f"--- MAX RESIDUAL = {round(self.max_residual,3)}% ---")
        sys.stdout.close()
        sys.stdout = sys.__stdout__

class engine:
    def __init__(self,engine_name,override_inputs=True):
        
        self.create_interpolation_functions()

        self.engine_name=engine_name
        self.input_file="input files/engines/"+engine_name+".json"
        self.output_file="output files/engines/"+engine_name+".txt"
        sys.stdout = open(self.output_file, 'w')
        sys.stdout.close()
        sys.stdout = sys.__stdout__
        with open(self.input_file) as file:
            self.data = json.load(file)
        self.read_fuel_data()

        if override_inputs:
            self.override_inputs()
        self.R_pb=[0.1,10]
        self.R_pbf=1
        self.R_pbo=1
        self.R=self.data["oxidiser by fuel"]

        self.m_z=self.data["m_z"]
        self.A_t=self.data["A_t"]
        self.p_f1=self.data["fuel tank pressure"]
        self.p_o1=self.data["oxidiser tank pressure"]
        self.p_c=self.data["p_c"]

        self.eta_tf=self.data["fuel rich turbine efficiency"]
        self.eta_to=self.data["oxidiser rich turbine efficiency"]
        self.eta_pf=self.data["fuel pump efficiency"]
        self.eta_po=self.data["oxidiser pump efficiency"]
        
        self.rho_o=self.data["oxidiser density"]
        self.rho_f=self.data["fuel density"]
        self.p_pbf=self.data["fuel rich preburner pressure"]
        
        
        self.R_0=8.314
        
        self.ho=1e-1
        self.hf=1e-1

        self.C_ff=0.14       # Pressure drop loss coefficient between the fuel pump and the fuel-rich preburner
        self.C_oo=0.14       # Pressure drop loss coefficient between the oxidizer pump and the oxidizer-rich preburner
        self.C_f1=0.63       # Pressure drop loss coefficient between the fuel pump and fuel injector of the fuel-rich preburner
        self.C_o1=0       # Pressure drop loss coefficient between the oxidizer pump and oxidizer injector of the oxidizer-rich preburner
        self.C_f2=0       # Pressure drop loss coefficient between the fuel-rich preburner and the fuel-rich turbine
        self.C_o2=0       # Pressure drop loss coefficient between the oxidizer-rich preburner and the oxidizer-rich turbine
        self.C_f3=0.14       # Pressure drop loss coefficient between the fuel-rich turbine and the combustion chamber
        self.C_o3=0.43       # Pressure drop loss coefficient between the oxidizer-rich turbine and the combustion chamber
        #self.C_f4=0        Pressure drop loss coefficient between the fuel-rich preburner and the oxidizer-rich preburner
        #self.C_o4=0        Pressure drop loss coefficient between the oxidizer-rich preburner and the fuel-rich preburner
        self.C_fo=0.14       # Pressure drop loss coefficient between the oxidizer pump and the fuel-rich preburner
        self.C_of=0.45       # Pressure drop loss coefficient between the fuel pump and the oxidizer-rich preburner

        self.p_pbo=(1+self.C_fo)*self.p_pbf/(1+self.C_oo)

        self.max_residual=0

        self.symbols = ["D_E", "Isp", "Thrust", "p_c", "m_f", "m_o", "m_tf", "m_to", "m_ff", "m_fo", "m_of", "m_oo", "p_f2", "p_o2", "p_f3", "p_o3", "p_f4", "p_o4", "pi_tf", "pi_to", "delta_p_f", "delta_p_o", "P_f", "P_o", "g_f", "g_o", "gamma_pbf", "gamma_pbo", "M_pbf", "M_pbo", "T_pbf", "T_pbo", "R_pbf", "R_pbo"]
        
    def create_interpolation_functions(self):#,query_pressure, query_of):
        # Load the data
        data = np.loadtxt("data files/LOXMETHANE.txt", skiprows=1)  # Skip header
        
        pressures = data[:, 0]
        ofs = data[:, 1]
        temps = data[:, 2]
        isps = data[:, 3]
        mws = data[:, 4]
        cstars = data[:, 5]
        gammas = data[:, 6]

        # Stack (pressure, OF) pairs as interpolation input
        points = np.column_stack((pressures, ofs))

        # Create interpolators for each output
        self.temp_interp = LinearNDInterpolator(points, temps)
        self.isp_interp = LinearNDInterpolator(points, isps)
        self.mw_interp = LinearNDInterpolator(points, mws)
        self.cstar_interp = LinearNDInterpolator(points, cstars)
        self.gamma_interp = LinearNDInterpolator(points, gammas)
        '''
        # Interpolate at desired (pressure, O/F)
        T = self.temp_interp(query_pressure, query_of)
        Isp = self.isp_interp(query_pressure, query_of)
        MW = self.mw_interp(query_pressure, query_of)
        Cstar = self.cstar_interp(query_pressure, query_of)
        Gamma = self.gamma_interp(query_pressure, query_of)

        if None in (T, Isp, MW, Cstar, Gamma) or any(np.isnan(x) for x in (T, Isp, MW, Cstar, Gamma)):
            raise ValueError("Interpolation point outside data range or invalid. Pressure= {}, O/F={}".format(query_pressure, query_of))

        return LinearNDInterpolator
    
        {
            'Pressure': query_pressure,
            'O/F': query_of,
            'Temp (K)': T[()],
            'Isp (m/s)': Isp[()],
            'Mol. Weight': MW[()],
            'C* (m/s)': Cstar[()],
            'Gamma': Gamma[()]
        }

        '''

    def override_inputs(self):
        self.data["m_z"]=self.data["Thrust"]/self.isp(self.data["oxidiser by fuel"],self.data["p_c"])
        self.data["A_t"]=self.data["m_z"]*self.cstar(self.data["oxidiser by fuel"],self.data["p_c"])/self.data["p_c"]

    def read_fuel_data(self):
        self.fuel_data=np.genfromtxt("data files/LOXMETHANE cleaned.txt")[1:].T
        self.fuel_data_heads=["O/F","temp","isp","mw","cstar","gamma"]
           
    def temperature(self,R,P):
        return self.temp_interp(P/1e5,R)[()]#interpolate_combustion_data(P/1e5,R)["Temp (K)"]
    
    def isp(self,R,P):
        return self.isp_interp(P/1e5,R)[()]#interpolate_combustion_data(P/1e5,R)["Isp (m/s)"]
    
    def mol_w(self,R,P):
        return self.mw_interp(P/1e5,R)[()]*1e-3#interpolate_combustion_data(P/1e5,R)["Mol. Weight"]*1e-3

    def cstar(self,R,P):
        return self.cstar_interp(P/1e5,R)[()]#interpolate_combustion_data(P/1e5,R)["C* (m/s)"]
     
    def gamma(self,R,P):
        return self.gamma_interp(P/1e5,R)[()]#interpolate_combustion_data(P/1e5,R)["Gamma"]
    
    def gas_constant(self,R,P):
        return self.R_0/self.mol_w(P/1e5,R)[()]#interpolate_combustion_data(P/1e5,R)["Mol. Weight"]*1e-3
    
    def exit_diameter(self):

        p_p0=1e5/self.p_c
        gamma=self.gamma(self.R,self.p_c)
        # Define the isentropic pressure ratio function
        def pressure_ratio(M):
            return (1 + 0.5*(gamma -1)*M**2)**(-gamma/(gamma -1))

        # Define function whose root we want: pressure_ratio(M) - p_p0 = 0
        def f(M):
            return pressure_ratio(M) - p_p0

        # Solve for subsonic Mach (M < 1)
        #sol_sub = root_scalar(f, bracket=[1e-5, 1])
        #if not sol_sub.converged:
        #    raise ValueError("Subsonic Mach solving failed")
        #M_sub = sol_sub.root

        # Solve for supersonic Mach (M >1)
        sol_sup = root_scalar(f, bracket=[1.0001, 20])
        if not sol_sup.converged:
            raise ValueError("Supersonic Mach solving failed")
        M_sup = sol_sup.root

        # Area-Mach relation
        def area_ratio(M):
            return (1/M) * ( (2/(gamma+1)*(1 + 0.5*(gamma-1)*M**2)) ) ** ( (gamma+1)/(2*(gamma-1)) )

        #A_Astar_sub = area_ratio(M_sub)
        A_Astar_sup = area_ratio(M_sup)
        A_e=A_Astar_sup*self.A_t
        d_e=(A_e/pi)**0.5*2
        return d_e

    '''
    def c_star(self):
        #self.c_star=((self.data['R_c']*self.data['T_c']/self.data['gamma_c'])**0.5)/(2/(self.data['gamma_c']+1))**((self.data['gamma_c']+1)/2/(self.data['gamma_c']-1))
        return ((self.gas_constant(self.R)*self.temperature(self.R)/self.gamma(self.R))**0.5)/(2/(self.gamma(self.R)+1))**((self.gamma(self.R)+1)/2/(self.gamma(self.R)-1)) 
    
    def delta_p_f(self,R_pbo,R_pbf):
        return (R_pbo-self.R)*(1+R_pbf)/(R_pbo-R_pbf)*(self.eta_tf*self.rho_f*self.eta_pf)*(self.gamma_pbf/(self.gamma_pbf-1))*(self.R_0/self.M_pbf)*self.T_pbf*(1-(1/self.data['pi_tf'])**(self.gamma_pbf-1/self.gamma_pbf))
    
    def delta_p_o(self,R_pbo,R_pbf):
        return (self.R-R_pbf)*(1+R_pbf)/(R_pbo-R_pbf)*(self.eta_to*self.rho_o*self.eta_po)*(self.gamma_pbo/(self.gamma_pbo-1))*(self.R_0/self.M_pbo)*self.T_pbo*(1-(1/self.data['pi_to'])**(self.gamma_pbo-1/self.gamma_pbo))
    '''

    def delta_p_f(self,p_pbf):
        return (1+self.C_ff)*p_pbf+self.C_f1*self.p_c-self.p_f1
    
    def delta_p_o(self,p_pbf):
        return (1+self.C_fo)*p_pbf-self.p_o1

    def pi_tf(self):
        return (self.p_pbf-self.C_f2*self.m_z*self.cstar(self.R,self.p_c)/self.A_t)/(self.m_z*self.cstar(self.R_pbf,self.p_pbf)/self.A_t*(1+self.C_f3))    

    def pi_to(self):
        return (self.p_pbo-self.C_o2*self.m_z*self.cstar(self.R,self.p_c)/self.A_t)/(self.m_z*self.cstar(self.R_pbf,self.p_pbf)/self.A_t*(1+self.C_o3))
    
    def Gf(self,R_pbo): #obsolete
        gamma_pbf=self.gamma(self.R_pbf)
        gamma_pbo=self.gamma(R_pbo)
        M_pbf=self.mol_w(self.R_pbf)
        M_pbo=self.mol_w(R_pbo)
        T_pbf=self.temperature(self.R_pbf)
        T_pbo=self.temperature(R_pbo)
        #print(self.delta_p_f(self.p_pbf_k)/1e5,self.delta_p_o(self.p_pbf_k)/1e5,gamma_pbf,gamma_pbo,M_pbf,M_pbo,T_pbf,T_pbo)
        #c1=self.delta_p_f(R_pbo,self.R_pb[0])/self.eta_tf/self.rho_f/self.eta_pf
        c1=self.delta_p_f(self.p_pbf)/self.eta_tf/self.rho_f/self.eta_pf
        #c2=self.delta_p_o(R_pbo,self.R_pb[0])/self.eta_to/self.rho_o/self.eta_po
        c2=self.delta_p_o(self.p_pbf)/self.eta_to/self.rho_o/self.eta_po
        w_f=gamma_pbf/(gamma_pbf-1)*(self.R_0/M_pbf)*T_pbf*(1-(1/self.pi_tf())**(gamma_pbf-1/gamma_pbf))
        w_o=gamma_pbo/(gamma_pbo-1)*(self.R_0/M_pbo)*T_pbo*(1-(1/self.pi_to())**(gamma_pbo-1/gamma_pbo))
        return (self.R*c2*R_pbo/(1+R_pbo)-self.R*w_o)/(self.R*c2/(1+R_pbo)-w_o)
    
    def Go(self,R_pbf):     #obsolete   
        gamma_pbf=self.gamma(R_pbf)
        gamma_pbo=self.gamma(self.R_pbo)
        M_pbf=self.mol_w(R_pbf)
        M_pbo=self.mol_w(self.R_pbo)
        T_pbf=self.temperature(R_pbf)
        T_pbo=self.temperature(self.R_pbo)
        #c1=self.delta_p_f(R_pbo,self.R_pb[0])/self.eta_tf/self.rho_f/self.eta_pf
        c1=self.delta_p_f(self.p_pbf)/self.eta_tf/self.rho_f/self.eta_pf
        #c2=self.delta_p_o(R_pbo,self.R_pb[0])/self.eta_to/self.rho_o/self.eta_po
        c2=self.delta_p_o(self.p_pbf)/self.eta_to/self.rho_o/self.eta_po
        w_f=gamma_pbf/(gamma_pbf-1)*(self.R_0/M_pbf)*T_pbf*(1-(1/self.pi_tf())**(gamma_pbf-1/gamma_pbf))
        w_o=gamma_pbo/(gamma_pbo-1)*(self.R_0/M_pbo)*T_pbo*(1-(1/self.pi_to())**(gamma_pbo-1/gamma_pbo))
        return (-c1*R_pbf/(1+R_pbf)+self.R*w_f)/(-c1/(1+R_pbf)+w_f)
    
    def objective_function(self,x):
        self.R_pbf=x[0]
        self.R_pbo=x[1]
        errs=self.calculate_all_parameters(finding_eq=True,print_residuals=False)#,print_max_residual=True)
        return errs    
    
    def inner_convergence2(self):
        x=self.R_pb
        ans=root(self.objective_function,x,tol=1e-6)
        print(f"Equilibrium Ratios are {ans.x}")
        self.R_pb=ans.x
        self.R_pbf=ans.x[0]
        self.R_pbo=ans.x[1]

    def inner_convergence(self): #obsolete
        while True:
            Fu=np.array([self.R_pbf-self.Gf(self.R_pbo),
                        self.R_pbo-self.Go(self.R_pbf)])
            J=np.array([
                        [1, (-self.Gf(self.R_pbo+self.ho)+self.Gf(self.R_pbo))/self.ho],
                        [(-self.Go(self.R_pbf+self.hf)+self.Go(self.R_pbf))/self.hf, 1]
                        ])
            delta_R_pb=np.linalg.solve(J,-Fu)
            if np.linalg.norm(delta_R_pb/self.R_pb)<1e-9:
                print(f"{self.p_pbf} has converged")
                break
            self.R_pbf=self.R_pbf+delta_R_pb[0]#*self.hf
            self.R_pbo=self.R_pbo+delta_R_pb[1]#*self.ho
            self.R_pb=[self.R_pbf,self.R_pbo]
            #print(self.R_pb,np.linalg.norm(delta_R_pb/self.R_pb))
        #print(self.R_pbf,self.R_pbo)
        self.R_pbf=0.17
        self.R_pbo=58

    def calculate_all_parameters(self,check_residuals=True,finding_eq=False,print_residuals=False,print_max_residual=False):
        #print(f"Calculating parameters for {self.engine_name} engine")
        self.max_residual=0
        self.parameters={}
        self.parameters["Exit Diameter"]=self.exit_diameter()#((self.A_t*29.5)/np.pi)**0.5*2
        self.parameters["Isp"]=Isp=self.isp(self.R,self.p_c)
        self.parameters["Thrust"]=Thrust=self.m_z*self.parameters["Isp"]
        self.parameters["chamber pressure"]=p_c=self.m_z*self.cstar(self.R,self.p_c)/self.A_t
        self.parameters["fuel flow rate"]=m_f=self.m_z/(1+self.R)
        self.parameters["oxidiser flow rate"]=m_o=self.m_z/(1+self.R)*self.R
        self.parameters["fuel-rich turbine gas flow rate"]=m_tf=m_f*((self.R_pbo-self.R)*(1+self.R_pbf))/(self.R_pbo-self.R_pbf)
        self.parameters["oxidiser-rich turbine gas flow rate"]=m_to=m_o*((self.R-self.R_pbf) * (1 + self.R_pbo)) / ((self.R_pbo - self.R_pbf) * self.R)
        self.parameters["fuel flow rate of the fuel-rich preburner"]=m_ff=m_tf / (1 + self.R_pbf)
        self.parameters["oxidiser flow rate of the fuel-rich preburner"]=m_fo=m_tf*self.R_pbf / (1 + self.R_pbf)
        self.parameters["fuel flow rate of the oxidiser-rich preburner"]=m_of=m_to / (1 + self.R_pbo)
        self.parameters["oxidiser flow rate of the oxidiser-rich preburner"]=m_oo=m_to*self.R_pbo / (1 + self.R_pbo)
        self.parameters["outlet pressure of the fuel pump"]=p_f2=(self.p_f1 + self.delta_p_f(self.p_pbf))
        self.parameters["outlet pressure of the oxidizer pump"]=p_o2=(self.p_o1 + self.delta_p_o(self.p_pbf))
        self.parameters["inlet pressure of the fuel-rich turbine"]=p_f3=(self.p_pbf - self.C_f2 * p_c)
        self.parameters["inlet pressure of the oxidizer-rich turbine"]=p_o3=(self.p_pbo - self.C_o2 * p_c)
        self.parameters["outlet pressure of the fuel-rich turbine"]=p_f4=p_c * (1 + self.C_f3)
        self.parameters["outlet pressure of the oxidizer-rich turbine"]=p_o4=p_c * (1 + self.C_o3)
        self.parameters["fuel-rich turbine pressure ratio"]=pi_tf=p_f3/p_f4
        self.parameters["oxidizer-rich turbine pressure ratio"]=pi_to=p_o3/p_o4
        self.parameters["fuel pump head"]=delta_p_f=self.delta_p_f(self.p_pbf)
        self.parameters["oxidiser pump head"]=delta_p_o=self.delta_p_o(self.p_pbf)
        self.parameters["fuel turbopump power"]=P_f=m_f*delta_p_f/self.rho_f/self.eta_pf
        self.parameters["oxidiser turbopump power"]=P_o=m_o*delta_p_o/self.rho_o/self.eta_po
        self.parameters["fuel-rich turbine power"]=g_f=m_tf*self.eta_tf*self.gamma(self.R_pbf,self.p_pbf)/(self.gamma(self.R_pbf,self.p_pbf)-1)*(self.R_0/self.mol_w(self.R_pbf,self.p_pbf))*self.temperature(self.R_pbf,self.p_pbf)*(1-(1/pi_tf)**((self.gamma(self.R_pbf,self.p_pbf)-1)/self.gamma(self.R_pbf,self.p_pbf)))
        self.parameters["oxidiser-rich turbine power"]=g_o=m_to*self.eta_to*self.gamma(self.R_pbo,self.p_pbo)/(self.gamma(self.R_pbo,self.p_pbo)-1)*(self.R_0/self.mol_w(self.R_pbo,self.p_pbo))*self.temperature(self.R_pbo,self.p_pbo)*(1-(1/pi_to)**((self.gamma(self.R_pbo,self.p_pbo)-1)/self.gamma(self.R_pbo,self.p_pbo)))
        self.parameters["gamma in fuel rich preburner"]=gamma_pbf=self.gamma(self.R_pbf,self.p_pbf)
        self.parameters["gamma in oxidiser rich preburner"]=gamma_pbo=self.gamma(self.R_pbo,self.p_pbo)
        self.parameters["molecular weight in fuel rich preburner"]=M_pbf=self.mol_w(self.R_pbf,self.p_pbf)*1e3
        self.parameters["molecular weight in oxidiser rich preburner"]=M_pbo=self.mol_w(self.R_pbo,self.p_pbo)*1e3
        self.parameters["temperature in fuel rich preburner"]=T_pbf=self.temperature(self.R_pbf,self.p_pbf)
        self.parameters["temperature in oxidiser rich preburner"]=T_pbo=self.temperature(self.R_pbo,self.p_pbo)
        self.parameters["fuel rich preburner O/F"]=R_pbf=self.R_pbf
        self.parameters["oxidiser rich preburner O/F"]=R_pbo=self.R_pbo

        if check_residuals:
            eqs=[]
            eqs2=[]
            eqs.append((self.m_z-Thrust/Isp)) #1
            eqs.append((self.m_z-m_f-m_o)) #2
            eqs.append((p_c-self.m_z/self.A_t*self.cstar(self.R,self.p_c))) #3
            #eqs.append((self.F-C_f*self.A_t*P_c)/a)
            eqs.append((m_f-self.m_z/(1+self.R))) #4
            eqs.append((m_f-m_ff-m_of)) #5
            eqs.append((m_o-self.R*m_f)) #6
            eqs.append((m_o-m_fo-m_oo)) #7
            eqs.append((m_ff - m_tf / (1 + R_pbf))) #8
            eqs.append((m_fo - R_pbf * m_tf / (1 + R_pbf))) #9
            eqs.append((m_of - m_to / (1 + R_pbo))) #10
            eqs.append((m_oo - R_pbo * m_to / (1 + R_pbo))) #11
            eqs.append(m_tf - m_f*((R_pbo - self.R) * (1 + R_pbf)) / (R_pbo - R_pbf)) #12
            eqs.append(m_to - m_o*((self.R - R_pbf) * (1 + R_pbo)) / ((R_pbo - R_pbf) * self.R)) #13
            eqs.append((p_f2 - (self.p_f1 + delta_p_f))) #14
            eqs.append((p_o2 - (self.p_o1 + delta_p_o))) #15
            eqs.append((self.p_pbf - (p_f2 - self.C_f1 * p_c) / (1 + self.C_ff))) #16
            eqs.append((self.p_pbo - (p_o2 - self.C_o1 * p_c) / (1 + self.C_oo))) #17
            eqs.append((p_f3 - (self.p_pbf - self.C_f2 * p_c))) #18
            eqs.append((p_o3 - (self.p_pbo - self.C_o2 * p_c))) #19
            eqs.append((p_f4 - p_c * (1 + self.C_f3))) #20
            eqs.append((p_o4 - p_c * (1 + self.C_o3))) #21
            eqs.append(pi_tf - p_f3 / p_f4) #22
            eqs.append(pi_to - p_o3 / p_o4) #23
            eqs.append((delta_p_f-((1+self.C_ff)*self.p_pbf+self.C_f1*p_c-self.p_f1))) #24
            eqs.append((delta_p_o-((1+self.C_oo)*self.p_pbo-self.p_o1))) #25
            eqs.append(pi_tf-(self.p_pbf-self.C_f2*p_c)/(p_c*(1+self.C_f3)))#26
            eqs.append(pi_to-(self.p_pbo-self.C_o2*p_c)/(p_c*(1+self.C_o3))) #27
            eqs.append((p_o2-self.p_pbf*(1+self.C_fo))) #28
            eqs.append((p_o2-self.p_pbo*(1+self.C_oo)))#29
            eqs.append((p_f2-self.p_pbo*(1+self.C_of))/p_f2) #30
            eqs.append((p_f2-(self.p_pbf*(1+self.C_ff)+self.C_f1*p_c))) #31
            eqs.append(P_f-g_f) #32
            #eqs.append(P_f-p_f)
            eqs.append(P_o-g_o) #33
            #eqs.append(P_o-p_o)
            eqs.append(g_f-m_tf*self.eta_tf*self.gamma(self.R_pbf,self.p_pbf)/(self.gamma(self.R_pbf,self.p_pbf)-1)*(self.R_0/self.mol_w(self.R_pbf,self.p_pbf))*self.temperature(self.R_pbf,self.p_pbf)*(1-(1/pi_tf)**((self.gamma(self.R_pbf,self.p_pbf)-1)/self.gamma(self.R_pbf,self.p_pbf)))) #34
            eqs.append(g_o-m_to*self.eta_to*self.gamma(self.R_pbo,self.p_pbo)/(self.gamma(self.R_pbo,self.p_pbo)-1)*(self.R_0/self.mol_w(self.R_pbo,self.p_pbo))*self.temperature(self.R_pbo,self.p_pbo)*(1-(1/pi_to)**((self.gamma(self.R_pbo,self.p_pbo)-1)/self.gamma(self.R_pbo,self.p_pbo)))) #35
            eqs.append((P_f-m_f*delta_p_f/self.rho_f/self.eta_pf)) #36
            eqs.append((P_o-m_o*delta_p_o/self.rho_o/self.eta_po)) #37
            #eqs.append((delta_p_f-(R_pbo-self.R)*(1+R_pbf)/(R_pbo-R_pbf)*(self.eta_tf*self.rho_f*self.eta_pf)*(self.gamma_pbf/(self.gamma_pbf-1))*(self.R_0/self.M_pbf)*self.T_pbf*(1-(1/pi_tf)**(self.gamma_pbf-1/self.gamma_pbf)))/a)
            #eqs.append((delta_p_o-(self.R-R_pbf)*(1+R_pbf)/(R_pbo-R_pbf)*(self.eta_to*self.rho_o*self.eta_po)*(self.gamma_pbo/(self.gamma_pbo-1))*(self.R_0/self.M_pbo)*self.T_pbo*(1-(1/pi_to)**(self.gamma_pbo-1/self.gamma_pbo)))/a)

            eqs2.append(self.m_z) #1
            eqs2.append(self.m_z) #2
            eqs2.append(self.m_z) #3
            eqs2.append(m_f) #4
            eqs2.append(m_f) #5
            eqs2.append(m_o) #6
            eqs2.append(m_o) #7
            eqs2.append(m_ff) #8
            eqs2.append(m_fo) #9
            eqs2.append(m_of) #10
            eqs2.append(m_oo) #11
            eqs2.append(m_tf) #12
            eqs2.append(m_to) #13
            eqs2.append(p_f2) #14
            eqs2.append(p_o2) #15
            eqs2.append(self.p_pbf) #16
            eqs2.append(self.p_pbo) #17
            eqs2.append(p_f3) #18
            eqs2.append(p_o3) #19
            eqs2.append(p_f4) #20
            eqs2.append(p_o4) #21
            eqs2.append(pi_tf) #22
            eqs2.append(pi_to) #23
            eqs2.append(delta_p_f) #24
            eqs2.append(delta_p_o) #25
            eqs2.append(pi_tf) #26
            eqs2.append(pi_to) #27
            eqs2.append(p_o2) #28
            eqs2.append(p_o2) #29
            eqs2.append(p_f2) #30
            eqs2.append(p_f2) #31
            eqs2.append(P_f) #32
            eqs2.append(P_o) #33
            eqs2.append(g_f) #34
            eqs2.append(g_o) #35
            eqs2.append(P_f) #36
            eqs2.append(P_o) #37

            #eqs.append((delta_p_f-(R_pbo-self.R)*(1+R_pbf)/(R_pbo-R_pbf)*(self.eta_tf*self.rho_f*self.eta_pf)*(self.gamma_pbf/(self.gamma_pbf-1))*(self.R_0/self.M_pbf)*self.T_pbf*(1-(1/pi_tf)**(self.gamma_pbf-1/self.gamma_pbf)))/a)
            #eqs.append((delta_p_o-(self.R-R_pbf)*(1+R_pbf)/(R_pbo-R_pbf)*(self.eta_to*self.rho_o*self.eta_po)*(self.gamma_pbo/(self.gamma_pbo-1))*(self.R_0/self.M_pbo)*self.T_pbo*(1-(1/pi_to)**(self.gamma_pbo-1/self.gamma_pbo)))/a)
            if print_residuals:
                print("Residuals:")

            for i in range(0,len(eqs)):
                if print_residuals:
                    print(f"{i+1} : {round(eqs[i]/eqs2[i]*100,3)}%")
                if np.abs((eqs[i]/eqs2[i]))*100>self.max_residual:
                    self.max_residual=np.abs((eqs[i]/eqs2[i]))*100
        if print_max_residual:
            print(f"Max Residual = {round(self.max_residual,3)}%")
            '''
            print(f"Gamma in fuel rich preburner = {self.gamma(self.R_pbf,self.p_pbf)}")
            print(f"Gamma in oxidiser rich preburner = {self.gamma(self.R_pbo,self.p_pbo)}")
            print(f"Molecular weight in fuel rich preburner = {self.mol_w(self.R_pbf,self.p_pbf)*1e3} g/mol")
            print(f"Molecular weight in oxidiser rich preburner = {self.mol_w(self.R_pbo,self.p_pbo)*1e3} g/mol")
            print(f"Cp in fuel rich preburner = {self.gamma(self.R_pbf,self.p_pbf)/(self.gamma(self.R_pbf,self.p_pbf)-1)*(self.R_0/self.mol_w(self.R_pbf,self.p_pbf))} J/kgK")
            print(f"Cp in oxidiser rich preburner = {self.gamma(self.R_pbo,self.p_pbo)/(self.gamma(self.R_pbo,self.p_pbo)-1)*(self.R_0/self.mol_w(self.R_pbo,self.p_pbo))} J/kgK")
            print(f"Temperature in fuel rich preburner = {self.temperature(self.R_pbf,self.p_pbf)} K")
            print(f"Temperature in oxidiser rich preburner = {self.temperature(self.R_pbo,self.p_pbo)} K")
            print(f"Pressure ratio in fuel rich turbine = {pi_tf}")
            print(f"Pressure ratio in oxidiser rich turbine = {pi_to}")
            print(f"Mass flow rate through fuel rich turbine = {m_tf} kg/s")
            print(f"Mass flow rate through oxidiser rich turbine = {m_to} kg/s")
            print(f"Fuel Turbine Power = {m_tf*self.eta_tf*self.gamma(self.R_pbf,self.p_pbf)/(self.gamma(self.R_pbf,self.p_pbf)-1)*(self.R_0/self.mol_w(self.R_pbf,self.p_pbf))*self.temperature(self.R_pbf,self.p_pbf)*(1-(1/pi_tf)**((self.gamma(self.R_pbf,self.p_pbf)-1)/self.gamma(self.R_pbf,self.p_pbf)))}")
            print(f"Oxidiser Turbine Power = {m_to*self.eta_to*self.gamma(self.R_pbo,self.p_pbo)/(self.gamma(self.R_pbo,self.p_pbo)-1)*(self.R_0/self.mol_w(self.R_pbo,self.p_pbo))*self.temperature(self.R_pbo,self.p_pbo)*(1-(1/pi_to)**((self.gamma(self.R_pbo,self.p_pbo)-1)/self.gamma(self.R_pbo,self.p_pbo)))}")
            '''
        if finding_eq:
            return eqs[31]/eqs2[31],eqs[32]/eqs2[32]

    def get_output(self,print_residual=True):
        sys.stdout = open(self.output_file, 'a')
        print(f"***********************************************  {self.engine_name} ENGINE  ***********************************************")
        print()
        print(f"--- INPUT PARAMETERS ---\n")
        """
        df=pd.DataFrame.from_dict(self.data,orient="index")
        print(df.to_markdown())
        """
        #print("="*70)
        for key in self.data.keys():
            if ("pressure" in key and not("ratio" in key)) or "head" in key:
                print(f"{key} = {round(self.data[key]/1e5,2)} bar")
            elif "m_z" in key:
                print(f"{key} = {round(self.data[key],2)} kg/s")
            elif "A_t" in key:
                print(f"{key} = {round(self.data[key],4)} m^2")
            elif not("Thrust" in key or "p_c" in key):
                print(f"{key} = {self.data[key]}")
            #if not("Thrust" in key or "p_c" in key):
                #print("="*70)
        print()
        print("--- OUTPUT PARAMETERS ---\n")
        i=0
        #print("="*70)
        for key in self.parameters.keys():
            if "Exit Diameter" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key],3)} m")
            elif ("pressure" in key and not("ratio" in key)) or "head" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key]/1e5,2)} bar")
            elif "Isp" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key]/g,2)} s")
            elif "Thrust" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key]/1e3,2)} kN")
            elif "rate" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key],2)} kg/s")
            elif "power" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key]/1e6,2)} MW")
            elif "temperature" in key:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key],2)} K")
            else:
                print(f"{key} ({self.symbols[i]}) = {round(self.parameters[key],3)}")
            i+=1
            ##print("="*70)

        if print_residual:
            print()
            print(f"--- MAX RESIDUAL = {round(self.max_residual,9)}% ---")
        sys.stdout.close()
        sys.stdout = sys.__stdout__

    def run_injector_calculations(self):

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

        sys.stdout = open(self.output_file, 'a')

        print("=== Fuel-Rich Injector ===")
        print(f"Mass flow per hole: {mdot_fu_per_hole:.4f} kg/s")
        print(f"Number of fuel injectors: {N_fu:.1f}")

        print("\n=== Oxidizer-Rich Injector ===")
        print(f"Required mass flow per injector: {mdot_ox_target_per_inj:.4f} kg/s")
        print(f"Calculated oxidizer injector diameter: {d_ox_mm:.3f} mm")
        print(f"Actual mass flow per hole (verified): {mdot_ox_per_hole:.4f} kg/s")

        print(f"\nCheck — Local O/F from 1 FR + 4 OR injectors = {OF_local:.3f}")

        sys.stdout.close()
        sys.stdout = sys.__stdout__

    def calculate_chamber_dimensions(self, C_smd=2.5):

        m_z          = 53.12        # total mass flow (kg/s)
        deltaP_inj   = 1.2e6        # injector ΔP = 12 bar

        C_smd        = C_smd          # empirical constant
        gamma_gas    = 1.1301       # from CEA
        Cstar        = 1837.0       # m/s
        p_c_val      = 60e5         # Pa (60 bar)

        rho_o        = self.rho_o       # oxidiser density (kg/m^3)
        sigma_LOX    = 0.013        # N/m
        rho_LOX      = 1140.0       # kg/m³
        k_LOX        = 1327.8       # To be found s/m^2 
        D_pipe_LOX   = 0.4          # m

        rho_f        = self.rho_f        # fuel density (kg/m^3)
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

        sys.stdout = open(self.output_file, 'a')
        print(f"\nCOMPONENT DIMENSIONS")
        print("\n=== Gas Generator Dimensions ===")
        print(f"Diameter of Oxidiser rich chamber    : {D_chamber_LOX:.6g}")
        print(f"SMD LOX (microns)                    : {SMD_LOX_um:.6g}")
        print(f"Diameter of Fuel rich chamber        : {D_chamber_LCH4:.6g}")
        print(f"SMD LCH4 (microns)                   : {SMD_LCH4_um:.6g}")

        print("\n=== Main Combustion Chamber Dimensions ===")
        print(f"Chamber Length (m)            : {L_CC:.6g}")

        print()

        sys.stdout.close()
        sys.stdout = sys.__stdout__

    def run_multall(self):
        print("Running multall")
        #cygwin_mintty = r"C:\cygwin64\bin\mintty.exe"
        #project_dir = "/cygdrive/c/Users/lenovo/PycharmProjects/Multall_Codes"

        cwd = os.getcwd()

        cygwin_mintty = os.path.join(cwd, "cygwin", "bin", "mintty.exe")
        #cygwin_bash = os.path.join(cwd, "cygwin", "bin", "bash.exe")
        project_dir = os.path.join(cwd, "multall")

        # Convert Windows paths to Cygwin style for commands inside mintty
        project_dir_cyg = "/cygdrive/" + project_dir[0].lower() + project_dir[2:].replace("\\", "/")
        project_dir=project_dir_cyg

        commands = f'''cd {project_dir} && \
    echo "Compiling MEANGEN..." && \
    gfortran -o5 meangen-17.4.f -o meangen-17.4.x && \
    echo "Running MEANGEN with input file..." && \
    echo F | ./meangen-17.4.x < meangen.in && \
    echo "Compiling STAGEN..." && \
    gfortran -o5 stagen-17.3.f -o stagen-17.3.x && \
    echo "Running STAGEN..." && \
    ./stagen-17.3.x < stagen.dat && \
    echo "Compiling MULTALL..." && \
    gfortran -o5 multall-open-17.5.f -o multall-open-17.5.x && \
    echo "Running MULTALL..." && \
    ./multall-open-17.5.x < stage_new.dat ; '''#exec bash'''

        cmd = [
            cygwin_mintty,
            "-i", "/Cygwin-Terminal.ico",
            "-e", "/bin/bash", "-l", "-c", commands
        ]

        subprocess.Popen(cmd)
        
    def run_multall_2(self):

        cwd = os.getcwd()
        #cygwin_bash = os.path.join(cwd, "cygwin", "bin", "bash.exe")
        cygwin_bash = r"D:\cygwin\bin\bash.exe"
        project_dir = os.path.join(cwd, "multall")

        # Convert Windows path to Cygwin style
        project_dir_cyg = "/cygdrive/" + project_dir[0].lower() + project_dir[2:].replace("\\", "/")

        commands = f"""
        cd '{project_dir_cyg}' && \
        echo "Compiling MEANGEN..." && \
        gfortran -o5 meangen-17.4.f -o meangen-17.4.x && \
        echo "Running MEANGEN..." && \
        echo F | ./meangen-17.4.x < meangen.in && \
        echo "Compiling STAGEN..." && \
        gfortran -o5 stagen-17.3.f -o stagen-17.3.x && \
        echo "Running STAGEN..." && \
        ./stagen-17.3.x < stagen.dat && \
        echo "Compiling MULTALL..." && \
        gfortran -o5 multall-open-17.5.f -o multall-open-17.5.x && \
        echo "Running MULTALL..." && \
        ./multall-open-17.5.x < stage_new.dat && \
        echo "Multall tasks finished!"
        """

        # Run bash directly
        process = subprocess.Popen([cygwin_bash, "-l", "-c", commands])
        return_code = process.wait()

        print("Python: All Fortran commands completed. Exit code:", return_code)

        if return_code == 0:
            with open("multall/meangen.in", "r") as f:
                meangen_input = f.read()
            sys.stdout = open(self.output_file, 'a')
            print("\n=== MEANGEN Input File Contents ===")
            print(meangen_input)
            sys.stdout.close()
            sys.stdout = sys.__stdout__

    def write_meangen_file(self,params, output_file="multall/meangen.in"):
  
        def get_param(params, key, default=None):
            return params.get(key, default)
        
        with open(output_file, "w") as f:
            turbo_type = get_param(params, "compressor or turbine", "C")
            flow_type = get_param(params, "axial or radial", "AXI")
            gas_constant = get_param(params, "gas constant", "287.500")
            gamma = get_param(params, "gamma", "1.4")
            stagnation_pressure = get_param(params, "stagnation pressure in bar", "1.000")
            inlet_temp = get_param(params, "inlet temperature in deg K", "300.000")
            num_stages = get_param(params, "no of stages", "1")
            design_radius_choice = get_param(params, "design radius choice", "M")
            rpm = get_param(params, "input rpm", "5000.000")
            mass_flow = get_param(params, "mass flow rate", "50.000")
            vel_method = get_param(params, "velocity triangles method", "A")
            reaction = get_param(params, "reaction", "0.600")
            flow_coeff = get_param(params, "flow coefficient", "0.600")
            loading_coeff = get_param(params, "stage loading coeff", "0.350")
            radtype = get_param(params, "design radius type", "A")
            design_radius = get_param(params, "design radius", "0.500")
            blade_chord_1 = get_param(params, "first blade row axial chord", "0.050")
            blade_chord_2 = get_param(params, "second blade row axial chord", "0.040")
            row_gap = get_param(params, "row gap", "0.250")
            stage_gap = get_param(params, "interstage gap", "0.500")
            blockage_le = get_param(params, "blockage factor leading edge", "0.00000")
            blockage_te = get_param(params, "blockage factor trailing edge", "0.00000")
            efficiency = get_param(params, "stage efficiency", "0.900")
            deviation_angle_1 = get_param(params, "first row deviation angle", "5.000")
            deviation_angle_2 = get_param(params, "second row deviation angle", "5.000")
            incidence_1 = get_param(params, "first row incidence angle", "-2.000")
            incidence_2 = get_param(params, "second row incidence angle", "-2.000")
            blade_twist = get_param(params, "free vortex or no twist", "1.00000")
            blade_rotate = get_param(params, "rotate", "n")
            qo_le1 = get_param(params, "QO angle at LE row 1", "88.000")
            qo_te1 = get_param(params, "QO angle at TE row 1", "92.000")
            qo_le2 = get_param(params, "QO angle at LE row 2", "92.000")
            qo_te2 = get_param(params, "QO angle at TE row 2", "88.000")
            change_angles = get_param(params, "change angles", "n")
            all_rows_output = get_param(params, "output for all blade rows", "Y")

            # Write 
            f.write(f'{turbo_type}                        TURBO_TYP,"C" FOR A COMPRESSOR,"T" FOR A TURBINE\n')
            f.write(f'{flow_type}                      FLO_TYP FOR AXIAL OR MIXED FLOW MACHINE \n')
            f.write(f'   {gas_constant}     {gamma}     GAS PROPERTOES, RGAS, GAMMA \n')
            f.write(f'     {stagnation_pressure}   {inlet_temp}     POIN,  TOIN \n')
            f.write(f'    {num_stages}                    NUMBER OF STAGES IN THE MACHINE \n')
            f.write(f'{design_radius_choice}                        CHOICE OF DESIGN POINT RADIUS, HUB, MID or TIP\n')
            f.write(f'    {rpm}             ROTATION SPEED, RPM \n')
            f.write(f'      {mass_flow}             MASS FLOW RATE, FLOWIN. \n')
            f.write(f'{vel_method}                        INTYPE, TO CHOOSE THE METHOD OF DEFINING THE VELOCITY TRIANGLES\n')
            f.write(f'  {reaction}  {flow_coeff}  {loading_coeff}    REACTION, FLOW COEFF., LOADING COEFF.\n')
            f.write(f'{radtype}                        RADTYPE, TO CHOOSE THE DESIGN POINT RADIUS\n')
            f.write(f'       {design_radius}             THE DESIGN POINT RADIUS \n')
            f.write(f'       {blade_chord_1}       {blade_chord_2} BLADE AXIAL CHORDS IN METRES.\n')
            f.write(f'       {row_gap}       {stage_gap} ROW GAP  AND STAGE GAP \n')
            f.write(f'   {blockage_le}   {blockage_te}     BLOCKAGE FACTORS, FBLOCK_LE,  FBLOCK_TE \n')
            f.write(f'       {efficiency}             GUESS OF THE STAGE ISENTROPIC EFFICIENCY\n')
            f.write(f'   {deviation_angle_1}   {deviation_angle_2}         ESTIMATE OF THE FIRST AND SECOND ROW DEVIATION ANGLES\n')
            f.write(f'  {incidence_1}  {incidence_2}         FIRST AND SECOND ROW INCIDENCE ANGLES\n')
            f.write(f'   {blade_twist}               BLADE TWIST OPTION, FRAC_TWIST\n')
            f.write(f'{blade_rotate}                        BLADE ROTATION OPTION , Y or N\n')
            f.write(f'  {qo_le1}  {qo_te1}         QO ANGLES AT LE  AND TE OF ROW 1 \n')
            f.write(f'  {qo_le2}  {qo_te2}         QO ANGLES AT LE  AND TE OF ROW 2 \n')
            f.write(f'{change_angles}                        DO YOU WANT TO CHANGE THE ANGLES FOR THIS STAGE ? "Y" or "N"\n')
            f.write(f'{all_rows_output}                        IS OUTPUT REQUESTED FOR ALL BLADE ROWS ? \n')
            # Template for following lines, fill with defaults or input mapping as needed:
            f.write('Y    ROTOR No.   1 SET ANSTK = "Y" TO USE THE SAME  BLADE SECTIONS AS THE LAST STAGE\n')
            f.write('N    STATOR No.  1 SET ANSTK = "Y" TO USE THE SAME  BLADE SECTIONS AS THE LAST STAGE\n')
            f.write('  0.1000  0.4500         MAX THICKNESS AND ITS LOCATION FOR STATOR  1 SECTION No.  1\n')
            f.write('  0.1000  0.4500         MAX THICKNESS AND ITS LOCATION FOR STATOR  1 SECTION No.  2\n')
            f.write('  0.1000  0.4500         MAX THICKNESS AND ITS LOCATION FOR STATOR  1 SECTION No.  3\n')
            print(f"meangen.in successfully created at:\n{output_file}")

    def main(self):

        print("Calculating equilibrium\n")
        #eng=engine("2400kn_new_code")
        self.inner_convergence2()
        self.calculate_all_parameters(print_residuals=False,print_max_residual=True)
        self.get_output()
        print("Calculating injector dimensions\n")
        self.calculate_chamber_dimensions()
        print("Calculating turbine dimensions\n")
        self.run_injector_calculations()
        print("Calculating combustion chamber size\n")
        
        meangen_params = {
                "type": "T",
                "configuration": "AXI",
                "gas_constant": 287.500,
                "gamma": 1.1300,
                "stagnation_pressure_bar": 800,
                "inlet_temperature_K": 1000.000,
                "num_stages": 2,
                "design_radius_choice": "M",
                "rpm": 5000.000,
                "mass_flow_rate": 50.000,
                "velocity_triangles_method": "A",
                "reaction": 0.600,
                "flow_coefficient": 0.600,
                "stage_loading_coeff": 0.350,
                "design_radius_type": "A",
                "design_radius": 0.500,
                "first_axial_chord": 0.050,
                "second_axial_chord": 0.040,
                "row_gap": 0.250,
                "interstage_gap": 0.500,
                "blockage_factor_LE": 0.00000,
                "blockage_factor_TE": 0.00000,
                "stage_efficiency": 0.900,
                "first_row_deviation_angle": 5.000,
                "second_row_deviation_angle": 5.000,
                "first_row_incidence_angle": -2.000,
                "second_row_incidence_angle": -2.000,
                "free_vortex_or_no_twist": 1.00000,
                "rotate": "n",
                "qo_angle_LE_row1": 88.000,
                "qo_angle_TE_row1": 92.000,
                "qo_angle_LE_row2": 92.000,
                "qo_angle_TE_row2": 88.000,
                "change_angles": "n",
                "output_all_rows": "Y",
                "rotor1_ANSTK": "Y",
                "stator1_ANSTK": "N",
                "stator1_section1": {"max_thickness": 0.1000, "location": 0.4500},
                "stator1_section2": {"max_thickness": 0.1000, "location": 0.4500},
                "stator1_section3": {"max_thickness": 0.1000, "location": 0.4500},
            }
        
        self.write_meangen_file(meangen_params)
        self.run_multall_2()

eng=engine("2400kn_new_code")
eng.main()