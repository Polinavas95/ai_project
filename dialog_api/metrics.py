from prometheus_client import Summary

DIALOG_GIGA_AINVOKE = Summary(
    "dialog_giga_ainvoke",
    "Время работы гигачата в режиме диалога"
)
QUIZ_GIGA_AINVOKE= Summary(
    "quiz_giga_ainvoke",
    "Время работы гигачата в режиме квиза"
)