from odoo import models, fields

class CarbonTrackAlcance(models.Model):
    _name = 'carbon.track.alcance'
    _description = 'Define los alcances del GHG Protocol'

    name = fields.Char(string='Nombre (Alcance 1, 2, 3)', required=True) [cite: 41]
    descripcion = fields.Text(string='Descripción') [cite: 42]