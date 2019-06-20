import irbis.core as irbis

async def do_async_stuff():
    result = await connection.connect_async()
    if not result:
        print('Failed to connect')
        return

    print('Connected')

    maxMfn = await connection.get_max_mfn_async()
    print(f"Max MFN={maxMfn}");

    text = await connection.format_record_async('@brief', 1)
    print(text)

    await connection.nop_async()
    print("NOP")

    record = await connection.read_record_async(1)
    print(record)

    text = await connection.read_text_file_async('dn.mnu')
    print(text)

    count = await connection.search_count_async('K=бетон')
    print(f'Count={count}')

    found = await connection.search_async('K=бетон')
    print(found)

    await connection.disconnect_async()
    print('Disconnected')

#=============================================

connection = irbis.Connection()
connection.host = 'localhost'
connection.username = 'librarian'
connection.password = 'secret'
connection.database = 'IBIS'

irbis.init_async()

irbis.irbis_event_loop.run_until_complete(do_async_stuff())

irbis.close_async()
