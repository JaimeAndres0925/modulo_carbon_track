from odoo import models, fields, api
from odoo.exceptions import UserError
import requests

class CarbonTrackFuenteExterna(models.Model):
    _name = 'carbon.track.fuente.externa'
    _description = 'Conexión a APIs Oficiales (Climatiq)'

    name = fields.Char(string='Nombre de la Fuente', default='Climatiq API (EPA/DEFRA)', required=True)
    api_key = fields.Char(string='API Key (Token)', required=True, groups="modulo_carbon_track.group_carbon_track_manager")
    base_url = fields.Char(string='URL Base', default='https://beta4.api.climatiq.io/search', required=True)
    
    estado = fields.Selection([
        ('borrador', 'Sin Conectar'),
        ('conectado', 'Conexión Exitosa'),
        ('error', 'Error de Conexión')
    ], string='Estado', default='borrador', readonly=True)

    ultima_sincronizacion = fields.Datetime(string='Última Sincronización', readonly=True)

    def action_test_connection(self):
        """ Prueba que la API Key es válida """
        self.ensure_one()
        headers = {'Authorization': f'Bearer {self.api_key}'}
        

        parametros_prueba = {
            'results_per_page': 30,     
            'region': 'ES',             
            'data_version': '^5'
        }
        
        try:
            response = requests.get(self.base_url, headers=headers, params=parametros_prueba, timeout=10)
            
            if response.status_code == 200:
                self.estado = 'conectado'
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': '¡Conexión Exitosa!',
                        'message': 'Odoo se ha comunicado correctamente con Climatiq.',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            elif response.status_code == 401:
                self.estado = 'error'
                raise UserError("Error 401: API Key incorrecta. Revisa que no haya espacios al copiarla.")
            else:
                self.estado = 'error'
                raise UserError(f"Error de la API: {response.status_code} - Detalles: {response.text}")
                
        except requests.exceptions.RequestException as e:
            self.estado = 'error'
            raise UserError(f"No se pudo conectar a Internet o a la API: {str(e)}")

    def action_sync_factors(self):
        self.ensure_one()
        if self.estado != 'conectado':
            raise UserError("¡Prueba la conexión primero!")

        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        anio_actual = fields.Date.today().year

        parametros_busqueda = {
            'results_per_page': 30,     
            'region': 'ES',             
            'data_version': '^5'
        }

        try:
            response_search = requests.get(self.base_url, headers=headers, params=parametros_busqueda, timeout=15)
            if response_search.status_code != 200:
                raise UserError(f"Error en búsqueda: {response_search.status_code}")
                
            resultados = response_search.json().get('results', [])
            
            importados = 0
            existentes = 0
            nulos = 0
            # Cambio para poder hacer una consulta
            url_estimate = self.base_url.replace('/search', '/estimate')
            
            for item in resultados:
                activity_id = item.get('activity_id')
                dataset_info = item.get('source_dataset', 'Climatiq Default')   
                if not activity_id:
                    continue
                    
                nombre_completo = f"{item.get('name', 'Factor')} ({item.get('year', fields.Date.today().year)}) - {item.get('region', 'Global')}"
                
                if self.env['carbon.track.emision'].search([('name', '=', nombre_completo)], limit=1):
                    existentes += 1
                    continue
                
                tipo_unidad = item.get('unit_type')
                payload_estimacion = {
                    "emission_factor": {
                        "activity_id": activity_id,
                        "data_version": "^5"
                    },
                    "parameters": {}
                }
                unidad_final = 'u'
                
                if tipo_unidad == 'Energy':
                    payload_estimacion['parameters'] = {"energy": 1, "energy_unit": "kWh"}
                    unidad_final = 'kWh' # Energia
                elif tipo_unidad == 'Weight':
                    payload_estimacion['parameters'] = {"weight": 1, "weight_unit": "kg"}
                    unidad_final = 'kg'  # Peso 
                elif tipo_unidad == 'Volume':
                    payload_estimacion['parameters'] = {"volume": 1, "volume_unit": "l"}
                    unidad_final = 'l'   # Volumen
                elif tipo_unidad == 'Distance':
                    payload_estimacion['parameters'] = {"distance": 1, "distance_unit": "km"}
                    unidad_final = 'km'  # Distancia
                elif tipo_unidad == 'Passenger-Distance':
                    payload_estimacion['parameters'] = {"passenger_distance": 1, "passenger_distance_unit": "km"}
                    unidad_final = 'pkm' # Pasajero-kilómetro (Viajes)
                elif tipo_unidad == 'Money':
                    payload_estimacion['parameters'] = {"money": 1, "money_unit": "eur"}
                    unidad_final = '€'   # Gasto económico (Compras)
                elif tipo_unidad == 'Time':
                    payload_estimacion['parameters'] = {"time": 1, "time_unit": "h"}
                    unidad_final = 'h'   # Horas (Uso de maquinaria)
                elif tipo_unidad == 'Number':
                    payload_estimacion['parameters'] = {"number": 1}
                    unidad_final = 'ud'  # Unidades (Ej: Noches de hotel, equipos)
                else:
                    nulos += 1
                    continue
                    
                res_est = requests.post(url_estimate, headers=headers, json=payload_estimacion, timeout=10)
                
                if res_est.status_code == 200:
                    datos_est = res_est.json()
                    valor_co2e = float(datos_est.get('co2e', 0.0)) 
                    
                    anio = item.get('year', fields.Date.today().year)
                    fecha_inicio = f"{anio}-01-01"
                    fecha_fin = f"{anio}-12-31"
                    cat_api = item.get('category', 'General')
                    
                    self.env['carbon.track.emision'].create({
                        'name': nombre_completo,
                        'valor': valor_co2e,
                        'fuentes': dataset_info,
                        'unidad': unidad_final,
                        'es_oficial': True,
                        'categoria': cat_api,
                        'valido_desde': fecha_inicio,
                        'valido_hasta': fecha_fin,
                    })
                    importados += 1
                else:
                    nulos += 1

            self.ultima_sincronizacion = fields.Datetime.now()
            #Devolvemos una notificación con los FE importados existentes y descartados
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '¡Sincronización Completada!',
                    'message': f'Nuevos: {importados} | Existentes: {existentes} | Descartados: {nulos}',
                    'type': 'success',
                    'sticky': True,
                }
            }
            
        except requests.exceptions.RequestException as e:
            raise UserError(f"Error de red/conexión: {str(e)}")