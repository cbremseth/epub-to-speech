import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re


def extract_epub_to_markdown(epub_path, output_file):
    """
    Process an EPUB file, extract content and headers, and save as markdown.

    Args:
        epub_path: Path to the EPUB file
        output_file: Path to save the markdown output

    Returns:
        str: Path to the created markdown file
    """
    try:
        # Read the EPUB file
        book = epub.read_epub(epub_path)

        # Get book metadata
        title = book.get_metadata('DC', 'title')
        creator = book.get_metadata('DC', 'creator')

        # Start building markdown content
        markdown_content = []

        # Add book title and author if available
        if title:
            markdown_content.append(f"# {title[0][0]}\n")
        if creator:
            markdown_content.append(f"By {creator[0][0]}\n")

        # Process each document in the EPUB
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # Get content as bytes and decode to string
                html_content = item.get_content().decode('utf-8')

                # Parse HTML
                soup = BeautifulSoup(html_content, 'html.parser')

                # Extract chapter title if available
                chapter_title = soup.find(['h1', 'h2'])
                if chapter_title:
                    markdown_content.append(
                        f"\n## {chapter_title.get_text().strip()}\n")

                # Process all headings and paragraphs
                for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
                    tag_name = element.name
                    text = element.get_text().strip()

                    # Skip empty elements
                    if not text:
                        continue

                    # Format headings with appropriate markdown
                    if tag_name.startswith('h'):
                        level = int(tag_name[1])
                        # Ensure headings are properly nested
                        markdown_content.append(
                            f"\n{'#' * (level + 1)} {text}\n")
                    else:
                        # Regular paragraph
                        markdown_content.append(f"{text}\n\n")

        # Join all content and write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(''.join(markdown_content))

        return output_file

    except Exception as e:
        return f"Error processing EPUB: {str(e)}"


def clean_html(html_content):
    """
    Clean HTML content and extract only useful text.

    Args:
        html_content: HTML content as string

    Returns:
        str: Cleaned text
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()

    # Get text
    text = soup.get_text()

    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())

    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text
