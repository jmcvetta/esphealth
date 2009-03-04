import unittest


import core



class TestHL7Messages(unittest.TestCase):
    def testMessageCreation(self):
        pass




        
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHL7Messages)
    unittest.TextTestRunner(verbosity=2).run(suite)

