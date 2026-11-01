from odoo import fields, models

CONDITIONS = [('new', 'New'), ('good', 'Good'), ('damaged', 'Damaged')]


class LibraryCopy(models.Model):
    _name = 'library.copy'
    _description = 'Library Book Copy'
    _rec_name = 'inventory_number'

    book_id = fields.Many2one(
        'library.book', string='Book', required=True, ondelete='restrict')
    inventory_number = fields.Char(required=True)
    condition = fields.Selection(CONDITIONS, default='good', required=True)