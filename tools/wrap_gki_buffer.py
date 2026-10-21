with open('src/RVL_SDK/bte/gki_buffer.c', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Make GKI_set_pool_permission static inline
text = text.replace(
    'UINT8 GKI_set_pool_permission(UINT8 pool_id, UINT8 permission)',
    'static inline UINT8 GKI_set_pool_permission(UINT8 pool_id, UINT8 permission)'
)

# 2. Wrap GKI_igetpoolbuf in #if 0
text = text.replace(
    'void *GKI_igetpoolbuf(UINT8 pool_id)',
    '#if 0\nvoid *GKI_igetpoolbuf(UINT8 pool_id)'
)
text = text.replace(
    '	return p_hdr + 1;\n}\n\nvoid GKI_freebuf(',
    '	return p_hdr + 1;\n}\n#endif\n\nvoid GKI_freebuf('
)

# 3. Cut gki_chk_buf_damage and put it as static inline above GKI_freebuf
chk_fn = '''BOOLEAN gki_chk_buf_damage(void *p_buf)
{
	UINT32 *magic = (UINT32 *)((UINT8 *)p_buf + GKI_get_buf_size(p_buf));

	if ((UINT32)magic & 1)
		return TRUE;

	if (*magic == MAGIC_NO)
		return FALSE;

	return TRUE;
}
'''
static_chk_fn = '''static inline BOOLEAN gki_chk_buf_damage(void *p_buf)
{
	UINT32 *magic = (UINT32 *)((UINT8 *)p_buf + GKI_get_buf_size(p_buf));

	if ((UINT32)magic & 1)
		return TRUE;

	if (*magic == MAGIC_NO)
		return FALSE;

	return TRUE;
}

'''
if '\r\n' in text:
    chk_fn = chk_fn.replace('\n', '\r\n')
    static_chk_fn = static_chk_fn.replace('\n', '\r\n')

assert chk_fn in text, "chk_fn not found"
text = text.replace(chk_fn, '')
text = text.replace('void GKI_freebuf(void *p_buf)', static_chk_fn + 'void GKI_freebuf(void *p_buf)')

# 4. Wrap GKI_poolfreecount and GKI_change_buf_owner in #if 0
text = text.replace(
    'UINT16 GKI_poolfreecount(UINT8 pool_id)',
    '#if 0\nUINT16 GKI_poolfreecount(UINT8 pool_id)'
)
text = text.replace(
    '	p_hdr->task_id = task_id;\n}\n\nvoid GKI_send_msg(',
    '	p_hdr->task_id = task_id;\n}\n#endif\n\nvoid GKI_send_msg('
)

# 5. Wrap GKI_find_buf_start in #if 0
text = text.replace(
    'void *GKI_find_buf_start(void *p_user_area)',
    '#if 0\nvoid *GKI_find_buf_start(void *p_user_area)'
)
text = text.replace(
    '	return (void *)xx;\n}\n\nUINT8 GKI_create_pool(',
    '	return (void *)xx;\n}\n#endif\n\nUINT8 GKI_create_pool('
)

with open('src/RVL_SDK/bte/gki_buffer.c', 'w', encoding='utf-8') as f:
    f.write(text)
print('Updated gki_buffer.c successfully')
