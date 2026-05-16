from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import random

class SICAESApiClient:
    def __init__(self):
        self.url_base = "https://api.simulada.ministerio.es/v1" 

    def enviar_cae(self, data):
        # Simulación de respuesta exitosa
        return {
            "status": "success", 
            "id_cae": f"SICAES-{random.randint(1000, 9999)}"
        }

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

    cups = fields.Char(
        string='CUPS',
        related='huella_id.cups',
        readonly=True,            
        store=True,               
        help="Código Universal del Punto de Suministro (traído del registro de consumo)"
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
                'api_response_log': (record.api_response_log or '') + \
                    f"\n[SIMULACIÓN] Certificado {record.cae_external_id} validado por el Ministerio."
            })

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('carbon.track.cae') or 'CAE/NEW'
        return super(CarbonTrackCae, self).create(vals_list)

    def action_enviar_api(self):
        client = SICAESApiClient()
        for record in self:
            data = {
                'cups': record.cups,
                'kwh': record.ahorro_kwh,
                'ref': record.name
            }
            response = client.enviar_cae(data) 
        
            if response.get('status') == 'success':
                record.write({
                    'estado': 'sent',
                    'cae_external_id': response['id_cae'],
                    'api_response_log': f"[CONEXIÓN API EXITOSA]\nID: {response['id_cae']}\nCUPS enviado: {record.cups}"
                })

    @api.constrains('cups')
    def _check_cups_format(self):
        for record in self:
            if record.cups and len(record.cups) not in [20, 22]:
                raise ValidationError("El CUPS debe tener 20 o 22 caracteres (Formato Español).")
    
    def action_marcar_aprobado(self):
        for reg in self:
            if reg.estado == 'approved':
                continue # Si ya está aprobado, no hacemos nada
            
            # 1. Cambiamos el estado a aprobado (como tú lo tienes)
            reg.estado = 'approved'
            
            # 2. CREACIÓN AUTOMÁTICA DEL INFORME
            self.env['carbon.track.reporte.cae'].with_context(desde_cae=True).create({
                'name': f"Informe Oficial - {reg.name}",
                'cae_id': reg.id,
                'validador_id': self.env.user.id,
                'consumo_ahorrado': reg.ahorro_kwh,
                'co2_evitado': 0.0, 
            })