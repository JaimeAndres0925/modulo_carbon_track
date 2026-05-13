from odoo import models, fields, api

class CarbonTrackRegistro(models.Model):
    _name = 'carbon.track.registro'
    _description = 'Registros de consumo (Datos de entrada)'
    _order = 'fecha desc'
    
    name = fields.Char(string='Referencia', required=True, copy=False, readonly=True, default='Nuevo')
    concepto = fields.Char(string='Concepto / Descripción', help="Ej: Vuelo a Madrid, Factura de la luz de Mayo...")
    
    #Relaciones del modelo de datos
    periodo_id = fields.Many2one('carbon.track.periodo', string= 'Periodo', required=True, ondelete='cascade') 
    actividad_id = fields.Many2one('carbon.track.actividad', string='Actividad', required=True)
    cups = fields.Char(string='CUPS', help="Código Universal del Punto de Suministro") 
    
    #Datos de entrada
    fecha = fields.Date(string='Fecha', default=fields.Date.context_today) 
    cantidad = fields.Float(string='Magnitud de Consumo', required=True) 
    unidad = fields.Char(string='Unidad', related='actividad_id.unidad',readonly=True) 
    notas =fields.Text(string='Notas')
    
    cae_ids = fields.One2many('carbon.track.cae', 'huella_id', string='Certificados CAE') 
    
    # Campo calculado para el resultado
    valor_co2e = fields.Float(string='Total c02E (kg)', compute='_compute_co2e', store=True) 
    
    @api.depends('cantidad', 'actividad_id.factor_emision_id.valor')
    def _compute_co2e(self):
        for record in self:
            factor = record.actividad_id.factor_emision_id.valor or 0.0
            record.valor_co2e = record.cantidad * factor
            
    # 1. Creamos el campo de selección para el impacto
    nivel_impacto = fields.Selection([
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto')
    ], string='Impacto', compute='_compute_nivel_impacto', store=True)

    # 2. Creamos la función que decide el color según la cantidad
    @api.depends('valor_co2e')
    def _compute_nivel_impacto(self):
        for record in self:
            if record.valor_co2e < 10000.0:
                record.nivel_impacto = 'bajo'
            elif record.valor_co2e <= 50000.0:
                record.nivel_impacto = 'medio'
            else:
                record.nivel_impacto = 'alto'
                
    # Metodo para usar el motor de secuencias de Odoo
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                # Pedimos a Odoo el siguiente número de nuestra secuencia
                vals['name'] = self.env['ir.sequence'].next_by_code('carbon.track.registro.secuencia') or 'Nuevo'
        return super().create(vals_list)

    
    
    
    
    