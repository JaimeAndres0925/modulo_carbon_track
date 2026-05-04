from odoo import models, fields

class CarbonTrackPeriodo(models.Model):
    _name = 'carbon.track.periodo'
    _description = 'Periodos de reporte'

    name = fields.Char(string='Nombre del Periodo', required=True) 
    fecha_inicio = fields.Date(string='Fecha Inicio') 
    fecha_fin = fields.Date(string='Fecha Fin') 
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('cerrado', 'Cerrado')
    ], string='Estado', default='borrador') 