from odoo import models, fields, api
from odoo.exceptions import UserError 

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    es_gasto_contaminante = fields.Boolean(string='¿Genera Huella de Carbono?', default=False)
    actividad_id = fields.Many2one('carbon.track.actividad', string='Actividad Contaminante')
    
    # Campos para la monetización y cálculo del carbono al vuelo
    co2e_estimado = fields.Float(string='CO2e Estimado (kg)', compute='_compute_coste_ambiental', store=True)
    coste_ambiental = fields.Float(string='Coste Ambiental', compute='_compute_coste_ambiental', store=True)
    periodo_id = fields.Many2one('carbon.track.periodo', string='Periodo de Cálculo')
    
    @api.depends('quantity', 'actividad_id', 'es_gasto_contaminante')
    def _compute_coste_ambiental(self):
        # Tasa interna estándar: 50€ por Tonelada (0.05€ por kg)
        PRECIO_POR_KG = 0.05 
        
        for expense in self:
            if expense.es_gasto_contaminante and expense.actividad_id:
                # Odoo buscará el factor de emisión asociado a esta actividad
                factor = expense.actividad_id.factor_emision_id.valor or 0.0
                
                # Multiplicamos la cantidad del ticket por el factor
                expense.co2e_estimado = expense.quantity * factor
                
                # Multiplicamos los kilos resultantes por el precio del carbono
                expense.coste_ambiental = expense.co2e_estimado * PRECIO_POR_KG
            else:
                expense.co2e_estimado = 0.0
                expense.coste_ambiental = 0.0

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    # Campo que detecta si hay exceso de contaminación
    requiere_eco_aprobacion = fields.Boolean(
        string='Requiere Eco-Aprobación', 
        compute='_compute_eco_aprobacion'
    )

    @api.depends('expense_line_ids.co2e_estimado')
    def _compute_eco_aprobacion(self):
        for sheet in self:
            # Si algún gasto individual supera los 150 kg, se activa la alerta
            sheet.requiere_eco_aprobacion = any(
                exp.co2e_estimado > 150.0 for exp in sheet.expense_line_ids
            )

    # El nuevo botón que usará el Gestor de Sostenibilidad
    def action_eco_approve(self):
        # Le pasamos contexto a la función original para que sepa que tiene permiso
        return self.with_context(aprobacion_excepcional=True).action_approve_expense_sheets()

    # Sobreescribimos la aprobación original
    def action_approve_expense_sheets(self):
        # Si requiere eco-aprobación y NO estamos usando el botón especial, lanzamos error.
        for sheet in self:
            if sheet.requiere_eco_aprobacion and not self.env.context.get('aprobacion_excepcional'):
                raise UserError(
                    "¡Alerta Ecológica! Este informe supera el límite de emisiones "
                    "permitido (150 kg CO2e). Debe ser revisado y aprobado usando el "
                    "botón de 'Aprobación Excepcional (Eco)'."
                )

        # 2. Ejecutamos la aprobación normal de Odoo
        res = super(HrExpenseSheet, self).action_approve_expense_sheets()
        
        # 3. Lógica de crear el registro en el modulo
        meses = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 
                 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
        
        for sheet in self:
            for expense in sheet.expense_line_ids:
                if expense.es_gasto_contaminante and expense.actividad_id:
                    mes_nombre = meses.get(expense.date.month, 'Mes')
                    # Buscamos primero si hay uno abierto (estado='abierto')
                    periodo = self.env['carbon.track.periodo'].search([('estado', '=', 'abierto')], limit=1)

                    # Si no hay ninguno abierto, buscamos uno en borrador
                    if not periodo:
                        periodo = self.env['carbon.track.periodo'].search([('estado', '=', 'borrador')], limit=1)

                    # Solo si NO hay absolutamente nada, creamos uno
                    if not periodo:
                        periodo = self.env['carbon.track.periodo'].create({
                        'name': f'Periodo Sistema - {fields.Date.today().year}',
                        'fecha_inicio': fields.Date.today(),
                        'fecha_fin': fields.Date.today(),
                        'estado': 'abierto'
                        })
                    
                    
                    self.env['carbon.track.registro'].create({
                        'concepto': f'Gasto Auto: {expense.name}',
                        'fecha': expense.date,
                        'actividad_id': expense.actividad_id.id,
                        'periodo_id': periodo.id,
                        'cantidad': expense.quantity,
                    })
        return res