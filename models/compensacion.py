from odoo import models, fields, api

class CarbonTrackCompensacion(models.Model):
    _name = 'carbon.track.compensacion'
    _description = 'Proyectos de Compensación de Carbono'
    _order = 'fecha desc'
    
    codigo = fields.Char(string='Referencia', required=True, copy=False, readonly=True, default='Nuevo')
    name = fields.Char(string='Nombre del Proyecto', required=True, placeholder="Ej. Plantación 50 Pinos")
    fecha = fields.Date(string='Fecha', default=fields.Date.context_today)
    periodo_id = fields.Many2one('carbon.track.periodo', string='Periodo', required=True)
    
    tipo = fields.Selection([
        ('arboles', 'Plantación de Árboles'),
        ('bonos', 'Compra de Bonos de Carbono'),
        ('energia', 'Certificados de Energía Renovable'),
        ('bosque', 'Conservación de Bosques (REDD+)'),
        ('metano', 'Captura de Metano (Vertederos/Granjas)'),
        ('azul', 'Carbono Azul (Manglares y Ecosistemas Marinos)'),
        ('agricultura', 'Agricultura Regenerativa'),
    ], string='Tipo de Compensación', required=True)
    
    co2e_compensado = fields.Float(string='CO2e Compensado (kg)', required=True)
    notas = fields.Text(string='Notas o URL del Certificado')
    
    @api.model
    def create(self, vals):
        if vals.get('codigo', 'Nuevo') == 'Nuevo':
            vals['codigo'] = self.env['ir.sequence'].next_by_code('carbon.track.compensacion') or 'Nuevo'
        return super(CarbonTrackCompensacion, self).create(vals)