from flask.ext.wtf import Form
from wtforms import widgets
from wtforms import StringField, BooleanField, RadioField, SelectField,SelectMultipleField
from wtforms.validators import DataRequired

class SurveyForm(Form):

    use_length_choices = [
    ('less_than_6_months','0 - 6 months'),
    ('6_to_12_months','6 - 12 months'),
    ('1_to_2_years','1 - 2 years'),
    ('2_plus_years','2+ years')
    ]

    length_of_use = RadioField('length_of_use',choices=use_length_choices)



    use_frequency_choices = [
    ('daily','Daily'),
    ('weekly','Weekly'),
    ('monthly','Monthly'),
    ('less_frequently','Less Frequently'),
    ('not_at_all','Not at all')

    ]

    use_frequency = RadioField('use_frequency', choices=use_frequency_choices)

    type_of_use_choices = [
    ('read_posts','Read posts'),
    ('read_comments', 'Read comments'),
    ('vote','Vote'),
    ('comment','Write comments'),
    ('submit_content','Submit Content'),
    ('save_content', 'Save Content'),
    ('all','All of the above')
    ]

    type_of_use = SelectMultipleField('type_of__use',
                                            choices=type_of_use_choices,
                                            option_widget=widgets.CheckboxInput(),
                                            widget=widgets.ListWidget(prefix_label=False))

