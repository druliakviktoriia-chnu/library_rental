{
    'name': 'Library Rental',
    'version': '19.0.1.0.0',
    'summary': 'Book rental management for a library',
    'category': 'Services',
    'author': 'Victoria',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/book_views.xml',
        'views/copy_views.xml',
        'views/member_views.xml',
        'views/loan_views.xml',
        'data/library_data.xml',
    ],
    'installable': True,
    'application': True,
}