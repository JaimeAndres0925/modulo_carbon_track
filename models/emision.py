from odoo import models, fields

class CarbonTRackEmision(models.Model):
    _name = 'carbon.track.emision'
    _description = 'Factores de emisión'
    # Dentro de la clase CarbonTrackEmision en emision.py
    fuente_externa_id = fields.Many2one('carbon.track.fuente.externa', string='Fuente de Datos')
    
    name = fields.Char(string='Nombre del Factor', required= True) 
    fuentes = fields.Char(string = 'Fuentes') 
    valor = fields.Float(string= 'Valor (kg CO2e por unidad)') 
    unidad = fields.Char(string = 'Unidad (kWh, litros, etc.)') 
    valido_desde = fields.Date(string= 'Valido desde') 
    valido_hasta = fields.Date(string= 'Valido hasta') 
    categoria = fields.Char(string = 'Categoria') 
     