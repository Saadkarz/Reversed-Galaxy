with open('src/RVL_SDK/bte/gki_ppc.c', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. wrap GKI_create_task
text = text.replace(
    'UINT8 GKI_create_task(TASKPTR task_entry',
    '#if 0\nUINT8 GKI_create_task(TASKPTR task_entry'
)
text = text.replace(
    '    return GKI_SUCCESS;\n}\n\nvoid GKI_run(',
    '    return GKI_SUCCESS;\n}\n#endif\n\nvoid GKI_run('
)

# 2. wrap GKI_suspend_task, GKI_resume_task, GKI_exit_task
text = text.replace(
    'UINT8 GKI_suspend_task(UINT8 task_id)',
    '#if 0\nUINT8 GKI_suspend_task(UINT8 task_id)'
)
text = text.replace(
    '    GKI_enable();\n}\n\nvoid GKI_sched_lock(',
    '    GKI_enable();\n}\n#endif\n\nvoid GKI_sched_lock('
)

# 3. wrap GKI_wait
text = text.replace(
    'UINT16 GKI_wait(UINT16 flag, UINT32 timeout)',
    '#if 0\nUINT16 GKI_wait(UINT16 flag, UINT32 timeout)'
)
text = text.replace(
    '    return evt;\n}\n\nvoid GKI_delay(',
    '    return evt;\n}\n#endif\n\nvoid GKI_delay('
)

# 4. wrap GKI_isend_event
text = text.replace(
    'UINT8 GKI_isend_event(UINT8 task_id, UINT16 event)',
    '#if 0\nUINT8 GKI_isend_event(UINT8 task_id, UINT16 event)'
)
text = text.replace(
    '    return GKI_SUCCESS;\n}\n\nUINT8 GKI_get_taskid(',
    '    return GKI_SUCCESS;\n}\n#endif\n\nUINT8 GKI_get_taskid('
)

# 5. wrap GKI_map_taskname
text = text.replace(
    'INT8* GKI_map_taskname(UINT8 task_id)',
    '#if 0\nINT8* GKI_map_taskname(UINT8 task_id)'
)
text = text.replace(
    '    return (INT8*)"BAD";\n}\n\nvoid GKI_enable(',
    '    return (INT8*)"BAD";\n}\n#endif\n\nvoid GKI_enable('
)

# 6. wrap GKI_get_time_stamp and GKI_register_mempool
text = text.replace(
    'INT8* GKI_get_time_stamp(INT8* tbuf)',
    '#if 0\nINT8* GKI_get_time_stamp(INT8* tbuf)'
)
text = text.replace(
    '    gki_cb.com.p_user_mempool = p_mem;\n}\n\nvoid* GKI_os_malloc(',
    '    gki_cb.com.p_user_mempool = p_mem;\n}\n#endif\n\nvoid* GKI_os_malloc('
)

with open('src/RVL_SDK/bte/gki_ppc.c', 'w', encoding='utf-8') as f:
    f.write(text)
print('Updated gki_ppc.c successfully')
