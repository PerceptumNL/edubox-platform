from django.apps import AppConfig


class SkillsConfig(AppConfig):
    name = 'kb.skills'

    def ready(self):
        self.get_model('SequenceSkill').register_signals()
        self.get_model('IfSkill').register_signals()
        self.get_model('IfElseSkill').register_signals()
        self.get_model('ForSkill').register_signals()
        self.get_model('WhileSkill').register_signals()
