import os
import tagging
import database


def get_suggestions():

    tag_ids = tagging.get_all_tag_ids()
    recomm_ids = []
    recomms = []
    file_ids = []
    tag_quantities = []
    i = 0
    counter = 0
    query_items = "SELECT pk_id FROM file"

    cursor = database.get_current_gallery("connection").cursor()
    cursor.execute(query_items)
    result = cursor.fetchall()

    for item in result:
        file_ids.append(item[0])

    for tag_id in tag_ids:
        for tempFile in file_ids:
            if tagging.file_has_tag_id(tempFile, tag_id):
                counter += 1
        tag_quantities.append([counter, tag_id])
        counter = 0

    if len(tag_ids) > 10:
        while i < 10:
            recomm_ids.append(max(tag_quantities)[1])
            tag_quantities.remove(max(tag_quantities))
            i += 1
        i = 0
    else:
        while i < len(tag_ids):
            recomm_ids.append(max(tag_quantities)[1])
            tag_quantities.remove(max(tag_quantities))
            i += 1
        i = 0

    for tag in recomm_ids:
        recomms.append(tagging.tag_id_to_name(tag))

    return recomms