from typing import Generator
from bs4 import BeautifulSoup, Tag, NavigableString

MAX_LEN = 4096
BLOCK_TAGS = {'p', 'b', 'strong', 'i', 'ul', 'ol', 'div', 'span'}

def split_message(source: str, max_len=MAX_LEN) -> Generator[str, None, None]:
    soup = BeautifulSoup(source, 'html.parser')
    fragments = []
    current_fragment = ''
    open_tags = []

    def process_node(node):
        nonlocal current_fragment, open_tags, fragments

        if isinstance(node, NavigableString):
            text = str(node)
            idx = 0
            while idx < len(text):
                #вычисляем оставшееся место с закрывающими тегами
                closing_tags = ''.join(f'</{tag}>' for tag in reversed(open_tags))
                space_left = max_len - len(current_fragment) - len(closing_tags)
                if space_left <= 0:
                    #места нет, значит закрываем фрагмент
                    fragments.append(current_fragment + closing_tags)
                    #начинаем новый фрагмент
                    current_fragment = ''.join(f'<{tag}>' for tag in open_tags)
                    continue 
                chunk = text[idx:idx+space_left]
                current_fragment += chunk
                idx += len(chunk)
        elif isinstance(node, Tag):
            if node.name in BLOCK_TAGS:
                attrs = ''.join(f' {k}="{v}"' for k, v in node.attrs.items())
                start_tag = f"<{node.name}{attrs}>"
                end_tag = f'</{node.name}>'
                
                closing_tags = ''.join(f'</{tag}>' for tag in reversed(open_tags))
                potential_length = len(current_fragment) + len(start_tag) + len(end_tag) + len(closing_tags)
                if potential_length > max_len:
                    #места нет, значит закрываем фрагмент
                    fragments.append(current_fragment + closing_tags)
                    
                    #начинаем новый фрагмент
                    current_fragment = ''.join(f'<{tag}>' for tag in open_tags)
                    
                    closing_tags = ''.join(f'</{tag}>' for tag in reversed(open_tags))
                    potential_length = len(current_fragment) + len(start_tag) + len(end_tag) + len(closing_tags)
                    if potential_length > max_len and not node.contents:
                        #если даже пустой тег не помещается делаем исключение
                        raise ValueError("Block Element too long", current_fragment+closing_tags, len(current_fragment+closing_tags))

                current_fragment += start_tag
                open_tags.append(node.name)
        
                for child in node.contents:
                    process_node(child)
                    
                
                closing_tags = ''.join(f'</{tag}>' for tag in reversed(open_tags))
                if len(current_fragment) + len(end_tag) + len(closing_tags) > max_len:
                    current_fragment += end_tag
                    open_tags.pop()
                    closing_tags = ''.join(f'</{tag}>' for tag in reversed(open_tags))
                   
                    fragments.append(current_fragment + closing_tags)
                    
                    current_fragment = ''.join(f'<{tag}>' for tag in open_tags)
                else:
                    current_fragment += end_tag
                    open_tags.pop()

            else:
                #добавление неблочных тегов(нельзя разрывать)
                full_tag_str = str(node)
                closing_tags = ''.join(f'</{tag}>' for tag in reversed(open_tags))
                if len(full_tag_str) > max_len:
                    raise ValueError("Non block tag text too long", node.name, full_tag_str, len(full_tag_str))
                if len(current_fragment) + len(full_tag_str) + len(closing_tags) > max_len:
                    fragments.append(current_fragment + closing_tags)
                    current_fragment = ''.join(f'<{tag}>' for tag in open_tags)
                    closing_tags = ''.join(f'</{tag}>' for tag in reversed(open_tags))
                    if len(full_tag_str) + len(current_fragment) + len(closing_tags) > max_len:
                        raise ValueError("Nonblock tag too long" ,node.name , current_fragment+full_tag_str+closing_tags, len(current_fragment+ full_tag_str+closing_tags))

                current_fragment += full_tag_str

    for child in soup.contents:
        process_node(child)

    if current_fragment:
        #закрываем все открытые теги 
        closing_tags = ''.join(f'</{tag}>' for tag in reversed(open_tags))
        fragments.append(current_fragment + closing_tags)

    for fragment in fragments:
        yield fragment

        
        
import click

@click.command()
@click.argument('input_file', type=click.File('r'))
@click.option('--max-len', default=4096, help='Максимальная длина фрагмента.')
def main(input_file, max_len):
    source = input_file.read()
    fragments = list(split_message(source, max_len=max_len))
    for idx, fragment in enumerate(fragments, 1):
        print(f"-- fragment #{idx}: {len(fragment)} chars --")
        print(fragment)
        print("\n")

if __name__ == '__main__':
    main()
