import fitz  # PyMuPDF
import re

"""
ШИНЭЧЛЭЛ: 3 оронтой тоо унших чадвартай болсон.
"""

def line_checker(line):
    """
    Мөрүүд 3-аас бага оронтой тооны дараа текст орсон эсэхийг шалгана.
    """
    if not line.strip():
        return False

    line = line.strip()
    line = ' '.join(line.split())

    match = re.match(r'^\d{1,3}\s+\S+', line) # 1 -с 3 оронтой тоо шалгах 
    return bool(match)

def is_page_number(line):
    """
    Хуудасны дугаар биш үгүйг шалгана.
    """
    page_number_patterns = [
        r'^\s*\d+\s*$',       # Дан тооноос бүрдсэн мөр
        r'^\s*Page\s*\d+\s*$',  # Page гэсний дараа тоо орсон мөр
    ]

    for pattern in page_number_patterns:
        if re.match(pattern, line.strip(), re.IGNORECASE):
            return True
    return False

def format_text(text):
    """
    Үг хоорондын хоосон зайг байхгүй болгож үг болгоныг тустаа мөр болгож форматлах
    """
    formatted_lines = []
    for line in text.split('\n'):
        line = line.replace('\t', ' ')
        line = line.strip()
        line = ' '.join(line.split())
        formatted_lines.append(line)
    
    formatted_text = '\n'.join(formatted_lines)
    return formatted_text

def pdf_to_txt_without_indentation(pdf_file, txt_file):
    """
    PDF файлыг догол мөргүй болгож текст файл болгох. ChatGPT хийсэн.
    """
    pdf_document = fitz.open(pdf_file)
    
    footnotes = []
    citation_numbers = set()
    
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        blocks = page.get_text("blocks")  # Текст болок авах

        for block in blocks:
            x0, y0, x1, y1, text, block_no, block_type = block
            
            formatted_text = format_text(text)
            lines = formatted_text.split('\n')
            buffer_line = ""

            for line in lines:
                if line_checker(line) and not is_page_number(line):
                    # Эшлэлүүдийг гаргаж авах
                    match = re.match(r'^(\d{1,3})\s+', line) # 1 -с 3 оронтой тоо шалгах 
                    if match:
                        citation_number = int(match.group(1))
                        citation_numbers.add(citation_number)
                    
                    if buffer_line:
                        footnotes.append(buffer_line + '\n')  # Эхний зай авах мөр - padding
                    buffer_line = line
                else:
                    if buffer_line:
                        buffer_line += ' ' + line
            
            if buffer_line:
                footnotes.append(buffer_line + '\n')  # Төгсгөлийн зай авах мөр - padding
        
        footnotes.append('\n\n')  # Хуудас тусгаарлах
    
    return citation_numbers, footnotes

def check_missing_citations(citation_numbers):
    """
    Эшлэлүүдийн тоог тоолж дутуу тоог буцаах
    """
    
    if not any(number in citation_numbers for number in [1, 2, 3]):
        return "Эшлэл олдсонгүй.\n\n"
    
    max_number = max(citation_numbers)
    expected_numbers = set(range(1, max_number + 1))
    missing_numbers = sorted(expected_numbers - citation_numbers)
    
    if not missing_numbers:
        return "Бүх эшлэл бүртгэгдсэн.\n\n"
    
    missing_messages = [f"Дутуу эшлэл: {number}" for number in missing_numbers]
    return '\n'.join(missing_messages) + '\n\n'

def write_footnotes_with_messages(txt_file, footnotes, message):
    """
    Фүүтноот ба текст хувиргагч.
    """
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(message)
        f.writelines(footnotes)


pdf_file = 'testDoc.pdf' # Файлын нэр
txt_file = pdf_file[:-4] + '_output.txt'  # Үр дүнгийн нэр

# Эшлэл олж текст файл болгох
citation_numbers, footnotes = pdf_to_txt_without_indentation(pdf_file, txt_file)

# Дутуу эшлэлийн мэдээлэл
missing_citations_message = check_missing_citations(citation_numbers)

# Эшлэл ба дутуу эшлэлийн мэдээлэл текст болгох
write_footnotes_with_messages(txt_file, footnotes, missing_citations_message)
