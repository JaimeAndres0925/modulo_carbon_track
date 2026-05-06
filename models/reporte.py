from odoo import models, fields, api

class CarbonTrackReporte(models.Model):
    _name = 'carbon.track.reporte'
    _description = 'Informes agregados por periodo' 
    
    periodo_id = fields.Many2one('carbon.track.periodo', string='Periodo', required=True) 
    fecha_de_generacion = fields.Datetime(string='Fecha de Generación', default=fields.Datetime.now)
    name = fields.Char(string='Nombre del Informe', related='periodo_id.name', store=True, readonly=True) 
    
    total_alcance1 = fields.Float(string='Total Alcance 1', compute = '_compute_totales', store=True) 
    total_alcance2 = fields.Float(string='Total Alcance 2', compute = '_compute_totales', store=True) 
    total_alcance3 = fields.Float(string='Total Alcance 3', compute = '_compute_totales', store=True) 

    @api.depends('periodo_id')
    def _compute_totales(self):
        """
        Suma los cáculos realizados en el periodo seleccionado por cada alcance[cite:82, 83]
        """
        for report in self:
            registros = self.env['carbon.track.registro'].search([('periodo_id', '=', report.periodo_id.id)])
            report.total_alcance1 = sum(r.valor_co2e for r in registros if r.actividad_id.alcance_id.name == 'Alcance 1')
            report.total_alcance2 = sum(r.valor_co2e for r in registros if r.actividad_id.alcance_id.name == 'Alcance 2')
            report.total_alcance3 = sum(r.valor_co2e for r in registros if r.actividad_id.alcance_id.name == 'Alcance 3')        