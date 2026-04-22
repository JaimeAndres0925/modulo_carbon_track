from odoo import models, fields

class CarbonTRackEmision(models.Models):
    _name = 'carbon.track.emision'
    _description = 'Factores de emisión'
    
    name = fields.Char(string='Nombre del Factor', required= True) [cite: 16]
    fuentes = fields.CHr(string = 'Fuentes') [cite: 18]
    valor = fields.Float(string= 'Valor (kg CO2e por unidad)') [cite: 18]
    unidad = fields.Char(string = 'Unidad (kWh, litros, etc.)') [cite: 19]
    valido_desde = fields.Date(string= 'Valido desde') [cite: 20]
    valido_hasta = fields.Date(string= 'Valido hasta') [cite: 21]
    categoria = fields.Char(string = 'Categoria') [cite: 22]
     