from odoo import models, fields
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_create_cae(self):
        self.ensure_one()
        
        periodo = self.env['carbon.track.periodo'].search([
        ('fecha_inicio', '<=', self.invoice_date),
        ('fecha_fin', '>=', self.invoice_date)
        ], limit=1)
        
        if not periodo:
            raise ValidationError("Antes de generar un CAE, debes crear al menos un Periodo en Carbon Track.")

        registro_huella = self.env['carbon.track.registro'].create({
            'concepto': f"Consumo de Factura {self.name}",
            'fecha': self.invoice_date or fields.Date.today(),
            'cantidad': self.amount_untaxed,
            'periodo_id': periodo.id,
            'actividad_id': self.env['carbon.track.actividad'].search([], limit=1).id,
        })

        cae_solicitud = self.env['carbon.track.cae'].create({
            'huella_id': registro_huella.id,
            'cups': 'ES002100000123456789WA', 
            'ahorro_kwh': registro_huella.cantidad * 0.15,
        })

        return {
            'name': 'Solicitud CAE Generada',
            'type': 'ir.actions.act_window',
            'res_model': 'carbon.track.cae',
            'view_mode': 'form',
            'res_id': cae_solicitud.id,
            'target': 'current',
        }