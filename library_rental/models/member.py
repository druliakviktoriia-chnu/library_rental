from odoo import fields, models


class LibraryMember(models.Model):
    _name = 'library.member'
    _description = 'Library Member'

    name = fields.Char(required=True)
    membership_number = fields.Char(required=True, copy=False)
    phone = fields.Char()
    email = fields.Char()
    user_id = fields.Many2one(
        'res.users', string='Odoo User', ondelete='set null')

    _membership_number_uniq = models.Constraint(
        'UNIQUE(membership_number)',
        'Membership number must be unique.',
    )
    _user_id_uniq = models.Constraint(
        'UNIQUE(user_id)',
        'One Odoo user can be linked to only one library member.',
    )