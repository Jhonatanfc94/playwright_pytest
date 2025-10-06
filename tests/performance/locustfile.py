import logging
from locust import HttpUser, task, between, LoadTestShape

# Configura el logging
logging.basicConfig(level=logging.INFO)

class CayalaVisitor(HttpUser):
    wait_time = between(5, 10)
    host = "https://cba.ucb.edu.bo/"

    def on_start(self):
        """Se ejecuta una vez por usuario virtual al inicio."""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9", # Cambiado a español de España, más común
        }

    @task(10)
    def visit_homepage(self):
        """Visita la página principal y valida el contenido."""
        with self.client.get("/", headers=self.headers, catch_response=True, name="/") as response:
            logging.info(f"Visitando homepage: {response.status_code}")
            
            # Validación del código de estado
            if response.status_code != 200:
                response.failure(f"El código de estado no es 200, fue: {response.status_code}")
                return # Detiene la ejecución de esta tarea si el estado no es 200

            # Validación de contenido real
            expected_title = "Universidad Católica Boliviana"
            if expected_title not in response.text:
                response.failure(f"El texto '{expected_title}' no se encontró en la página principal.")
            
            # Validación de tiempo de respuesta
            if response.elapsed.total_seconds() > 5:
                response.failure(f"El tiempo de respuesta fue mayor a 5s: {response.elapsed.total_seconds()}s")

    @task(8)
    def explore_sections(self):
        """Explora secciones clave y valida su contenido."""
        sections = [
            "/oferta-pregrado/",
            # Puedes agregar más secciones aquí para hacer la prueba más realista
            # "/vida-universitaria/",
            # "/admisiones/",
        ]
        for section in sections:
            with self.client.get(section, headers=self.headers, name="/[seccion]", catch_response=True) as response:
                logging.info(f"Visitando sección {section}: {response.status_code}")
                
                if response.status_code != 200:
                    response.failure(f"El código de estado para {section} no es 200, fue: {response.status_code}")
                    continue # Salta a la siguiente sección si esta falla

                # Validación de contenido real para la sección
                expected_text = "Oferta Pregrado"
                if expected_text not in response.text:
                    response.failure(f"El texto '{expected_text}' no se encontró en la sección {section}.")
                
                if response.elapsed.total_seconds() > 5:
                    response.failure(f"El tiempo de respuesta para {section} fue mayor a 5s: {response.elapsed.total_seconds()}s")

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
