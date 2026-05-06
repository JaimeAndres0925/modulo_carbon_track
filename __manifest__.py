{
    'name': 'Carbon Track',
    'version': '1.0',
    'summary': 'Gestión de huella de carbono y emisiones CO2e',
    'category': 'Sustainability', 
    'author': 'Jaime Andrés Venegas Cárdenas', 
    'depends': ['base', 'mail', 'hr_expense'], # Asegúrate de poner el nombre de tu carpeta
    'data': [
        'security/ir.model.access.csv',
        'views/carbon_track_menus.xml',
        'views/hr_expense_views.xml',
        'report/carbon_track_report_template.xml',
        'report/carbon_track_report_action.xml',
        
    ],
    'installable': True,
    'application': True,
}