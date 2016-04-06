from django.db import models
from kb.badges.models import *
from kb.models import UserProfile

class Skill(Badge):
    identification = None
    """This should be overriden by subclasses to set to a unique skill id."""

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        if self.identification:
            kwargs['badge_id'] = self.identification
        kwargs['badge_type'] = Badge.T_SKILL_BADGE
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_instance_by_id(identification):
        for skill_class in Skill.__subclasses__():
            if skill_class.identification == identification:
                return skill_class.get_instance()
        return None

    @classmethod
    def get_instance(cls):
        if cls.identification is None:
            raise ValueError("Skill class did not define identification")
        return cls.objects.get(pk=cls.identification)

    @classmethod
    def register_signals(self):
        pass


class CodeSkill(Skill):
    xp_increment = 1

    class Meta:
        proxy = True

    @classmethod
    def is_skill_in_code(cls, code):
        """Whether the submitted code exhibits this skill."""
        return False

    @classmethod
    def extract_from_code(cls, code, user, *args, **kwargs):
        if cls.is_skill_in_code(code):
            cls.get_instance().update_badge(user.profile, cls.xp_increment)

    @classmethod
    def register_signals(cls):
        from connectors.signals import parsed_submission
        from codelib import Root
        from codelib.signals import code_parsed
        from codelib.dialects import js
        parsed_submission.connect(cls.extract_from_code, sender=Root)
        #code_parsed.connect(cls.extract_from_code, sender=js.Dialect)


class SequenceSkill(CodeSkill):
    identification = 'code_skill_sequence'
    xp_increment = 1

    class Meta:
        proxy = True

    @classmethod
    def is_skill_in_code(cls, code):
        """Whether the submitted code exhibits this skill."""
        return code.node_count() > 1


class IfSkill(CodeSkill):
    identification = 'code_skill_if'
    xp_increment = 4

    class Meta:
        proxy = True

    @classmethod
    def is_skill_in_code(cls, code):
        """Whether the submitted code exhibits this skill."""
        from codelib import IfElse
        return code.contains(IfElse)


class IfElseSkill(CodeSkill):
    identification = 'code_skill_if_else'
    xp_increment = 5

    class Meta:
        proxy = True

    @classmethod
    def is_skill_in_code(cls, code):
        """Whether the submitted code exhibits this skill."""
        from codelib import IfElse
        return any(map(lambda s: s.else_block, code.find(IfElse)))


class ForSkill(CodeSkill):
    identification = 'code_skill_for'
    xp_increment = 10

    class Meta:
        proxy = True

    @classmethod
    def is_skill_in_code(cls, code):
        """Whether the submitted code exhibits this skill."""
        from codelib import For
        return code.contains(For)


class WhileSkill(CodeSkill):
    identification = 'code_skill_while'
    xp_increment = 6

    class Meta:
        proxy = True

    @classmethod
    def is_skill_in_code(cls, code):
        """Whether the submitted code exhibits this skill."""
        from codelib import While
        return code.contains(While)
