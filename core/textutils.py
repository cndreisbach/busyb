def get_hashtags(text):
    """
    Split a string by spaces, then strip off punctuation, returning
    only the words that start with a pound sign.
    """
    tags = {
        item.strip("#.,-\"\'&*^!")
        for item in text.split()
        if item.startswith("#")
    }
    return tags
