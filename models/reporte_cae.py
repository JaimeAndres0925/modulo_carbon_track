from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CarbonTrackReporteCae(models.Model):
    _name = 'carbon.track.reporte.cae'
    _description = 'Informe Oficial de Validación CAE'
    _order = 'fecha_generacion desc'

    name = fields.Char(string='Nombre del Informe', readonly=True)
    cae_id = fields.Many2one('carbon.track.cae', string='Certificado Origen', readonly=True, ondelete='cascade')
    fecha_generacion = fields.Datetime(string='Fecha de Generación', default=fields.Datetime.now, readonly=True)
    validador_id = fields.Many2one('res.users', string='Validado por', readonly=True)
    
    # Campos espejo para que el informe quede congelado (aunque el CAE cambie luego)
    consumo_ahorrado = fields.Float(string='Ahorro (kWh)', readonly=True)
    co2_evitado = fields.Float(string='CO2 Evitado (kg)', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        # Bloqueo global: si la petición no viene del botón, bloqueamos todo el lote
        if not self.env.context.get('desde_cae'):
            raise UserError(_("Los informes solo pueden ser generados automáticamente al validar un Certificado CAE."))
        return super(CarbonTrackReporteCae, self).create(vals_list)

    def action_imprimir_pdf(self):
        # Aquí llamaríamos a la acción de impresión que definimos antes
        return self.env.ref('modulo_carbon_track.action_report_cae_solicitud').report_action(self.cae_id)