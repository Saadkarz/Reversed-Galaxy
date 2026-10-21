with open('src/RVL_SDK/bte/gki_buffer.c', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('static void *GKI_find_buf_start')
idx_end = text.find('UINT8 GKI_create_pool(')
new_chunk = 'char gki_find_buf_start_str[] = "GKI_get_buf_start:: bad addr";\n\n'
if '\r\n' in text:
    new_chunk = new_chunk.replace('\n', '\r\n')

text = text[:idx] + new_chunk + text[idx_end:]

with open('src/RVL_SDK/bte/gki_buffer.c', 'w', encoding='utf-8') as f:
    f.write(text)
print('Replaced with global char array')
