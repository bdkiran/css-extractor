import re
import tinycss2
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

def does_prelude_contain_psuodo_selector(prelude):
    for item in prelude:
        if isinstance(item, tinycss2.ast.LiteralToken):
            if item.value == ":":
                return True
    return False

def get_psudo_selector_from_prelude(prelude):
    my_psudo = ""
    for item in prelude:
        if isinstance(item, tinycss2.ast.LiteralToken):
            if item.value == ":":
                my_psudo += ":"
        if len(my_psudo) >= 1 and isinstance(item, tinycss2.ast.IdentToken):
            my_psudo += item.value
            return my_psudo
    return None

def split_css_classes_and_pseudo(css_content):
    byte_thing = str.encode(css_content)
    rules = tinycss2.parse_stylesheet_bytes(byte_thing, skip_whitespace=True, skip_comments=True)
    regular_classes = []
    psedo_selector_classes = []
    for rule in rules[0]:
        if isinstance(rule, tinycss2.ast.QualifiedRule):
            class_name = rule.prelude[1]
            if isinstance(class_name, tinycss2.ast.IdentToken):
                if does_prelude_contain_psuodo_selector(rule.prelude):
                    psedo_selector_classes.append(rule)
                else:
                    regular_classes.append(rule)
    
    regular_class_string = tinycss2.serialize(regular_classes)
    psudo_class_string = tinycss2.serialize(psedo_selector_classes)
    return regular_class_string, psudo_class_string

def split_css_by_pseudo_selector(css_content):
    pseudo_styles_string_dict = {}
    if css_content == "":
        logger.error("no css content for psudo selector")
        pseudo_styles_string_dict
    # Dictionary to hold styles for each pseudo-selector
    pseudo_styles = defaultdict(list)
    byte_thing = str.encode(css_content)
    rules = tinycss2.parse_stylesheet_bytes(byte_thing, skip_whitespace=True, skip_comments=True)
    for rule in rules[0]:
        if isinstance(rule, tinycss2.ast.QualifiedRule):
            class_name = rule.prelude[1]
            if isinstance(class_name, tinycss2.ast.IdentToken):
                psudo = get_psudo_selector_from_prelude(rule.prelude)
                if not psudo:
                    error_log = "unable to parse class {}".format(class_name.value)
                    logger.error(error_log)
                else:
                    pseudo_styles[psudo].append(rule)
    for psedo, blocks in pseudo_styles.items():
        contents = tinycss2.serialize(blocks)
        pseudo_styles_string_dict[psedo] = contents

    return pseudo_styles_string_dict    

def combine_css_classes_with_pseudo(pseudo_selector: str, css_content:str, combine_class_name: str):
    combined_styles = []
    byte_thing = str.encode(css_content)
    rules = tinycss2.parse_stylesheet_bytes(byte_thing, skip_whitespace=True, skip_comments=True)
    for rule in rules[0]:
        if isinstance(rule, tinycss2.ast.QualifiedRule):
            class_name = rule.prelude[1]
            if isinstance(class_name, tinycss2.ast.IdentToken):
                combined_styles.append(f"/*{class_name.value}*/")
                combined_styles.append(tinycss2.serialize(rule.content))

    combined_styles_str = '\n'.join(combined_styles)
    new_class_name = f".{combine_class_name}{pseudo_selector}"
    return f"{new_class_name} {{\n{combined_styles_str}\n}}"
    
    
    