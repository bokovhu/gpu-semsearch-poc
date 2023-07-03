import re


class Disassembler:
    def __init__(
        self,
        num_sentences=3,
        window_slide=2,
        sentence_delimiter_pattern="((?:[\\.\\?\\!\\n;]|```)\\s+)",
    ) -> None:
        self.num_sentences = num_sentences
        self.window_slide = window_slide
        self.sentence_delimiter_pattern = sentence_delimiter_pattern

    def disassemble(self, text: str):
        text_splitted = re.split(self.sentence_delimiter_pattern, text)
        stripped_parts = [l.strip() for l in text_splitted]
        non_empty_parts = [l for l in stripped_parts if len(l) > 1]
        sentences = []

        while len(non_empty_parts) > 0:
            sentences.append(non_empty_parts[0 : self.num_sentences])
            non_empty_parts = non_empty_parts[self.window_slide :]

        return sentences
