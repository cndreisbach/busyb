from hashids import Hashids
hashids = Hashids(min_length=4)


class HashidConverter:
    regex = '[a-zA-Z0-9]{4,}'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value
