import uuid
import logging
from locust import HttpUser, SequentialTaskSet, task, between, LoadTestShape, events

# Configura el logging
logging.basicConfig(level=logging.INFO)

class UserLifecycleBehavior(SequentialTaskSet):
    """
    Define el comportamiento secuencial de un usuario virtual.
    Fase 1: Registro -> Fase 2: Login -> Fase 3: Eliminar -> Fin.
    """
    def on_start(self):
        # Se ejecuta cuando el usuario virtual "nace".
        self.username = f"locust_user_{uuid.uuid4().hex[:8]}"
        self.password = "LoadTestPass123!"
        self.headers = {"Content-Type": "application/json"}

    @task
    def phase_1_register(self):
        payload = {"username": self.username, "password": self.password}
        with self.client.post("/register", json=payload, headers=self.headers, catch_response=True, name="/register") as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"Fallo en Registro: Código {response.status_code} - {response.text}")

    @task
    def phase_2_login(self):
        payload = {"username": self.username, "password": self.password}
        with self.client.post("/login", json=payload, headers=self.headers, catch_response=True, name="/login") as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                response.failure("Credenciales incorrectas al intentar login.")
            else:
                response.failure(f"Fallo en Login: Código {response.status_code} - {response.text}")

    @task
    def phase_3_delete(self):
        with self.client.delete(f"/user/{self.username}", catch_response=True, name="/user/[username]") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Fallo al Eliminar: Código {response.status_code} - {response.text}")

    @task
    def finish_lifecycle(self):
        # Detiene la secuencia actual para este usuario, permitiendo que nazca uno nuevo.
        self.interrupt()

class ApiLoadTester(HttpUser):
    # Asignamos el comportamiento secuencial
    tasks = [UserLifecycleBehavior]
    
    # Tiempo de espera entre peticiones (ajustado de 1 a 3 segundos para fluidez de API)
    # Puedes regresarlo a between(5, 10) si prefieres simular un usuario más lento
    wait_time = between(1, 3) 
    
    # URL de tu backend Flask
    host = "http://localhost:5000"

# --- HOOK FINAL BASADO EN TUS CRITERIOS ---
@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Verifica los criterios de éxito usando las estadísticas de Locust.
    """
    logging.info("--- INICIANDO VERIFICACIÓN DE CRITERIOS DE ÉXITO ---")
    
    # Criterio 1: Tasa de fallos (Tolerancia Cero)
    if environment.stats.total.fail_ratio > 0.0:
        logging.error(f"Prueba fallida: La tasa de fallos fue de {environment.stats.total.fail_ratio:.2%}, se requiere tolerancia cero.")
        environment.process_exit_code = 1
        return

    # Criterio 2: Rendimiento (Percentil 95 > 200 ms)
    p95_response_time = environment.stats.total.get_response_time_percentile(0.95)
    logging.info(f"Reporte de SLO: Percentil 95 del tiempo de respuesta = {p95_response_time:.2f} ms")
    
    # Nota: 200ms para una API local en Flask suele cumplirse, pero si falla, 
    # es porque la encriptación de bcrypt (que agregamos) consume CPU intencionalmente.
    if p95_response_time > 200:
        logging.error(f"Prueba fallida: El percentil 95 ({p95_response_time:.2f} ms) superó el umbral de 200 ms.")
        environment.process_exit_code = 1
        return

    logging.info("Prueba exitosa: Todos los criterios de rendimiento y funcionales se cumplieron.")
    environment.process_exit_code = 0

# --- TU SIMULADOR DE TRÁFICO (LOAD SHAPE) ---
class DailyTrafficShape(LoadTestShape):
    """
    Demo de concurrencia y cuello de botella en I/O.
    Stage 1: Comportamiento ideal (1 usuario). Todo fluye.
    Stage 2: Tráfico concurrente (20 usuarios de golpe). El archivo .txt colapsa.
    """
    stages = [
        {"duration": 30, "users": 1, "spawn_rate": 1},   # Etapa 1: Paz y tranquilidad
        {"duration": 60, "users": 20, "spawn_rate": 10}, # Etapa 2: Caos controlado
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
            run_time -= stage["duration"]

        return None