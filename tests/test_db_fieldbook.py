from context import db_fieldbook as db


class TestDbFieldbook:

    def test_valid_mobile_number_returns_student_dict(self):
        result = db.get_student_if_valid_else_none('447793885600')
        assert result['name'] == 'Matt Stibbs'

    def test_invalid_mobile_number_returns_None(self):
        result = db.get_student_if_valid_else_none('440000000000')
        assert result is None