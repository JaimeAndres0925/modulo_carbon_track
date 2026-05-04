from odoo import models, fields

class CarbonTrackActividad(models.Model):
    _name = 'carbon.track.actividad'
    _descripciption = 'Actividades generadoras de emisiones'
    
    nombre = fields.Char(string = 'Nombre de la actividad', required = True)
    description = fields.Text(string= 'Descripcion') 
    alcance_id = fields.Many2one('carbon.track.alcance', string='Alcance') 
    factor_emision_id = fields.Many2one('carbon.track.emision', string= 'Factor de Emisión') 
    unidad = fields.Char(string='Unidad de Medida') 
    activo = fields.Boolean(string='Activo', default=True) 
    