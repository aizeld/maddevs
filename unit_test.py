import unittest
from msg_split import split_message 
from bs4 import BeautifulSoup

class TestSplitMessage(unittest.TestCase):

    def test_simple_split(self):
        #Test that a simple HTML string is split correctly
        source = "<p>" + "Hello World! " * 300 + "</p>"
        max_len = 1000
        fragments = list(split_message(source, max_len=max_len))
        for fragment in fragments:
            self.assertTrue(len(fragment) <= max_len)
            
            soup = BeautifulSoup(fragment, 'html.parser')
            self.assertIsNotNone(soup.find('p'))

    def test_no_split_needed(self):
        #Test that if the source is shorter than max_len, it is not split
        source = "<p>Hello World!</p>"
        max_len = 1000
        fragments = list(split_message(source, max_len=max_len))
        self.assertEqual(len(fragments), 1)
        self.assertEqual(fragments[0], source)

    def test_unbreakable_tag_too_long(self):
        #Test that ValueError is raised when an unbreakable tag is too long
        source = "<a>" + "A" * 5000 + "</a>"
        max_len = 1000
        with self.assertRaises(ValueError) as context:
            list(split_message(source, max_len=max_len))
        self.assertIn("Non block tag text too long", str(context.exception))

    def test_preserve_structure(self):
        #Test that the function preserves the HTML structure across fragments
        source = "<div><p>Paragraph 1</p><p>Paragraph 2</p><p>Paragraph 3</p></div>"
        max_len = 50
        fragments = list(split_message(source, max_len=max_len))
        for fragment in fragments:
            soup = BeautifulSoup(fragment, 'html.parser')
            self.assertTrue(soup.find('div') or soup.find('p'))

    def test_does_not_break_non_block_tags(self):
    #Test that non-block tags are not broken across fragments
        source = "<p>Text with a <a href='link'>link</a> in it.</p>" * 100
        max_len = 500
        fragments = list(split_message(source, max_len=max_len))
        for fragment in fragments:
            self.assertNotIn('</a><a', fragment)
            soup = BeautifulSoup(fragment, 'html.parser')
            self.assertIsNotNone(soup.find('a'))

if __name__ == '__main__':
    unittest.main()
