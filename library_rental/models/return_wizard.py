from odoo import fields, models
from odoo.exceptions import UserError

from .copy import CONDITIONS


class LibraryReturnWizard(models.TransientModel):
    _name = 'library.return.wizard'
    _description = 'Return Book Wizard'

    loan_id = fields.Many2one('library.loan', required=True)
    condition_on_return = fields.Selection(CONDITIONS, required=True)
    notes = fields.Text()

    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if ('loan_id' in fields_list and not res.get('loan_id')
                and self.env.context.get('active_model') == 'library.loan'):
            res['loan_id'] = self.env.context.get('active_id')
        return res

    def action_confirm(self):
        self.ensure_one()
        if self.loan_id.state != 'active':
            raise UserError('Ця видача вже закрита.')
        self.loan_id.write({
            'state': 'returned',
            'return_date': fields.Date.today(),
        })
        self.loan_id.copy_id.condition = self.condition_on_return
        return {'type': 'ir.actions.act_window_close'}