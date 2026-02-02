import argparse
import pprint
import re


class XpcFile:
    def __init__(self, raw_input):
        self.raw_input = raw_input

    def prepare_raw_input(self):
        # Remove any METADATA lines
        return re.sub(r"\n\d+\|METADATA=true.*", "", self.raw_input)

    @property
    def records(self):
        # Return a list of XpcRecord objects by splitting prepared content
        # at each newline + record header. Uses positive lookahead to retain
        # record header in the match.
        return [
            XpcRecord(record)
            for record in re.split(
                r"\n(?=\*?\d+\*?\|DCT_CODE=\w+\x1bENT_CODE=\w+\x1bUCODE_FORMAT=UTF8\x1b)",
                self.prepare_raw_input(),
            )
        ]


class XpcRecord:
    def __init__(self, raw_input):
        self.raw_input = raw_input

        # XPC files sometime have a linebreak at the end, sometimes don't, but
        # the last field in the last record in the file might end with a bunch
        # of linebreaks so it's not as simple as trimming the record.
        # If declared length != match length, but declared length *does* equal
        # match length - 1, then assume that's why.
        try:
            assert self.valid
        except AssertionError:
            if XpcRecord(raw_input[:-1]).valid:
                self.raw_input = raw_input[:-1]
            else:
                raise

    def match_from_raw_input(self):
        # Extract declared length, dictionary, entity, and content.
        return re.fullmatch(
            r"^(?P<header>(?P<length_padding>\*?(?P<length>\d+)\*?)\|DCT_CODE=(?P<dictionary>\w+)\x1bENT_CODE=(?P<entity>\w+)\x1bUCODE_FORMAT=UTF8\x1b(?P<body>.*)$)",
            self.raw_input,
            flags=re.DOTALL,
        )

    @property
    def parts(self):
        # Present match as a dictionary of it's parts
        return self.match_from_raw_input().groupdict()

    @property
    def record_length(self):
        # XPC declared length counts all characters from the bar immediately
        # following the declaration (inclusive), but the length declaration
        # might be padded with asterisks, so the match includes "length_padding"
        # to deal with that condition.
        return len(self.raw_input) - self.match_from_raw_input().end("length_padding")

    @property
    def valid(self):
        return int(self.parts["length"]) == self.record_length

    @property
    def body_as_dict(self):
        # Split record body at regular (and only regular) gold-semi-colons.
        # Split each field at the first "=" to get field code/field value.
        return {
            key: value
            for field in re.split(r"(?<!\x15)\x1b", self.parts["body"])
            for key, value in (re.split("=", field, maxsplit=1),)
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert the given SITS:Vision XPC file into a Python dict and pretty-print it"
    )
    parser.add_argument("path")

    pprint.pp(
        [
            record.body_as_dict
            for record in XpcFile(
                open(parser.parse_args().path, encoding="utf-8-sig").read()
            ).records
        ]
    )
