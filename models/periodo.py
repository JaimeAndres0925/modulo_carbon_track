from odoo import models, fields

class CarbonTrackPeriodo(models.Model):
    _name = 'carbon.track.periodo'
    _description = 'Periodos de reporte'

    name = fields.Char(string='Nombre del Periodo', required=True) 
    fecha_inicio = fields.Date(string='Fecha Inicio') 
    fecha_fin = fields.Date(string='Fecha Fin') 
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('cerrado', 'Cerrado')
    ], string='Estado', default='borrador')
    
    # 1. El límite que la empresa no debe superar (lo rellenará el usuario a mano)
    presupuesto_co2e = fields.Float(string='Presupuesto Máximo (kg CO2e)', default=5000.0)
    
    # 2. Lo que llevamos gastado (se calcula solo)
    total_co2e_consumido = fields.Float(compute='_compute_presupuesto', string='Total Consumido')
    
    # 3. El porcentaje para la barra de progreso (se calcula solo)
    porcentaje_consumido = fields.Float(compute='_compute_presupuesto', string='% Consumido')

    def _compute_presupuesto(self):
        for periodo in self:
            # Buscamos todos los registros de consumo que pertenezcan a este periodo
            registros = self.env['carbon.track.registro'].search([('periodo_id', '=', periodo.id)])
            
            # Sumamos todo el CO2e
            total = sum(registros.mapped('valor_co2e'))
            periodo.total_co2e_consumido = total
            
            # Calculamos el porcentaje (con cuidado de no dividir por cero)
            if periodo.presupuesto_co2e > 0:
                periodo.porcentaje_consumido = (total / periodo.presupuesto_co2e) * 100
            else:
                periodo.porcentaje_consumido = 0.0 