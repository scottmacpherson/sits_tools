import re

class XpcFile:
    def __init__(self, raw_input):
        self.raw_input = raw_input

    @staticmethod
    def prepare_raw_input(raw_input):
        # Remove any METADATA lines
        return re.sub(r"\n\d+\|METADATA=true.*", "", raw_input)

    @staticmethod
    def records_from_prepared_input(prepared_input):
        return [XpcRecord(record) for record in re.split(r"\n(?=\*?\d+\*?\|DCT_CODE=\w+\x1bENT_CODE=\w+\x1bUCODE_FORMAT=UTF8\x1b)", prepared_input)]

    @property
    def records(self):
        return self.records_from_prepared_input(self.prepare_raw_input(self.raw_input))

class XpcRecord:
    def __init__(self, raw_input):
        self.raw_input = raw_input

    @staticmethod
    def match_from_raw_input(raw_input):
        return re.fullmatch(r"^(?P<header>\*?(?P<length>\d+)\*?\|DCT_CODE=(?P<dictionary>\w+)\x1bENT_CODE=(?P<entity>\w+)\x1bUCODE_FORMAT=UTF8\x1b(?P<body>.*)$)", raw_input, flags=re.DOTALL)

    @property
    def parts(self):
        return self.match_from_raw_input(self.raw_input).groupdict()

    @property
    def record_length(self):
        return len(self.raw_input) - self.match_from_raw_input(self.raw_input).end("length")

    @property
    def valid(self):
        return int(self.parts["length"]) == self.record_length

    @property
    def body_as_dict(self):
        return re.split(r"(?<!\x15)\x1b", self.parts["body"])

if __name__ == '__main__':
    records = XpcFile(open("…", encoding="utf-8-sig").read()).records
    print(f"{len(records)=}")
