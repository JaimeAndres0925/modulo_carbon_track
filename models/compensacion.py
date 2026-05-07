from odoo import models, fields

class CarbonTrackCompensacion(models.Model):
    _name = 'carbon.track.compensacion'
    _description = 'Proyectos de Compensación de Carbono'
    _order = 'fecha desc'

    name = fields.Char(string='Nombre del Proyecto', required=True, placeholder="Ej. Plantación 50 Pinos")
    fecha = fields.Date(string='Fecha', default=fields.Date.context_today)
    periodo_id = fields.Many2one('carbon.track.periodo', string='Periodo', required=True)
    
    tipo = fields.Selection([
        ('arboles', 'Plantación de Árboles'),
        ('bonos', 'Compra de Bonos de Carbono (VERs)'),
        ('energia', 'Certificados de Energía Renovable (GOs)')
    ], string='Tipo de Compensación', required=True)
    
    co2e_compensado = fields.Float(string='CO2e Compensado (kg)', required=True)
    notas = fields.Text(string='Notas o URL del Certificado')