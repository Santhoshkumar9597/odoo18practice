from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    cancel_days=fields.Integer(string='Cancel Days',config_parameter='s_gym_cancel_days')