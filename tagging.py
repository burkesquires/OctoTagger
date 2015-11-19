#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Functionality for assigning tags to imported files.
'''

import os
import sqlite3
import database

# Methods for assigning tags to files

def tag_file(file_id, tag_name, amount=-1):
    # Get gallery connection
    gallery = database.get_current_gallery("connection")
    cursor = gallery.cursor()

    # Try to find existing tag
    query_get_tags = "SELECT * FROM tag WHERE name = \'%s\'" % (tag_name)
    cursor.execute(query_get_tags)
    tags = cursor.fetchall()
    if tags:
        # Tag has been found
        for tag in tags:
            tag_id = tag[0]
            query_link = "INSERT INTO file_has_tag(pk_fk_file_id, pk_fk_tag_id, amount) VALUES (%d, %d, %d)" % (file_id, tag_id, amount)
            cursor.execute(query_link)
    else:
        # Tag has not been found, create it

        # If an amount has been specified, make tag numeric
        if amount > -1:
            is_numeric = 1
        else:
            is_numeric = 0

        query_insert_tag = "INSERT INTO tag(name, is_numeric) VALUES (\'%s\', %d)" % (tag_name, is_numeric)
        cursor.execute(query_insert_tag)

        # Get ID of newly created tag and create link between it and the file
        query_get_tags = "SELECT * FROM tag WHERE name = \'%s\'" % (tag_name)
        cursor.execute(query_get_tags)
        tags = cursor.fetchall()
        for tag in tags:
            tag_id = tag[0]
            query_link = "INSERT INTO file_has_tag(pk_fk_file_id, pk_fk_tag_id, amount) VALUES (%d, %d, %d)" % (file_id, tag_id, amount)
            cursor.execute(query_link)

    # Write changes
    gallery.commit()

def tag_files(file_ids, tag_name, amount=-1):
    for file_id in file_ids:
        tag_file(file_id, tag_name, amount)


# Methods for analyzing assigned tags


def file_has_tag_id(file_id, tag_id):
    tags = get_tags(file_id)
    if tag_id in tags:
        return True
    else:
        return False

def file_has_tag(file_id, tag_name):
    tag_id = tag_name_to_id(tag_name)
    return file_has_tag_id(file_id, tag_id)

def get_tags(file_id):
    # Get gallery connection
    gallery = database.get_current_gallery("connection")
    cursor = gallery.cursor()

    tags = []
    query_get_tags = "SELECT pk_fk_tag_id FROM file_has_tag WHERE pk_fk_file_id = %d" % (file_id)
    cursor.execute(query_get_tags)
    result = cursor.fetchall()
    for tag in result:
        tags.append(tag[0])

    gallery.commit()
    return tags

def tag_id_to_name(tag_id):
    # Get gallery connection
    gallery = database.get_current_gallery("connection")
    cursor = gallery.cursor()

    query_get_tags = "SELECT name FROM tag WHERE pk_id = %d" % (tag_id)
    cursor.execute(query_get_tags)
    tags = cursor.fetchall()
    gallery.commit()
    if tags:
        for tag in tags:
            return tag[0]
    else:
        return False

def tag_name_to_id(tag_name):
    # Get gallery connection
    gallery = database.get_current_gallery("connection")
    cursor = gallery.cursor()

    query_get_tags = "SELECT pk_id FROM tag WHERE name = \'%s\'" % (tag_name)
    cursor.execute(query_get_tags)
    tags = cursor.fetchall()
    gallery.commit()
    if tags:
        for tag in tags:
            return tag[0]
    else:
        return False

def get_all_tag_ids():
    # Get gallery connection
    gallery = database.get_current_gallery("connection")
    cursor = gallery.cursor()

    tag_ids = []
    query_get_tags = "SELECT pk_id FROM tag"
    cursor.execute(query_get_tags)
    tags = cursor.fetchall()
    for tag in tags:
        tag_ids.append(tag[0])

    gallery.commit()
    return tag_ids

def get_all_tags():
    # Get gallery connection
    gallery = database.get_current_gallery("connection")
    cursor = gallery.cursor()

    tag_names = []
    query_get_tags = "SELECT name FROM tag"
    cursor.execute(query_get_tags)
    tags = cursor.fetchall()
    for tag in tags:
        tag_names.append(tag[0])

    gallery.commit()
    return tag_names