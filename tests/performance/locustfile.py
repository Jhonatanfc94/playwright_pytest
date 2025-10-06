import logging
from locust import HttpUser, task, between, LoadTestShape, events

# Configura el logging
logging.basicConfig(level=logging.INFO)

class CayalaVisitor(HttpUser):
    wait_time = between(5, 10)
    host = "https://cba.ucb.edu.bo/"

    def on_start(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9",
        }

    @task(10)
    def visit_homepage(self):
        with self.client.get("/", headers=self.headers, catch_response=True, name="/") as response:
            if not response.ok:
                response.failure(f"FALLO DE CONEXIÓN: Código de estado {response.status_code}")
                return

            # FALLO FUNCIONAL: El contenido es incorrecto. Esto es un bug.
            expected_title = "Universidad Católica Boliviana"
            if expected_title not in response.text:
                response.failure(f"FALLO DE CONTENIDO: El texto '{expected_title}' no se encontró.")
            
            # NOTA: Ya no marcamos la lentitud como un fallo aquí.

    @task(8)
    def explore_sections(self):
        with self.client.get("/oferta-pregrado/", headers=self.headers, name="/[seccion]", catch_response=True) as response:
            if not response.ok:
                response.failure(f"FALLO DE CONEXIÓN: Código de estado {response.status_code}")
                return

            # FALLO FUNCIONAL: El contenido es incorrecto.
            expected_text = "Oferta Pregrado"
            if expected_text not in response.text:
                response.failure(f"FALLO DE CONTENIDO: El texto '{expected_text}' no se encontró.")

# --- HOOK FINAL BASADO 100% EN LA DOCUMENTACIÓN OFICIAL ---
@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Se ejecuta al final de la prueba para verificar todos nuestros criterios de éxito
    usando únicamente las estadísticas integradas de Locust.
    """
    logging.info("--- INICIANDO VERIFICACIÓN DE CRITERIOS DE ÉXITO ---")
    
    # Criterio 1: Tasa de fallos funcionales (Tolerancia Cero)
    # environment.stats.total.fail_ratio solo cuenta los response.failure() que definimos.
    if environment.stats.total.fail_ratio > 0.0:
        logging.error(f"Prueba fallida: La tasa de fallos de contenido/conexión fue de {environment.stats.total.fail_ratio:.2%}, se requiere tolerancia cero.")
        environment.process_exit_code = 1
        return

    # Criterio 2: Rendimiento (Percentil 95 > 5 segundos)
    # Esto significa: "fallar si el 5% de las peticiones más lentas superaron los 5000ms".
    p95_response_time = environment.stats.total.get_response_time_percentile(0.95)
    logging.info(f"Reporte de SLO: Percentil 95 del tiempo de respuesta = {p95_response_time:.2f} ms")
    if p95_response_time > 800:
        logging.error(f"Prueba fallida: El percentil 95 ({p95_response_time:.2f} ms) superó el umbral de 5000 ms.")
        environment.process_exit_code = 1
        return

    # Si llegamos aquí, todos los criterios pasaron
    logging.info("Prueba exitosa: Todos los criterios de rendimiento y funcionales se cumplieron.")
    environment.process_exit_code = 0

class DailyTrafficShape(LoadTestShape):
    """
    Define una forma de carga personalizada que simula un patrón de tráfico.
    Stage 1: 1 minuto con 1 usuario para calentar.
    Stage 2: 2 minutos con 3 usuarios para simular una carga ligera.
    """
    stages = [
        {"duration": 60, "users": 1, "spawn_rate": 1},
        {"duration": 120, "users": 3, "spawn_rate": 5},
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
            run_time -= stage["duration"]

        return None