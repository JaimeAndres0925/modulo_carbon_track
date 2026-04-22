from odoo import models, fields, api

class CarbonTrackRegistro(models.Model):
    _name = 'carbon.track.registro'
    _description = 'Registros de consumo (Datos de entrada)'
    
    actividad_id = fields.Many2one('carbon.track.actividad', string='Actividad', required=True) [cite: 26]
    fecha = fields.Date(string='Fecha', default=fields.Fate.context_today) [cite: 27]
    cantidad = fields.Float(string='Cantidad', required=True) [cite: 28]
    unidad = fields.Char(string='Unidad', related='actividad_id_unidad',readonly=True) [cite: 29]
    periodo_id = fields.Many2one(carbon.track.periodo, string= 'Periodo', required=True) [cite: 30]
    notas =fields.Text(string='Notas') [cite: 30]
    
    valor_co2e = fields.Float(string='Total c02E (kg)', compute='_compute-co2e', store=True) [cite: 35]
    
    @api.depends('cantidad', 'actividad_id.factor_emision_id.valor')
    def _compute_co2e(self):
        for record in self:
            # Cálculo: Cantidad * Valor del Factor de Emisión [cite: 67, 77]
            factor = record.actividad_id.factor_emision_id.valor or 0.0
            record.valor_co2e = record.cantidad * factor

    
    
    
    
    