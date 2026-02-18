

import re


def sanitize_filename(name: str, replacement: str = '_') -> str:
	""""""
	# Remove leading/trailing whitespace
	name = name.strip()

	# Replace non-alphanumeric/dot/dash/underscore with replacement character
	name = re.sub(r'[^\w\.-]', replacement, name)

	# Collapse multiple contiguous replacements into a single one
	name = re.sub(f'{re.escape(replacement)}+', replacement, name)

	# Remove leading period; prevent hidden files on unix
	if name.startswith('.'):
		name = f"{name[1:]}"

	return name