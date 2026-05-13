# models/carbon_track_cae.py

from odoo import models, fields, api
import random

class CarbonTrackCae(models.Model):
    _name = 'carbon.track.cae'
    _description = 'Solicitud de Certificado CAE'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Referencia CAE', required=True,
        copy=False, readonly=True, default='Nuevo'
    )

    # Relación con el registro de huella principal
    huella_id = fields.Many2one(
        'carbon.track.registro',
        string='Registro de Huella',
        required=True
    )

    # Si quieres sacar el CUPS desde el consumo vinculado al registro,
    # hazlo con related (ajusta la ruta al campo real de tu modelo):
    # cups = fields.Char(related='huella_id.consumo_id.cups', string='CUPS', store=True)
    
    # O simplemente déjalo como campo manual:
    cups = fields.Char(
        string='CUPS',
        help="Código Universal del Punto de Suministro",
        required=True
    )

    ahorro_kwh = fields.Float(string='Ahorro Anual (kWh)', required=True)
    fecha_solicitud = fields.Date(string='Fecha de Solicitud', default=fields.Date.context_today)

    estado = fields.Selection([
        ('draft', 'Borrador'),
        ('sent', 'Enviado a SICAES'),
        ('approved', 'Validado por Ministerio'),
        ('rejected', 'Rechazado'),
    ], string='Estado', default='draft', tracking=True)

    cae_external_id = fields.Char(string='ID Oficial SICAES', readonly=True)
    api_response_log = fields.Text(string='Log de la API', readonly=True)
    
    def action_marcar_aprobado(self):
        for record in self:
                record.write({
                'estado': 'approved',
                'api_response_log': (
                    record.api_response_log or ''
                ) + f"\n[SIMULACIÓN] Certificado {record.cae_external_id} validado por el Ministerio."
            })

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code('carbon.track.cae') or 'CAE/NEW'
        return super().create(vals)

    def action_enviar_api(self):
        """Simulación de conexión con SICAES para el TFG"""
        for record in self:
            id_simulado = f"SICAES-{random.randint(1000, 9999)}"
            record.write({
                'estado': 'sent',
                'cae_external_id': id_simulado,
                'api_response_log': (
                    f"[SIMULACIÓN TFG] Conexión exitosa con SICAES.\n"
                    f"Certificado registrado con ID: {id_simulado}\n"
                    f"CUPS: {record.cups} | Ahorro: {record.ahorro_kwh} kWh"
                ),
            })
    