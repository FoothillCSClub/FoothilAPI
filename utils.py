from re import match

from settings import COURSE_TYPES_TO_FLAGS

COURSE_NAME_PATTERN = r'[FD]0*(\d*\w?H?)\.?'

class ValidationError(Exception):
    def __init__(self, message: str, details: str):
        self.message = message
        self.details = details

def parse_course_string(raw_class: str):
    '''
    This is the key parser for the course names

    :param raw_class: (str) The unparsed string containing the course name
    :return match_obj.groups(): (list) the string for the regex match
    '''
    # Split the raw course string by a space, to separate different parts
    # ex. 'C S D001A01Z' => ['C', 'S', 'D001A01Z']
    parts = raw_class.split(' ')

    if len(parts) < 2:
        raise ValidationError(
            'Raw course string is invalid',
            'At least two space separated parts could not be found'
        )

    # All parts excluding the last one are assumed to be the department name
    # ex. `C S` => `CS`
    dept = ''.join(parts[0:-1])
    # The last part is the actual course string (without the department)
    # ex. `D001A01Z`
    without_dept = parts[-1]

    if len(without_dept) < 6 or len(without_dept) > 8:
        raise ValidationError(
            'Course + Section ID is invalid or unknown',
            'Length of raw course string without the dept is not between 6-8 chars'
        )

    # First five characters are the course name
    # ex. `D001A` or `F04BH`
    course = without_dept[0:5]
    # Regex to clean the leading `F` / `D` and extraneous 0's
    match_obj = match(COURSE_NAME_PATTERN, course)

    if not match_obj.groups():
        raise ValidationError(
            'Unable to extract the course name (ex. "24A")',
            'Course name regex does not match'
        )

    # Cleaned course name, e.g. `4A`
    cleaned_course = match_obj[1]

    # The last chars are the class section + flags
    # ex. `01Z` or `5ZH`
    section = without_dept[5:]

    # Extract flags by filtering nonalphabets from the class section
    flags = set(filter(str.isalpha, section))

    return {
        'dept': dept,
        'course': cleaned_course,
        'section': section,
        'flags': flags,
    }

def get_class_type(campus: str, flags: set):
    class_type = None

    for name, flag in COURSE_TYPES_TO_FLAGS[campus].items():
        if name != 'standard' and flag in flags:
            if class_type:
                raise ValidationError('Class has multiple types in its flags', '')
            class_type = name

    if not class_type:
        class_type = 'standard'

    return class_type
