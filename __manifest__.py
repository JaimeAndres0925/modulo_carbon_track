{
    'name': 'Carbon Track',
    'version': '1.0.0',
    'summary': 'Gestión de huella de carbono y emisiones CO2e',
    'category': 'Sostenibilidad/Recursos Humanos', 
    'description': """
        Módulo corporativo para la gestión integral de la Huella de Carbono.
        - Sincronización automática con la API de Climatiq.
        - Gestión de Alcances 1, 2 y 3.
        - Autocálculo de factores de emisión.
        - Integración automática con el módulo de Gastos de empleados
    """,
    'website': 'https://github.com/JaimeAndres0925/modulo_carbon_track',
    'author': 'Jaime Andrés Venegas Cárdenas', 
    'depends': ['base', 'mail', 'hr_expense', 'account'], 
    'data': [
        'security/carbon_track_security.xml',
        'security/ir.model.access.csv',
        'views/configuracion_views.xml',   
        'views/operaciones_views.xml',
        'views/informes_views.xml',
        'views/hr_expense_views.xml',
        'views/cae.xml',
        'views/account_views.xml',
        'data/secuencias.xml',
        'data/alcances_data.xml',
        'data/crons.xml',
        'report/carbon_track_report_template.xml',
        'report/carbon_track_report_action.xml',
    ],
    
    'assets': {
        'web.assets_backend': [
            'modulo_carbon_track/static/src/scss/colors.scss',
        ],
    },
    
    'installable': True,
    'application': True,
}