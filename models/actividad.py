from odoo import models, fields, api

class CarbonTrackActividad(models.Model):
    _name = 'carbon.track.actividad'
    _descripciption = 'Actividades generadoras de emisiones'

    name = fields.Char(string = 'Nombre de la actividad', required = True)
    description = fields.Text(string= 'Descripcion') 
    alcance_id = fields.Many2one('carbon.track.alcance', string='Alcance') 
    factor_emision_id = fields.Many2one('carbon.track.emision', string= 'Factor de Emisión') 
    unidad = fields.Char(string='Unidad de Medida') 
    activo = fields.Boolean(string='Activo', default=True) 
    codigo = fields.Char(string='Código', required=True, copy=False, readonly=True, default='Nuevo')

    # Campos calculados
    registro_count = fields.Integer(compute='_compute_registro_stats', string='Nº Registros')
    total_co2e_acumulado = fields.Float(compute='_compute_registro_stats', string='CO2e Total')

    def _compute_registro_stats(self):
        for act in self:
            # Buscamos todos los registros asociados a esta actividad
            registros = self.env['carbon.track.registro'].search([('actividad_id', '=', act.id)])
            act.registro_count = len(registros)
            act.total_co2e_acumulado = sum(registros.mapped('valor_co2e'))

    # Función que se ejecuta al pulsar el botón
    def action_view_registros(self):
        self.ensure_one()
        return {
            'name': 'Registros de Consumo',
            'type': 'ir.actions.act_window',
            'res_model': 'carbon.track.registro',
            'view_mode': 'list,form',
            'domain': [('actividad_id', '=', self.id)], # Filtra para ver solo los de esta actividad
            'context': {'default_actividad_id': self.id}, # Si crea uno nuevo, ya le pone esta actividad
        }
        
    # Función para obtener la unidad de medida del factor de emisión  
    @api.onchange('factor_emision_id')
    def _onchange_factor_id(self):
    
        if self.factor_emision_id:
            self.unidad = self.factor_emision_id.unidad
        else:
            self.unidad = False
            
    @api.model
    def create(self, vals):
        if vals.get('codigo', 'Nuevo') == 'Nuevo':
            vals['codigo'] = self.env['ir.sequence'].next_by_code('carbon.track.actividad') or 'Nuevo'
        return super(CarbonTrackActividad, self).create(vals)
    