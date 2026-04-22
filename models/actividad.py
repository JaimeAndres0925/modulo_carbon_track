from odoo import models, fields

class CarbonTrackActividad(models.Model):
    _name = 'carbon.track.actividad'
    _descripciption = 'Actividades generadoras de emisiones'
    
    nombre = fields.char(string = 'Nombre de la actividad', required = True)
    description = fields.Text(string= 'Descripcion') [cite: 9]
    alcance_id = fields.Many2one('carbon.track.alcance', string='Alcance') [cite: 10]
    factor_emision_id = fields.Many2one('carbon.track.emision', string= 'Factor de Emisión') [cite: 11]
    unidad = fields.Char(string='Unidad de Medida') [cite: 11]
    activo = fields.Boolean(string='Activo', default=True) [cite: 12]
    