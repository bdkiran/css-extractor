import re
from collections import defaultdict
import logging
import tinycss2

logger = logging.getLogger(__name__)

def extract_class_from_media_queries(css_content, className):
    rules = tinycss2.parse_stylesheet_bytes(css_content, skip_whitespace=True, skip_comments=True)
    # Dictionary to hold combined styles for each @media condition
    media_blocks = defaultdict(list)
    for rule in rules[0]:
        if isinstance(rule, tinycss2.ast.AtRule):
            if rule.at_keyword == "media":
                media_block = rule.prelude[1]
                no_whitespace_rule = tinycss2.parse_blocks_contents(rule.content, skip_whitespace=True, skip_comments=True)
                for at_media_rule in no_whitespace_rule:
                    class_name = at_media_rule.prelude[1]
                    if isinstance(class_name, tinycss2.ast.IdentToken):
                        if class_name.value == className:
                            media_blocks[media_block].append(at_media_rule)
    if not media_blocks:
        return None
    else:
        full_css_string = ''
        for media_condition, blocks in media_blocks.items():
            extracted_css = tinycss2.serialize(blocks)
            full_media_block = "@media " + media_condition.serialize() + "{\n" + extracted_css + "\n}\n\n"
            full_css_string = full_css_string + full_media_block
        return full_css_string

def combine_matching_media_queries(css_content):
    byte_thing = str.encode(css_content)
    rules, encoding = tinycss2.parse_stylesheet_bytes(byte_thing, skip_whitespace=True, skip_comments=True)
    # Dictionary to hold combined styles for each @media condition
    media_blocks = defaultdict(list)
    for rule in rules:
        if isinstance(rule, tinycss2.ast.AtRule):
            if rule.at_keyword == "media":
                media_block = rule.prelude[1]
                no_whitespace_rule = tinycss2.parse_blocks_contents(rule.content, skip_whitespace=True, skip_comments=True)
                for at_media_rule in no_whitespace_rule:
                    class_name = at_media_rule.prelude[1]
                    if isinstance(class_name, tinycss2.ast.IdentToken):
                            media_blocks[media_block].append(at_media_rule)

    # Combine the content of matching @media conditions
    combined_media_css = []
    for media_condition, blocks in media_blocks.items():
        contents = tinycss2.serialize(blocks)
        full_media_block = "@media " + media_condition.serialize() + "{\n" + contents + "\n}\n\n"
        combined_media_css.append(full_media_block)

    return combined_media_css

def combine_nested_classes_in_media(css_content, combined_class_name):    
    media_condition = ""
    contents = ""
    byte_thing = str.encode(css_content)
    rules, encoding = tinycss2.parse_stylesheet_bytes(byte_thing, skip_whitespace=True, skip_comments=True)
    for rule in rules:
        if isinstance(rule, tinycss2.ast.AtRule):
            if rule.at_keyword == "media":
                media_block = rule.prelude[1]
                media_condition = media_block
                no_whitespace_rule = tinycss2.parse_blocks_contents(rule.content, skip_whitespace=True, skip_comments=True)
                for at_media_rule in no_whitespace_rule:
                    class_name = at_media_rule.prelude[1]
                    if isinstance(class_name, tinycss2.ast.IdentToken):
                            combined_css = f".{combined_class_name} {{\n"
                            combined_css += f"/*{class_name.value}*/" # Add the old class name
                            combined_css += tinycss2.serialize(at_media_rule.content)
                            combined_css += "\n}"
                            contents += combined_css
    full_media_block = "@media " + media_condition.serialize() + "{\n" + contents + "\n}\n\n"
    return full_media_block