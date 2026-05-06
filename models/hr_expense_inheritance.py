from odoo import models, fields, api

class HrExpense(models.Model):
    _inherit = 'hr.expense' # Heredamos el modelo de gastos nativo de Odoo

    # Añadimos campos de tu módulo al formulario de gastos
    carbon_actividad_id = fields.Many2one('carbon.track.actividad', string='Actividad de Carbono')
    es_gasto_contaminante = fields.Boolean(string='¿Genera Huella de Carbono?', default=False)

    def action_submit_expenses(self):
        """
        Esta función se ejecuta cuando el empleado envía el gasto a aprobar.
        Aquí crearemos el registro en tu módulo automáticamente.
        """
        res = super(HrExpense, self).action_submit_expenses()
        
        for expense in self:
            if expense.es_gasto_contaminante and expense.carbon_actividad_id:
                # Buscamos o creamos un periodo (esto es un ejemplo simple)
                periodo = self.env['carbon.track.periodo'].search([], limit=1) 
                
                # Creamos el registro en tu módulo de forma automática
                self.env['carbon.track.registro'].create({
                    'name': f"Gasto: {expense.name}",
                    'actividad_id': expense.carbon_actividad_id.id,
                    'cantidad': expense.quantity, # Usamos la cantidad del ticket
                    'periodo_id': periodo.id,
                    # El campo total_co2e se calculará solo gracias al @api.depends que ya programamos
                })
        return res