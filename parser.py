import json
import os
import re

def sanitize_filename(name):
    """
    Replace invalid filename characters with underscores.
    Allowed characters: alphanumeric, underscore, hyphen.
    Spaces are replaced with underscores.
    """
    safe_name = re.sub(r'[^\w\s-]', '_', name)
    safe_name = re.sub(r'\s+', '_', safe_name).strip('_')
    return safe_name

def replace_citations(text, references):
    """
    Replace citation markers in the HTML text with clickable links that include a popup title.
    This version supports markers with comma separated numbers, e.g., [1,2].

    Parameters:
      text: The HTML text string that may contain citation markers.
      references: A list of dictionaries where each dictionary should have keys "text" and "link".

    Returns:
      Updated text with clickable links for each reference.
    """
    # This regex will match things like [1] or [1,2, 3]
    citation_pattern = re.compile(r'\[([\d\s,]+)\]')

    def replacement(match):
        # Get the group with digits and commas and strip extra spaces
        numbers_str = match.group(1)
        # Split by comma and remove extra spaces for each number
        numbers = [num.strip() for num in numbers_str.split(',') if num.strip().isdigit()]
        # For each number, build its clickable link if possible.
        links = []
        for num in numbers:
            try:
                ref = references[int(num) - 1]
                link = ref["link"]
                title = ref["text"]
                links.append(f'<a href="{link}" title="{title}" target="_blank">[{num}]</a>')
            except (IndexError, ValueError):
                # If reference not available, use the original marker for that number.
                links.append(f'[{num}]')
        # Return the joined clickable markers, wrapped in brackets.
        return f'{"".join(links)}'

    return citation_pattern.sub(replacement, text)

def process_information(information_item):
    """
    Process a single information item by replacing citation markers with clickable links,
    if the 'reference' key is provided.
    """
    text = information_item.get('information_text', '')
    if 'reference' in information_item:
        references = information_item['reference']
        text = replace_citations(text, references)
    return text

def save_article_html(name, html_content, output_dir="output_html"):
    """
    Write the processed HTML content to a file named after the article name.
    Filenames are sanitized to replace invalid characters.
    """
    safe_name = sanitize_filename(name)
    filename = os.path.join(output_dir, f"{safe_name}.html")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    with open('a_nice.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    output_dir = "output_html"
    os.makedirs(output_dir, exist_ok=True)

    for entry in data.get('internal_content', []):
        # Case 1: Entry with "name" and "content"
        if 'name' in entry and 'content' in entry:
            name = entry['name']
            try:
                info_item = entry['content'][0]['information'][0]
                html_text = process_information(info_item)
                save_article_html(name, html_text, output_dir)
            except (IndexError, KeyError, TypeError):
                print(f"Warning: Skipped malformed entry with name '{name}'")
        # Case 2: Entry with a "sub_category" list
        elif 'sub_category' in entry:
            for sub in entry['sub_category']:
                try:
                    sub_name = sub['name']
                    info_item = sub['information'][0]
                    html_text = process_information(info_item)
                    save_article_html(sub_name, html_text, output_dir)
                except (IndexError, KeyError, TypeError):
                    print("Warning: Skipped malformed sub_category entry")

if __name__ == "__main__":
    main()
