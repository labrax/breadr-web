
from html_templates import SECTION_TEMPLATE


sections = [{'name': 'Basics', 'code': 'basics', 
             'functions': [{'type_identifier': 'input_element', 'name': ' Input', 'icon': 'fa-solid fa-arrow-right-to-bracket'},
                           {'type_identifier': 'output_element', 'name': ' Output', 'icon': 'fa-solid fa-arrow-right-from-bracket'}]},
            {'name': 'Crumbs', 'code': 'crumbs',
             'functions': [{'type_identifier': 'multiple_element', 'name': ' AAA', 'icon': 'fas fa-code'},
                           {'type_identifier': 'multiple_element', 'name': ' BBB', 'icon': 'fas fa-code'},
                           {'type_identifier': 'multiple_element', 'name': ' CCC', 'icon': 'fas fa-code'}]}
            ]


def get_function_list():
    ret = ''
    for s in sections:
        section_code = s['code']
        section_name = s['name']
        print(s['functions'])
        # section_content = '\n'.join([render_function(i) for i in s['functions']])
        ret += SECTION_TEMPLATE.generate(section_code=section_code, section_name=section_name, functions=s['functions']).decode('utf-8')
    return ret
