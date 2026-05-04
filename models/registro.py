from odoo import models, fields, api

class CarbonTrackRegistro(models.Model):
    _name = 'carbon.track.registro'
    _description = 'Registros de consumo (Datos de entrada)'
    
    #Relaciones del modelo de datos
    periodo_id = fields.Many2one('carbon.track.periodo', string= 'Periodo', required=True) 
    actividad_id = fields.Many2one('carbon.track.actividad', string='Actividad', required=True) 
    
    #Datos de entrada
    fecha = fields.Date(string='Fecha', default=fields.Date.context_today) 
    cantidad = fields.Float(string='Cantidad', required=True) 
    unidad = fields.Char(string='Unidad', related='actividad_id.unidad',readonly=True) 
    notas =fields.Text(string='Notas') 
    
    # Campo calculado para el resultado
    valor_co2e = fields.Float(string='Total c02E (kg)', compute='_compute_co2e', store=True) 
    
    @api.depends('cantidad', 'actividad_id.factor_emision_id.valor')
    def _compute_co2e(self):
        for record in self:
            # Cálculo: Cantidad * Valor del Factor de Emisión [cite: 67, 77]
            factor = record.actividad_id.factor_emision_id.valor or 0.0
            record.valor_co2e = record.cantidad * factor

    
    
    
    
    