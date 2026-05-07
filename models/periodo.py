from odoo import models, fields, api

class CarbonTrackPeriodo(models.Model):
    _name = 'carbon.track.periodo'
    _description = 'Periodos de Seguimiento'
    

    name = fields.Char(string='Nombre', required=True)
    presupuesto_co2e = fields.Float(string='Presupuesto Máximo (kg CO2e)', default=5000.0)
    
    # Relación Inversa: Para ver las compensaciones desde el periodo
    compensacion_ids = fields.One2many('carbon.track.compensacion', 'periodo_id', string='Proyectos de Compensación')

    # Campos Calculados
    total_co2e_consumido = fields.Float(compute='_compute_balances', string='Total Consumido (kg)', store=True)
    porcentaje_consumido = fields.Float(compute='_compute_balances', string='% Consumido', store=True)
    
    # NUEVOS CAMPOS: La parte de compensación
    total_co2e_compensado = fields.Float(compute='_compute_balances', string='Total Compensado (kg)', store=True)
    huella_neta = fields.Float(compute='_compute_balances', string='Huella de Carbono Neta (kg)', store=True)
    es_net_zero = fields.Boolean(compute='_compute_balances', string='¿Net Zero Alcanzado?', store=True)

    @api.depends('compensacion_ids.co2e_compensado') # Odoo recalcula si añadimos compensaciones
    def _compute_balances(self):
        for periodo in self:
            # 1. Calculamos lo malo (Consumo)
            registros = self.env['carbon.track.registro'].search([('periodo_id', '=', periodo.id)])
            total_consumo = sum(registros.mapped('valor_co2e'))
            periodo.total_co2e_consumido = total_consumo
            
            # 2. Calculamos lo bueno (Compensación)
            total_compensado = sum(periodo.compensacion_ids.mapped('co2e_compensado'))
            periodo.total_co2e_compensado = total_compensado
            
            # 3. La Matemática de la Sostenibilidad
            periodo.huella_neta = total_consumo - total_compensado
            
            # Si hemos compensado todo o más de lo que consumimos, ¡somos Net Zero!
            periodo.es_net_zero = periodo.huella_neta <= 0
            
            # 4. El progreso del presupuesto
            if periodo.presupuesto_co2e > 0:
                periodo.porcentaje_consumido = (total_consumo / periodo.presupuesto_co2e) * 100
            else:
                periodo.porcentaje_consumido = 0.0
    
    def action_send_email(self):
        self.ensure_one() # Nos aseguramos de que solo se ejecute en un periodo a la vez
        
        # Buscamos la plantilla de correo (la crearemos en el XML en el siguiente paso)
        template = self.env.ref('modulo_carbon_track.email_template_periodo', raise_if_not_found=False)
        
        # Preparamos el contexto para abrir la ventana de redacción de Odoo
        ctx = {
            'default_model': 'carbon.track.periodo',
            'default_res_ids': self.ids,
            'default_template_id': template.id if template else False,
            'default_composition_mode': 'comment',
        }
        
        # Le decimos a Odoo que abra la ventana emergente de envío de correo
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }