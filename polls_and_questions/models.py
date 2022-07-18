from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import InteractionUser

RESULT_PRIVACY_CHOICES = (('EVERYONE', 'Everyone can see the results'),
                          ('CREATOR_AND_SPEAKERS', 'The creator and the speakers can see the results'),
                          ('ONLY_CREATOR', 'Only the creator can see the results'),
                          )

EXTERNAL_USERS_CHOICES = (
    ('SYSTEM', _('Sistem user')), # users with accounts in external API
    ('PARTICIPANT', _('Participant user')),  # users logged with email in external API

)


class Interaction(models.Model):
    """
    Abstract data model for Interaction.

     Attributes:
         watchit_uuid (UUID): The watchit identifier.
         creator_id (UUID ): The creator identifier.
         question (str): The label for the interaction.

    """
    watchit_uuid = models.UUIDField('event identifier')
    creator = models.ForeignKey(InteractionUser, on_delete=models.CASCADE, )
    question = models.CharField(_('question'), max_length=256)

    creation_date = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(_('is published'), default=False)
    streaming = models.BooleanField(_('is streaming'), default=False)

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
        multiple_answers (bool): Indicate if multiple answer answer will be allowed or not.
        answering_time_limit (int): Time limit for answering.

    """
    enabled = models.BooleanField(_('Visibility in Event Room'), default=True)

    answers_privacy = models.CharField(_('Defaults results privacy'), max_length=20, choices=RESULT_PRIVACY_CHOICES)
    multiple_answers = models.BooleanField(_('allow multiple answer answer'), default=True)
    allow_no_limited_answering = models.BooleanField(_('allow answering with no time limitation'), default=True)
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


class PAnswer(models.Model):
    """
    Model for Answer of Poll

    poll (Poll): Poll the one that the answer belongs to.
    selected_choice (list[Choice]): Choices selected in the answer.
    participant_id (UUID): Identifier of participant that responds.
    creation_date (Date): Date of the answer.
    """
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    selected_choice = models.ManyToManyField(Choice)
    creator = models.ForeignKey(InteractionUser, on_delete=models.CASCADE, )
    creation_date = models.DateTimeField(_('creation_date'), auto_now=True)

    class Meta:
        verbose_name = _('poll answer')


class QuestionConfig(models.Model):
    """
    Model for configuration of interation type Question.

    enabled (bool): Indicate if Q&A component is enabled or not.
    allow_audience_create_questions (bool): Indicate if audience can create questions or not.
    auto_publish (bool): Indicate if Auto-publish the questions since the moment they are created.
    allow_audience_vote_questions (bool): Indicate if audience can vote questions or not.
    allow_audience_vote_answers (bool): Indicate if audience can vote answers or not.

    """
    enabled = models.BooleanField(_('Enable the Q&A componet'), default=True)

    allow_audience_create_questions = models.BooleanField(_('allow audience create questions'), default=True)
    auto_publish = models.BooleanField(_('Auto publish create questions'), default=True)
    allow_audience_vote_questions = models.BooleanField(_('audience can vote questions'), default=True)
    allow_audience_vote_answers = models.BooleanField(_('audience can vote answers'), default=True)

    answers_privacy = models.CharField(_('results privacy'), max_length=20, choices=RESULT_PRIVACY_CHOICES)

    def __str__(self):
        return "%s" % self.id


class Question(Interaction):
    """
    Model for Interaction type Question.
    """
    configuration = models.ForeignKey(QuestionConfig, on_delete=models.CASCADE)

    @property
    def votes_count(self):
        """ Retrieve count of votes for the question  """
        return self.votes.count()

class QAnswer(models.Model):
    """
    Model for Answer of Question.

    
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    creator = models.ForeignKey(InteractionUser, on_delete=models.CASCADE, )
    answer = models.CharField(_('answer'), max_length=256)
    creation_date = models.DateTimeField(_('creation_date'), auto_now=True)

    class Meta:
        verbose_name = _('question answer')

    def __str__(self):
        """ Unicode representation of Response to Question """
        return self.answer

    @property
    def votes_count(self):
        """ Retrieve count of votes for the question  """
        return self.votes.count()


class AbstractVote(models.Model):
    """ Abstract model for votes"""
    user = models.ForeignKey(InteractionUser, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(_('creation_date'), auto_now=True)

    class Meta:
        abstract = True


class QVote(AbstractVote):
    """ Model for question vote """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='votes')

    def __str__(self):
        return self.question.__str__()

    class Meta:
        verbose_name = _('question vote')
        unique_together = ('question', 'user')


class QAVote(AbstractVote):
    """ Model for question answer vote """
    answer = models.ForeignKey(QAnswer, on_delete=models.CASCADE, related_name='votes')

    class Meta:
        verbose_name = _('answer vote')
        unique_together = ('answer', 'user')

    def __str__(self):
        return self.answer.__str__()

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
