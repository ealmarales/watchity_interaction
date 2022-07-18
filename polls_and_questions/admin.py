from django.contrib import admin

from polls_and_questions.models import PollConfig, Choice, Poll, PAnswer, QuestionConfig, \
    Question, QAnswer, EventConfig, QVote, QAVote

admin.site.register(PollConfig)
admin.site.register(Choice)


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    class ChoiceInline(admin.StackedInline):
        model = Choice
        extra = 1

    inlines = [ChoiceInline]


@admin.register(PAnswer)
class PResponseAdmin(admin.ModelAdmin):
    filter_horizontal = ('selected_choice',)


# ---------------------------------------
@admin.register(QuestionConfig)
class DefaultQuestionConfigAdmin(admin.ModelAdmin):
    pass


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    class QResponseInline(admin.StackedInline):
        model = QAnswer
        extra = 1
    inlines = [QResponseInline]

@admin.register(QAnswer)
class QResponseAdmin(admin.ModelAdmin):
    pass

@admin.register(EventConfig)
class EventConfigAdmin(admin.ModelAdmin):
    pass

@admin.register(QVote)
class QAdmin(admin.ModelAdmin):
    pass

@admin.register(QAVote)
class QAAdmin(admin.ModelAdmin):
    pass