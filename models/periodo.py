from odoo import models, fields

class CarbonTrackPeriodo(models.Model):
    _name = 'carbon.track.periodo'
    _description = 'Periodos de reporte'

    name = fields.Char(string='Nombre del Periodo', required=True) [cite: 45]
    fecha_inicio = fields.Date(string='Fecha Inicio') [cite: 46]
    fecha_fin = fields.Date(string='Fecha Fin') [cite: 47]
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('cerrado', 'Cerrado')
    ], string='Estado', default='borrador') [cite: 48]