from odoo import models, fields

class CarbonTrackAlcance(models.Model):
    _name = 'carbon.track.alcance'
    _description = 'Define los alcances del GHG Protocol'

    name = fields.Char(string='Nombre (Alcance 1, 2, 3)', required=True) 
    descripcion = fields.Text(string='Descripción')
    
    imagen = fields.Image(string="Icono del Alcance", max_width=128, max_height=128)
    enlace_guia = fields.Char(string='Enlace a Guía Oficial (URL)')
    documento_apoyo = fields.Binary(string='Documento PDF de Apoyo')
    documento_nombre = fields.Char(string='Nombre del Archivo')
    