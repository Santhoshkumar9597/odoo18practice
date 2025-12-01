from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import date


class CancelAppointmentWizard(models.TransientModel):
    _name = 'cancel.appointment.wizard'
    _description = "Cancel Appointment Wizard"

    appointment_id = fields.Many2one('appointment.fitness', string='Appointment')
    reason = fields.Text(string='Reason')

    def default_get(self, fields):
        print("Default get executed")
        return super(CancelAppointmentWizard, self).default_get(fields)

    def action_cancel(self):
        cancel_day = self.env['ir.config_parameter'].sudo().get_param('s_gym_cancel_days')
        cancel_day = int(cancel_day or 0)

        allowed_date = self.appointment_id.booking_date - relativedelta(days=cancel_day)
        if allowed_date < date.today():
            raise ValidationError(_("Sorry, cancellation is not allowed for this booking!"))
        query="""select id,trainer_id from appointment_fitness where id= %s"""% self.appointment_id.id
        self._cr.execute(query)
        trainers=self.env.cr.dictfetchall()
        print("trainers----->", trainers)
        # self.appointment_id.state = 'cancel'
        # return {
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'cancel.appointment.wizard',
        #     'view_mode': 'form',
        #     'res_id': self.id,
        #     'target': 'new',
        # }

