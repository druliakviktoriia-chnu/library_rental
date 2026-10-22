from odoo import fields, models


class LibraryLoan(models.Model):
    _name = 'library.loan'
    _description = 'Library Loan'

    copy_id = fields.Many2one(
        'library.copy', string='Copy', required=True, ondelete='restrict')
    member_id = fields.Many2one(
        'library.member', string='Member', required=True, ondelete='restrict')
    loan_date = fields.Date(default=fields.Date.context_today)
    due_date = fields.Date()
    return_date = fields.Date()
    state = fields.Selection(
        [('active', 'Active'), ('returned', 'Returned')],
        default='active', required=True)

    book_id = fields.Many2one(related='copy_id.book_id', string='Book')
    book_author = fields.Char(related='copy_id.book_id.author', string='Author')
    book_isbn = fields.Char(related='copy_id.book_id.isbn', string='ISBN')