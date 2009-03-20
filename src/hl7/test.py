import unittest

import core
import segments
import pdb


class TestMessages(unittest.TestCase):
    def testMessageCreation(self):
        pass

class TestSegment(unittest.TestCase):
    def setUp(self):
        self.msh = segments.MSH()
        self.orc = segments.ORC()

    def testGetAttibute(self):
        self.assert_(self.orc.key == 'ORC')

    def testSetAttribute(self):
        self.orc.filler_number = 'OK'
        self.assert_(self.orc.filler_number == 'OK')

    def testCannotsetInvalidField(self):
        def try_invalid_attribution(segment, value):
            segment.invalid_attribute = value
            
            
        msh = segments.MSH()
        self.assertRaises(Exception, try_invalid_attribution, msh, 12)
        






        
if __name__ == '__main__':
    unittest.main()
