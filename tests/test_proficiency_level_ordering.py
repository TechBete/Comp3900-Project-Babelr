import unittest
from app.models import ProficiencyLevel
# Test cases to enforce the ordering of ProficiencyLevel.
class TestProficiencyOrdering(unittest.TestCase):
    def test_ordering(self):
        # Check that each proficiency level is less than the one following it.
        self.assertLess(ProficiencyLevel.elementary, ProficiencyLevel.limited_working)
        self.assertLess(ProficiencyLevel.limited_working, ProficiencyLevel.professional)
        self.assertLess(ProficiencyLevel.professional, ProficiencyLevel.native)
        self.assertLess(ProficiencyLevel.native, ProficiencyLevel.bilingual)

    def test_reverse_ordering(self):
        # Check that the reverse relations hold true.
        self.assertGreater(ProficiencyLevel.limited_working, ProficiencyLevel.elementary)
        self.assertGreater(ProficiencyLevel.professional, ProficiencyLevel.limited_working)
        self.assertGreater(ProficiencyLevel.native, ProficiencyLevel.professional)
        self.assertGreater(ProficiencyLevel.bilingual, ProficiencyLevel.native)

    def test_equality(self):
        # Verify that the same level is equal to itself and different levels are not.
        self.assertEqual(ProficiencyLevel.elementary, ProficiencyLevel.elementary)
        self.assertNotEqual(ProficiencyLevel.elementary, ProficiencyLevel.limited_working)
