import requests
import json
class SICAESApiClient:
    def __init__(self):
        self.url_base = "https://api.simulada.ministerio.es/v1" 

    def enviar_cae(self, data):
        # Para tu TFG, simulamos la respuesta si no tienes la API real
        try:
            # payload = json.dumps(data)
            # response = requests.post(f"{self.url_base}/certificar", data=payload)
            return {"status": "success", "id_cae": "CAE-2024-00123"}
        except Exception as e:
            return {"status": "error", "message": str(e)}   