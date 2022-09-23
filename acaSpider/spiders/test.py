import re



def remove_html(self, string):
    pattern = re.compile(r'<[^>]+>')
    return (re.sub(pattern, '', string).replace('\n', '').replace('  ', '')).strip()


if __name__ == '__main__':
    print_hi('PyCharm')