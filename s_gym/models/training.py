from odoo import fields, models,api,_

class GymTraining(models.Model):
    _name="gym.training"
    _description="Gym Training"

    training_name = fields.Char(string='Training Name')
    trainer_id=fields.Many2one('gym.fitness',string='Trainer')
    reference_record = fields.Selection(selection=[('gym.fitness', 'Trainers'), ('appointment.fitness', 'Appointment')],
                                        string="Record")


    @api.model
    def name_create(self, name):
        return self.create({'training_name': name}).name_get()[0]


