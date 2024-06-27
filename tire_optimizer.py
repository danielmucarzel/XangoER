import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt

class Dynamics:
    def __init__(self, spring_type, spring_k, spring_F, spring_non_lin_coef, tire_Fz, tire_Sa, tire_Ls):
        # Modelo de mola
        self.spring_type = spring_type  # Hooke, Softening
        self.spring_k = spring_k  # rigidez da mola [N/m]
        self.spring_F = spring_F  # força que a mola recebe [N]
        self.spring_non_lin_coef = spring_non_lin_coef  # coeficiente de ganho não-linear
        # Modelo de pneu
        self.tire_Fz = tire_Fz  # carga vertical no pneu [N]
        self.tire_Sa = tire_Sa  # slip angle do pneu [rad]
        self.tire_Ls = tire_Ls  # longitudinal slip do pneu [Admensional]
        self.tire_type = 'Default'

    def Tire(self, params):
        E, Cy, Cx, Cz, c1, c2 = params
        Cs = c1 * np.sin(2 * np.arctan(self.tire_Fz / c2))
        D = 1.5 * self.tire_Fz
        Bz = Cs / (Cz * D)
        Bx = Cs / (Cx * D)
        By = Cs / (Cy * D)
        tire_lateral_force = D * np.sin(Cy * np.arctan(By * self.tire_Sa - E * (By * self.tire_Sa - np.arctan(By * self.tire_Sa))))
        tire_auto_align_moment = D * np.sin(Cz * np.arctan(Bz * self.tire_Sa - E * (Bz * self.tire_Sa - np.arctan(Bz * self.tire_Sa))))
        tire_longitudinal_force = D * np.sin(Cx * np.arctan(Bx * self.tire_Ls - E * (Bx * self.tire_Ls - np.arctan(Bx * self.tire_Ls))))

        return tire_lateral_force, (12 + (tire_auto_align_moment/58)), tire_longitudinal_force

# Dados experimentais
angles = np.array([-9.0, -8.0, -7.0, -6.0, -5.0, -4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
tire_lateral_forces_1 = np.array([-2300, -2200, -2060, -1880, -1680, -1450, -1190, -850, -430, 60, 520, 890, 1170, 1390, 1580, 1730, 1890, 2000, 2090])
tire_auto_align_moment_1 = np.array([-28.84, -28.68, -27.21, -26.41, -27.70, -24.21, -24.15, -15.88, -4.91, 14.72, 33.80, 43.79, 46.93, 49.09, 50.90, 50.10, 50.81, 48.12, 48.83])

# Instanciando a classe Dynamics
dynamics_instance = Dynamics(spring_type="Hooke", spring_k=1000, spring_F=500, spring_non_lin_coef=0.1, tire_Fz=1500, tire_Sa=angles, tire_Ls=0.1)

# Função de erro total
def total_error(params):
    predicted_tire_lateral_forces, predicted_tire_auto_align_moment = dynamics_instance.Tire(params)
    sq_errors_lateral_force = (predicted_tire_lateral_forces - tire_lateral_forces_1) ** 2
    sq_errors_auto_align_moment = (predicted_tire_auto_align_moment - tire_auto_align_moment_1) ** 2
    total_error = np.sum(sq_errors_lateral_force) + np.sum(sq_errors_auto_align_moment)
    return total_error

# Restrições dos parâmetros
param_bounds = [(-2, 1.2), (1, 3), (1, 3), (1, 3), (1000, 10000), (1, 5000)]

# Minimizando o erro total com restrições nos parâmetros usando busca em grade
result = opt.brute(total_error, param_bounds, finish = None)

# Imprimindo os parâmetros otimizados
print("Parâmetros otimizados:")
print("E:", result[0])
print("Cy:", result[1])
print("Cx:", result[2])
print("Cz:", result[3])
print("c1:", result[4])
print("c2:", result[5])

# Calculando o erro total com os parâmetros otimizados
total_error_optimized = total_error(result)
print("Erro total com parâmetros otimizados:", total_error_optimized)

# Plotagem da curva otimizada com os dados experimentais
predicted_tire_lateral_forces, predicted_tire_auto_align_moment = dynamics_instance.Tire(result)
plt.figure(figsize=(18, 7))  # Definindo um tamanho para a figura

# Plotagem força lateral
plt.subplot(1, 2, 1)
plt.plot(angles, predicted_tire_lateral_forces, label='Curva Otimizada')
plt.scatter(angles, tire_lateral_forces_1, color='red', label='Dados Experimentais')
plt.xlabel('Ângulo de Deslizamento Lateral (graus)')
plt.ylabel('Força Lateral do Pneu (N)')
plt.title('Força Lateral do Pneu - Comparação da Curva Otimizada com os Dados Experimentais')
plt.legend()
plt.grid(True)

# Plotagem torque auto-alinhante
plt.subplot(1, 2, 2)
plt.plot(angles, predicted_tire_auto_align_moment, label='Curva Otimizada')
plt.scatter(angles, tire_auto_align_moment_1, color='blue', label='Dados Experimentais')
plt.xlabel('Ângulo de Deslizamento Lateral (graus)')
plt.ylabel('Torque auto-alinhante (N.m)')
plt.title('Torque Auto-alinhante - Comparação da Curva Otimizada com os Dados Experimentais')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
