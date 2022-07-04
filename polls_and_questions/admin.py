from django.contrib import admin

from polls_and_questions.models import DefaultPollConfig, Choice, Poll, PResponse, DefaultQuestionConfig, \
    Question, QResponse, EventConfig


admin.site.register(DefaultPollConfig)
admin.site.register(Choice)


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    class ChoiceInline(admin.StackedInline):
        model = Choice
        extra = 1

    inlines = [ChoiceInline]


@admin.register(PResponse)
class PResponseAdmin(admin.ModelAdmin):
    filter_horizontal = ('selected_choice',)


# ---------------------------------------
@admin.register(DefaultQuestionConfig)
class DefaultQuestionConfigAdmin(admin.ModelAdmin):
    pass


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    class QResponseInline(admin.StackedInline):
        model = QResponse
        extra = 1
    inlines = [QResponseInline]

@admin.register(QResponse)
class QResponseAdmin(admin.ModelAdmin):
    pass

@admin.register(EventConfig)
class EventConfigAdmin(admin.ModelAdmin):
    pass