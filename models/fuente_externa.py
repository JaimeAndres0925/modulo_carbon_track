import requests
from odoo import models, fields

class CarbonTrackFuenteExterna(models.Model):
    _name = 'carbon.track.fuente.externa'
    _description = 'Fuentes externas de factores de emisión'

    nombre = fields.Char(string='Nombre de la Fuente', required=True)
    url_api = fields.Char(string='URL de la API')
    clave_api = fields.Char(string='Clave API / Token')
    ultima_sincronizacion = fields.Datetime(string='Última Sincronización')
    
    factor_ids = fields.One2many(
        'carbon.track.emision', 
        'fuente_externa_id', 
        string='Factores de Emisión'
    )
    
    