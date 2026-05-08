from odoo import models, fields

class CarbonTRackEmision(models.Model):
    _name = 'carbon.track.emision'
    _description = 'Factores de emisión'

    fuente_externa_id = fields.Many2one('carbon.track.fuente.externa', string='Fuente de Datos')
    
    name = fields.Char(string='Nombre del Factor', required= True) 
    fuentes = fields.Char(string = 'Fuentes') 
    valor = fields.Float(string= 'Valor (kg CO2e por unidad)', required= True, digits=(12,6)) 
    unidad = fields.Char(string = 'Unidad (kWh, litros, etc.)') 
    valido_desde = fields.Date(string= 'Valido desde') 
    valido_hasta = fields.Date(string= 'Valido hasta') 
    categoria = fields.Char(string = 'Categoria') 
    
    es_oficial = fields.Boolean(string='Datos Oficiales Verificados', default=False, readonly=True, 
                                help="Si está marcado, este factor fue importado de una base de datos gubernamental y no se puede alterar.")
     