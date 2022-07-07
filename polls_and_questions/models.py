from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

RESULT_PRIVACY_CHOICES = (('EVERYONE', 'Everyone can see the results'),
                          ('CREATOR_AND_SPEAKERS', 'The creator and the speakers can see the results'),
                          ('CREATOR', 'Only the creator can see the results'),
                          )


class User(models.Model):
    username = models.CharField(_('username'), max_length=150, unique=True)
    screen_name = models.CharField(_('screen name'), max_length=255)
    email = models.EmailField(_('email'))

    def __str__(self):
        return self.screen_name




class Interaction(models.Model):
    """
    Abstract data model for Interaction.

     Attributes:
         watchit_uuid (UUID): The watchit identifier.
         creator_id (UUID ): The creator identifier.
         question (str): The label for the interaction.

    """
    watchit_uuid = models.UUIDField('event identifier')
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.CharField(_('question'), max_length=256)

    class Meta:
        abstract = True


    def __str__(self):
        return self.question


ANSWERING_TIME_LIMIT_CHOICES = (
    (5, '5'),
    (10, '10'),
    (15, '15'),
    (20, '20'),
    (25, '25'),
    (30, '30'),
    (35, '35'),
    (40, '40'),
    (45, '45'),
    (50, '50'),
    (55, '55'),
    (60, '60'),
    (65, '65'),
    (70, '70'),
    (75, '75'),
)


class PollConfig(models.Model):
    """
    Model for Configuration of interation type Poll.

    Attributes:
        enabled (bool): Indicate if Poll component is enabled or not.
        multiple_answers (bool): Indicate if multiple answer response will be allowed or not.
        answering_time_limit (int): Time limit for answering.

    """
    enabled = models.BooleanField(_('Visibility in Event Room'))
    show_in_event_room = models.BooleanField(_('Show polls in the Event Room'))

    answers_privacy = models.CharField(_('Defaults results privacy'), max_length=20, choices=RESULT_PRIVACY_CHOICES)
    multiple_answers = models.BooleanField(_('allow multiple answer response'))
    answering_time_limit = models.PositiveIntegerField(choices=ANSWERING_TIME_LIMIT_CHOICES, default=0)
    allow_no_limitated_answering = models.BooleanField(_('allow answering with no time limitation'))
    answering_time_limit = models.PositiveIntegerField(choices=ANSWERING_TIME_LIMIT_CHOICES, default=5)

    def __str__(self):
        return "%s" % self.id


class Poll(Interaction):
    """
    Model for Interaction type Poll.

    Attributes:
        creation_date (DateTime): Creation Date for the poll.
        published (bool): Indicate if the poll is published or not.
        streaming (bool): Indicate if the poll is streaming or not.

    """
    configuration = models.ForeignKey(PollConfig, on_delete=models.CASCADE)

    creation_date = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(_('is published'), default=False)
    streaming = models.BooleanField(_('is streaming'), default=False)


class Choice(models.Model):
    """
    Model for option of Poll.

    poll (Poll): Poll the one that the option belongs to.
    choice (str): label for the choice.
    order (int): Order for choice in poll's list of options will appear in.

    """
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='answers')
    choice = models.CharField(_('choice'), max_length=256)

    def __str__(self):
        return self.choice

class PResponse(models.Model):
    """
    Model for Response of Poll

    poll (Poll): Poll the one that the response belongs to.
    selected_choice (list[Choice]): Choices selected in the response.
    participant_id (UUID): Identifier of the participant that responds.
    date (Date): Date of the response.
    """
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    selected_choice = models.ManyToManyField(Choice)
    participant_id = models.UUIDField(_('participant identificator'))
    date = models.DateTimeField(_('date'), auto_now=True)

    class Meta:
        verbose_name = _('poll responses')


class QuestionConfig(models.Model):
    """
    Model for configuration of interation type Question.

    enabled (bool): Indicate if Q&A component is enabled or not.
    allow_audience_create_questions (bool): Indicate if audience can create questions or not.
    auto_publish (bool): Indicate if Auto-publish the questions since the moment they are created.
    allow_audience_vote_questions (bool): Indicate if audience can vote questions or not.
    allow_audience_vote_answers (bool): Indicate if audience can vote answers or not.

    """
    enabled = models.BooleanField(_('Enable the Q&A componet'))

    allow_audience_create_questions = models.BooleanField(_('allow audience create questions'))
    auto_publish = models.BooleanField(_('Auto publish create questions'))
    allow_audience_vote_questions = models.BooleanField(_('audience can vote questions'))
    allow_audience_vote_answers = models.BooleanField(_('audience can vote answers'))

    answers_privacy = models.CharField(_('results privacy'), max_length=20, choices=RESULT_PRIVACY_CHOICES)

    def __str__(self):
        return "%s" % self.id


class Question(Interaction):
    """
    Model for Interation type Poll.
    """
    configuration = models.ForeignKey(QuestionConfig, on_delete=models.CASCADE)


class QResponse(models.Model):
    """
    Model for Response of Question.

    
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    participant_id = models.UUIDField(_('participant id'))
    response = models.CharField(_('response'), max_length=256)
    date = models.DateTimeField(_('date'), auto_now=True)

    class Meta:
        verbose_name = _('question responses')

    def __str__(self):
        """ Unicode representation of Response to Question"""

        return self.response


class EventConfig(models.Model):
    """ Model for configuration of events.

    watchit_uuid (UUID): The watchit identifier.
    default_poll_config(): Default configuration for polls in watchit.
    default_question_config(): Default configuration for questions in watchit.

    """
    watchit_uuid = models.UUIDField('event identifier', primary_key=True)
    default_polls_config = models.ForeignKey(PollConfig,
                                             on_delete=models.SET_NULL,
                                             related_name='default_polls_config',
                                             null=True,
                                             blank=True,
                                             )
    default_questions_config = models.ForeignKey(QuestionConfig,
                                                 on_delete=models.SET_NULL,
                                                 related_name='default_questions_config',
                                                 null=True,
                                                 blank=True,
                                                 )

    def __str__(self):
        """ Unicode representation of EventConfig """
        return "%s" % self.watchit_uuid
