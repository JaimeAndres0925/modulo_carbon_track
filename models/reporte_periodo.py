from odoo import models, fields, api

class CarbonTrackReporte(models.Model):
    _name = 'carbon.track.reporte'
    _description = 'Informes agregados por periodo' 
    
    periodo_id = fields.Many2one('carbon.track.periodo', string='Periodo', required=True) 
    fecha_de_generacion = fields.Datetime(string='Fecha de Generación', default=fields.Datetime.now)
    name = fields.Char(string='Nombre del Informe', related='periodo_id.name', store=True, readonly=True) 
    
    total_alcance1 = fields.Float(string='Total Alcance 1', compute='_compute_totales') 
    total_alcance2 = fields.Float(string='Total Alcance 2', compute='_compute_totales') 
    total_alcance3 = fields.Float(string='Total Alcance 3', compute='_compute_totales') 

    @api.depends('periodo_id', 'periodo_id.registro_ids', 'periodo_id.registro_ids.valor_co2e')
    def _compute_totales(self):
        for report in self:
            alcance1 = 0.0
            alcance2 = 0.0
            alcance3 = 0.0
            
            if report.periodo_id and report.periodo_id.registro_ids:
                for r in report.periodo_id.registro_ids:
                    
                    nombre_alcance = (r.actividad_id.alcance_id.name or '').lower()
                    valor = r.valor_co2e 
                    
                    if '1' in nombre_alcance or 'directa' in nombre_alcance:
                        alcance1 += valor
                    elif '2' in nombre_alcance or 'energ' in nombre_alcance:
                        alcance2 += valor
                    elif '3' in nombre_alcance or 'indirecta' in nombre_alcance:
                        alcance3 += valor
            
            report.total_alcance1 = alcance1
            report.total_alcance2 = alcance2
            report.total_alcance3 = alcance3