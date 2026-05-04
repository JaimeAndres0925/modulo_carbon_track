{
    'name': 'Carbon Track',
    'version': '1.0',
    'summary': 'Gestión de huella de carbono y emisiones CO2e',
    'category': 'Sustainability', # Categoría alineada con tu Plan de Empresa [cite: 120]
    'author': 'Jaime Andrés Venegas Cárdenas', # Según tu documento [cite: 5]
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/carbon_track_menus.xml',
        'report/carbon_track_report_template.xml',
        'report/carbon_track_report_action.xml',
    ],
    'installable': True,
    'application': True,
}