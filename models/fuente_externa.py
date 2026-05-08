from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import json

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
        
        # Pedimos data_version porque Climatic
        parametros_prueba = {
            'query': 'electricity', 
            'results_per_page': 1,
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
        
        # 1. Búsqueda de los catálogos
        parametros_busqueda = {
            'category': 'Electricity', 
            'results_per_page': 5,
            'data_version': '^5'
        }

        try:
            # Llamamos al buscador normal
            response_search = requests.get(self.base_url, headers=headers, params=parametros_busqueda, timeout=15)
            if response_search.status_code != 200:
                raise UserError(f"Error en búsqueda: {response_search.status_code}")
                
            resultados = response_search.json().get('results', [])
            
            importados = 0
            existentes = 0
            nulos = 0
            
            url_estimate = self.base_url.replace('/search', '/estimate')
            
            for item in resultados:
                activity_id = item.get('activity_id')
                if not activity_id:
                    continue
                    
                nombre_completo = f"{item.get('name', 'Factor')} ({item.get('year', '2024')}) - {item.get('region', 'Global')}"
                
                # Si ya lo tenemos, nos ahorramos la segunda llamada
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
                    unidad_final = 'kWh'
                elif tipo_unidad == 'Weight':
                    payload_estimacion['parameters'] = {"weight": 1, "weight_unit": "kg"}
                    unidad_final = 'kg'
                elif tipo_unidad == 'Volume':
                    payload_estimacion['parameters'] = {"volume": 1, "volume_unit": "l"}
                    unidad_final = 'l'
                else:
                    # Si es una magnitud que no se contenpla, la saltamos para no complicarlo
                    nulos += 1
                    continue
                    
                # 3. Disparamos la consulta oculta de estimación
                res_est = requests.post(url_estimate, headers=headers, json=payload_estimacion, timeout=10)
                
                if res_est.status_code == 200:
                    datos_est = res_est.json()
                    valor_co2e = float(datos_est.get('co2e', 0.0)) 
                    
                    self.env['carbon.track.emision'].create({
                        'name': nombre_completo,
                        'valor': valor_co2e,
                        'unidad': unidad_final,
                        'es_oficial': True,
                    })
                    importados += 1
                else:
                    nulos += 1

            self.ultima_sincronizacion = fields.Datetime.now()
            

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