from odoo import fields, models


class LibraryCopy(models.Model):
    _name = 'library.copy'
    _description = 'Library Book Copy'
    _rec_name = 'inventory_number'

    book_id = fields.Many2one(
        'library.book', string='Book', required=True, ondelete='restrict')
    inventory_number = fields.Char(required=True)
    condition = fields.Selection(
        [('new', 'New'), ('good', 'Good'), ('damaged', 'Damaged')],
        default='good', required=True)