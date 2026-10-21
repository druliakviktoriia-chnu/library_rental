from odoo import fields, models


class LibraryMember(models.Model):
    _name = 'library.member'
    _description = 'Library Member'

    name = fields.Char(required=True)
    membership_number = fields.Char(required=True, copy=False)
    phone = fields.Char()
    email = fields.Char()

    _membership_number_uniq = models.Constraint(
        'UNIQUE(membership_number)',
        'Membership number must be unique.',
    )