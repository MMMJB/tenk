class Trie:
    def __init__(self):
        """Initialize a Trie node."""
        self._is_end = False
        self._children = {}

    @property
    def is_end(self):
        """Check if the current node marks a complete word."""
        return self._is_end

    @property
    def children(self):
        """Access the children of the current Trie node."""
        return self._children

    def has_char(self, char):
        """Check if the given character is present in the current Trie."""
        return self._children.get(char)

    def add_char(self, char):
        """Add a Trie node at the given character, and return the new Trie."""
        new_sub_trie = Trie()
        self._children[char] = new_sub_trie
        return new_sub_trie

    def make_end(self):
        """Mark the current Trie node as the end of a complete word."""
        self._is_end = True

    def search_trie(self, word):
        """Search for a given word in the Trie."""
        if not word:
            return self.is_end

        sub_trie = self.has_char(word[0])
        if sub_trie is None:
            return False

        return sub_trie.search_trie(word[1:])

    def add_word(self, word):
        """Add a word to the Trie."""
        if not word:
            self.make_end()
            return

        sub_trie = self.has_char(word[0])
        if sub_trie:
            sub_trie.add_word(word[1:])
        else:
            new_sub_trie = self.add_char(word[0])
            new_sub_trie.add_word(word[1:])

    @staticmethod
    def build_trie(word_list):
        """Build a Trie from a list of words."""
        trie = Trie()
        for word in word_list:
            trie.add_word(word)
        return trie
