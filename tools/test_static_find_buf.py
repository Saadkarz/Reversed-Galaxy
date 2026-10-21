with open('src/RVL_SDK/bte/gki_buffer.c', 'r', encoding='utf-8') as f:
    text = f.read()

# Remove the if (0)
text = text.replace(
    '\n\tif (0) GKI_exception(0, "GKI_get_buf_start:: bad addr");',
    ''
)
text = text.replace(
    '\r\n\tif (0) GKI_exception(0, "GKI_get_buf_start:: bad addr");',
    ''
)

# Put static void *GKI_find_buf_start (NOT inline) before GKI_create_pool
fn = '''static void *GKI_find_buf_start(void *p_user_area)
{
	UINT16 xx;
	UINT16 size;
	UINT32 yy;
	tGKI_COM_CB *p_cb = &gki_cb.com;
	UINT8 *p_ua = p_user_area;

	for (xx = 0; xx < GKI_NUM_TOTAL_BUF_POOLS; ++xx)
	{
		if (p_ua > p_cb->pool_start[xx] && p_ua < p_cb->pool_end[xx])
		{
			yy = p_ua - p_cb->pool_start[xx];
			size = p_cb->pool_size[xx];

			yy = yy / size * size;

			return p_cb->pool_start[xx] + yy + sizeof(BUFFER_HDR_T);
		}
	}

	GKI_exception(GKI_ERROR_BUF_SIZE_ZERO, "GKI_get_buf_start:: bad addr");

	return NULL;
}

'''
if '\r\n' in text:
    fn = fn.replace('\n', '\r\n')

target = 'UINT8 GKI_create_pool('
idx = text.find(target)
text = text[:idx] + fn + text[idx:]

with open('src/RVL_SDK/bte/gki_buffer.c', 'w', encoding='utf-8') as f:
    f.write(text)
print('Added static GKI_find_buf_start without inline')
