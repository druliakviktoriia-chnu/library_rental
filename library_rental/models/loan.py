from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError

LOAN_PERIOD_DAYS = 14
FINE_PER_DAY = 5.0


class LibraryLoan(models.Model):
    _name = 'library.loan'
    _description = 'Library Loan'

    copy_id = fields.Many2one(
        'library.copy', string='Copy', required=True, ondelete='restrict')
    member_id = fields.Many2one(
        'library.member', string='Member', required=True, ondelete='restrict')
    loan_date = fields.Date(default=fields.Date.context_today)
    due_date = fields.Date(
        compute='_compute_due_date', store=True, string='Due Date')
    return_date = fields.Date()
    state = fields.Selection(
        [('active', 'Active'), ('returned', 'Returned')],
        default='active', required=True)
    fine_amount = fields.Float(
        compute='_compute_fine_amount', store=True, string='Fine (UAH)')
    is_overdue = fields.Boolean(compute='_compute_is_overdue')

    book_id = fields.Many2one(related='copy_id.book_id', string='Book')
    book_author = fields.Char(related='copy_id.book_id.author', string='Author')
    book_isbn = fields.Char(related='copy_id.book_id.isbn', string='ISBN')

    @api.depends('loan_date')
    def _compute_due_date(self):
        for loan in self:
            if loan.loan_date:
                loan.due_date = loan.loan_date + timedelta(days=LOAN_PERIOD_DAYS)
            else:
                loan.due_date = False

    @api.depends('return_date', 'due_date')
    def _compute_fine_amount(self):
        for loan in self:
            if loan.return_date and loan.due_date and loan.return_date > loan.due_date:
                days = (loan.return_date - loan.due_date).days
                loan.fine_amount = days * FINE_PER_DAY
            else:
                loan.fine_amount = 0.0

    @api.depends('state', 'due_date')
    def _compute_is_overdue(self):
        today = fields.Date.context_today(self)
        for loan in self:
            loan.is_overdue = bool(
                loan.state == 'active' and loan.due_date and loan.due_date < today)

    @api.onchange('copy_id')
    def _onchange_copy_id(self):
        if not self.copy_id:
            return
        domain = [('copy_id', '=', self.copy_id.id), ('state', '=', 'active')]
        if self._origin:
            domain.append(('id', '!=', self._origin.id))
        if self.env['library.loan'].search_count(domain):
            return {'warning': {
                'title': 'Примірник вже виданий',
                'message': 'Цей примірник уже має активну видачу. '
                           'Збереження буде заблоковано.',
            }}

    @api.constrains('copy_id', 'state')
    def _check_single_active_loan(self):
        for loan in self:
            if loan.state != 'active':
                continue
            conflict = self.search_count([
                ('copy_id', '=', loan.copy_id.id),
                ('state', '=', 'active'),
                ('id', '!=', loan.id),
            ])
            if conflict:
                raise ValidationError(
                    'Примірник %s уже має активну видачу.'
                    % loan.copy_id.inventory_number)

    @api.constrains('loan_date', 'due_date')
    def _check_due_after_loan(self):
        for loan in self:
            if loan.loan_date and loan.due_date and loan.due_date <= loan.loan_date:
                raise ValidationError(
                    'Дата повернення за планом має бути пізніше дати видачі.')

    @api.constrains('loan_date', 'return_date')
    def _check_return_not_before_loan(self):
        for loan in self:
            if loan.loan_date and loan.return_date and loan.return_date < loan.loan_date:
                raise ValidationError(
                    'Фактична дата повернення не може бути раніше дати видачі.')