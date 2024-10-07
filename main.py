import re
import json
import tinycss2
from at_media_handling import extract_class_from_media_queries, combine_matching_media_queries, combine_nested_classes_in_media
from psudo_selector import split_css_classes_and_pseudo, split_css_by_pseudo_selector, combine_css_classes_with_pseudo
import logging
import argparse
from html_parser import parse_html


logger = logging.getLogger(__name__)
# This formatting is used across all the scripts
LOGGING_FORMATING = "%(asctime)s - %(filename)s:%(funcName)s:%(lineno)s - %(levelname)s - %(message)s"

def extract_regular_css_class(css_content, wanted_class_name): 
    rules = tinycss2.parse_stylesheet_bytes(css_content, skip_whitespace=True, skip_comments=True)
    extracted_css_nodes = []
    for rule in rules[0]:
        if isinstance(rule, tinycss2.ast.QualifiedRule):
            class_name = rule.prelude[1]
            if isinstance(class_name, tinycss2.ast.IdentToken):
                if class_name.value == wanted_class_name:
                    extracted_css_nodes.append(rule)
    if len(extracted_css_nodes) == 0:
        return None
    else:
        extracted_css = tinycss2.serialize(extracted_css_nodes)
        return extracted_css

def combine_regular_css_classes(css_contents, combined_class_name):
    # Updated regex pattern to match class selectors with dashes and underscores
    class_pattern = re.compile(r'\.([a-zA-Z0-9-_]+)\s*{([^}]*)}', re.DOTALL)
    
    # List to hold combined styles
    combined_styles = []

    # Extract and combine styles
    for match in class_pattern.finditer(css_contents):
        og_class_name = match.group(1).strip()
        og_class_name_comment = f"/*{og_class_name}*/"
        combined_styles.append(og_class_name_comment)
        styles = match.group(2).strip()
        combined_styles.append(styles)

    # Combine all styles into the new class
    combined_css = f".{combined_class_name} {{\n"
    combined_css += '\n'.join(combined_styles)
    combined_css += "\n}"

    return combined_css


def write_regular_css_to_new_class(css_content: str, new_class_name: str):
    regular_classes_match, psudo_classes_match = split_css_classes_and_pseudo(css_content)

    psudo_selectors_string = ''
    psudo_class_dict = split_css_by_pseudo_selector(psudo_classes_match)

    for psudo_class, psudo_css_content in psudo_class_dict.items():
        new_psudo_content = combine_css_classes_with_pseudo(psudo_class, psudo_css_content, new_class_name)
        psudo_selectors_string = psudo_selectors_string + '\n\n' + new_psudo_content

    regular_css = combine_regular_css_classes(regular_classes_match, new_class_name)

    all_css = '\n'.join([regular_css, psudo_selectors_string])
    return all_css

def write_at_media_to_new_class(css_content: str, new_class_name: str):
    if not css_content:
        return ""
    all_media_queries_list = combine_matching_media_queries(css_content)
    all_query_classes = []
    for media in all_media_queries_list:
        query_class = combine_nested_classes_in_media(media, new_class_name)
        all_query_classes.append(query_class)

    all_css = '\n'.join(all_query_classes)
    return all_css   

def tailwind_keepout(input_class_name: str):
    # Tailwind not selector, we need to fix this....
    cotains_class = ["space-y", "space-x", "group-hover:"]
    for classer in cotains_class:
        if classer in input_class_name:
            return True
    exact_match = ["group"]
    for classer in exact_match:
        if classer == input_class_name:
            return True
    return False

def css_class_converter(css_content: str, new_class_name: str, class_name_array: [str]):
    regular_css_buffer = ''
    at_media_css_buffer = ''
    not_found_regular_css_class = []
    not_found_media_css_class = []

    for class_name in class_name_array:
        regular_class_buffer = []
        at_media_class_buffer = []

        if tailwind_keepout(class_name):
            not_found_regular_css_class.append(class_name)
            not_found_media_css_class.append(class_name)
            continue
        
        reg_res = extract_regular_css_class(css_content, class_name)
        if reg_res:
            regular_class_buffer.append(reg_res)
        else:
            not_found_regular_css_class.append(class_name)
        
        at_media_res = extract_class_from_media_queries(css_content, class_name)
        if at_media_res:
            at_media_class_buffer.append(at_media_res)
        else:
            not_found_media_css_class.append(class_name)

        if regular_class_buffer:
            regular_css_string = '\n'.join(regular_class_buffer)
            regular_css_buffer = regular_css_buffer + "\n" + regular_css_string

        if at_media_class_buffer:
            at_media_css_string = '\n'.join(at_media_class_buffer)
            at_media_css_buffer = at_media_css_buffer + "\n" + at_media_css_string

    all_regular_css = write_regular_css_to_new_class(regular_css_buffer, new_class_name)
    all_at_media_css = write_at_media_to_new_class(at_media_css_buffer, new_class_name)

    classes_not_found = list(set(not_found_regular_css_class).intersection(not_found_media_css_class))

    new_CSS_buffer = ''
    new_CSS_buffer = new_CSS_buffer + all_regular_css
    new_CSS_buffer = new_CSS_buffer +"\n\n"
    new_CSS_buffer = new_CSS_buffer + all_at_media_css
    if classes_not_found:
        new_CSS_buffer = new_CSS_buffer +"\n"
        classes_not_found_string = ' '.join(classes_not_found)
        new_CSS_buffer = new_CSS_buffer +"\n"
        new_CSS_buffer = new_CSS_buffer + f"/* Classes not found for {new_class_name}*/"
        new_CSS_buffer = new_CSS_buffer +"\n"
        new_CSS_buffer = new_CSS_buffer + f"/* {classes_not_found_string} */"
    new_CSS_buffer = new_CSS_buffer +"\n\n"
    return new_CSS_buffer

def run_css_extraction(input_css_file, input_data_file, output_file):
    with open(input_css_file, 'rb') as fd:
        css_content = fd.read()
    
    with open(input_data_file) as input_data_f:
        input_list = json.load(input_data_f)

    open(output_file, "w").close()
    output_css_file = open(output_file, "a")
    
    for input_item in input_list:
        oldClassesString = input_item['oldClasses']
        old_classes = oldClassesString.split(",")
        old_classes = [x.strip() for x in old_classes]
        newClassName = input_item['newClass']
        converted_css = css_class_converter(css_content, newClassName, old_classes)
        output_css_file.write(converted_css)

    output_css_file.close()

def html(parsed_args):
    input_html_file = getattr(parsed_args, 'input_html_file')
    if not input_html_file:
        raise Exception("--input-html-file needs to be defined for --html extraction")
    output_json_file = getattr(parsed_args, 'output_json_file')
    if not output_json_file:
        raise Exception("--output-json-file needs to be defined for --html extraction")
    output_html_file = getattr(parsed_args, 'output_html_file')
    if not output_html_file:
        raise Exception("--output-html-file needs to be defined for --html extraction")
    parse_html(input_html_file, output_json_file, output_html_file)

def css(parsed_args):
    input_css_file = getattr(parsed_args, 'input_css_file')
    if not input_css_file:
        raise Exception("--input-css-file needs to be defined for --css extraction")
    input_json_file = getattr(parsed_args, 'input_json_file')
    if not input_json_file:
        raise Exception("--input-json-file needs to be defined for --css extraction")
    output_css_file = getattr(parsed_args, 'output_css_file')
    if not output_css_file:
        raise Exception("--output-css-file needs to be defined for --css extraction")
    run_css_extraction(input_css_file, input_json_file, output_css_file)

if __name__ == "__main__":
    logging.basicConfig(
        format=LOGGING_FORMATING,
        level=logging.INFO,
    )
    parser = argparse.ArgumentParser(
                    prog='CSS-Extractor',
                    description='Extract CSS from a given HTML and CSS, rebuilds the classes into new classes with all the properties of the original.',
                    epilog='Get extracting')

    parser = argparse.ArgumentParser()
    parser.add_argument('--html', dest='action', action='store_const', const=html)
    parser.add_argument('--css', dest='action', action='store_const', const=css)
    # These args are used fot the html parser function
    parser.add_argument('--input-html-file')
    parser.add_argument('--output-html-file')
    parser.add_argument('--output-json-file')
    #These args are used fot the css parser function
    parser.add_argument('--input-css-file')
    parser.add_argument('--input-json-file')
    parser.add_argument('--output-css-file')

    parsed_args = parser.parse_args()
    if parsed_args.action is None:
        parser.parse_args(['-h'])
    parsed_args.action(parsed_args)
