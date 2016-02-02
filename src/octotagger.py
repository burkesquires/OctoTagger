#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import edit_output_folder
import create_output_folder
import edit_gallery_folder
import create_gallery_folder
import output
import settings
import about
import itemview
import contextpane
import database
import tagging
import new_database
import import_files
import expression
import taglist
import taggingview
import export
import os
import re

# import create_folders

# TODO: Many things don't work at all in Windows right now for some reason...


class MainWindow(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1280, 720))

        # Create_folders.create_folders()
        # Fix working directory
        if os.path.basename(os.getcwd()) == "src":
            os.chdir("..")

        # Modes: overview, tagging, import, folder
        self.mode = "overview"

        # Map of temporary files and tags, for import mode
        self.temp_file_tags = {}

        # A StatusBar in the bottom of the window
        self.CreateStatusBar()

        # Setting icon
        self.SetIcon(wx.Icon("icons/logo.ico", wx.BITMAP_TYPE_ICO))

        # Setting up the menus.
        self.filemenu = wx.Menu()
        toolmenu = wx.Menu()
        viewmenu = wx.Menu()
        helpmenu = wx.Menu()
        menu_open_database = self.get_gallery_menu()

        # FILEMENU
        fileNewDatabase = self.filemenu.Append(
            wx.ID_ANY,
            "&New database",
            " Create a new database",
        )
        self.filemenu.AppendMenu(wx.ID_ANY,
                                 "&Open gallery",
                                 menu_open_database,
                                 )

        self.filemenu.AppendSeparator()
        fileImportFiles = self.filemenu.Append(
            wx.ID_ANY,
            "&Start file import process...",
            "Start the import process of files and folders"
        )
        fileDirectImportFiles = self.filemenu.Append(
            wx.ID_ANY,
            "&Direct file import",
            "Import files directly, without going through the process"
        )
        item_create_gallery_folder = self.filemenu.Append(
            wx.ID_ANY,
            "&Create gallery folder",
            "Create another gallery folder"
        )
        item_create_output_folder = self.filemenu.Append(
            wx.ID_ANY,
            "&Create advanced output folder",
            "Dialog for editing a specific output folder"
        )
        self.filemenu.AppendSeparator()
        item_settings = self.filemenu.Append(
            wx.ID_ANY,
            "&Settings",
            "OctoTagger settings."
        )
        fileExit = self.filemenu.Append(
            wx.ID_EXIT, "&Exit", " Terminate the program")

        # TOOLMENU
        toolStartTaggingMode = toolmenu.Append(
            wx.ID_ANY,
            "&Start tagging mode",
            "Enter the tagging mode"
        )
        toolmenu.AppendSeparator()
        toolResetCurrentDatabase = toolmenu.Append(
            wx.ID_ANY,
            "&Reset current database",
            "Reset the current database"
        )
        tool_delete_database = toolmenu.Append(
            wx.ID_ANY,
            "&Delete current database",
            "Completely removes the current database."
        )
        toolmenu.AppendSeparator()
        toolRestoreAllFiles = toolmenu.Append(
            wx.ID_ANY,
            "&Restore all files",
            " Restores all Files"
        )

        # VIEWMENU
        viewShowAllFiles = viewmenu.Append(
            wx.ID_ANY,
            "&Show all files",
            " Shows every file"
        )
        viewShowTaggedFiles = viewmenu.Append(
            wx.ID_ANY,
            "&Show tagged files",
            " Shows the tagged files only"
        )
        viewShowUntaggedFiles = viewmenu.Append(
            wx.ID_ANY,
            "&Show untagged files",
            " Shows the untagged files only"
        )
        viewmenu.AppendSeparator()
        viewShowOutputFolders = viewmenu.Append(
            wx.ID_ANY,
            "&Show output folders",
            " Shows the output folders"
        )

        # HELPMENU
        helpManual = helpmenu.Append(
            6, "&User Manual", " How to use this program")
        item_about = helpmenu.Append(wx.ID_ANY, "&About", "About OctoTagger")

        # Creating the menubar
        menuBar = wx.MenuBar()
        # Adding the "filemenu" to the MenuBar
        menuBar.Append(self.filemenu, "&File")
        # Adding the "toolmenu" to the MenuBar
        menuBar.Append(toolmenu, "&Tools")
        # Adding the "viewmenu" to the MenuBar
        menuBar.Append(viewmenu, "&View")
        # Adding the "helpmenu" to the MenuBar
        menuBar.Append(helpmenu, "&Help")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Set events
        self.Bind(
            wx.EVT_MENU, self.on_start_folder_mode, viewShowOutputFolders)
        self.Bind(wx.EVT_MENU, self.start_overview, viewShowAllFiles)
        self.Bind(wx.EVT_MENU, self.on_show_tagged, viewShowTaggedFiles)
        self.Bind(wx.EVT_MENU, self.on_show_untagged, viewShowUntaggedFiles)
        self.Bind(wx.EVT_MENU, self.on_new_database, fileNewDatabase)
        self.Bind(wx.EVT_MENU, self.on_reset, toolResetCurrentDatabase)
        self.Bind(wx.EVT_MENU, self.OnRestoreAllFiles, toolRestoreAllFiles)
        self.Bind(wx.EVT_MENU, self.on_delete, tool_delete_database)
        self.Bind(wx.EVT_MENU, self.on_start_import, fileImportFiles)
        self.Bind(wx.EVT_MENU, self.on_direct_import, fileDirectImportFiles)
        self.Bind(wx.EVT_MENU, self.OnManual, helpManual)
        self.Bind(wx.EVT_MENU, self.OnExit, fileExit)

        self.Bind(
            wx.EVT_MENU,
            self.OnCreateGalleryFolder,
            item_create_gallery_folder,
        )
        self.Bind(
            wx.EVT_MENU,
            self.OnCreateOutputFolder,
            item_create_output_folder,
        )

        self.Bind(wx.EVT_MENU, self.OnSettings, item_settings)
        self.Bind(wx.EVT_MENU, self.OnAbout, item_about)

        self.Bind(
            wx.EVT_MENU,
            self.start_tagging_mode,
            toolStartTaggingMode,
        )

        self.Bind(wx.EVT_CHAR_HOOK, self.OnKey)

        self.Bind(
            itemview.EVT_SELECTION_CHANGE,
            self.on_selection_change,
        )

        # Tag and Context Pane

        self.mainPan = itemview.ItemView(self)
        self.Bind(itemview.EVT_ITEM_DOUBLE_CLICK, self.on_double_click_item)
        self.Bind(itemview.EVT_ITEM_RIGHT_CLICK, self.on_right_click_item)

        self.main_box = wx.BoxSizer(wx.HORIZONTAL)
        left_panel = wx.Panel(self, size=(300, -1), name="left_panel")
        left_panel_sz = wx.BoxSizer(wx.VERTICAL)
        left_panel.SetSizer(left_panel_sz)

        tag_panel = wx.Panel(left_panel, name="tag_panel")
        tag_panel_sz = wx.BoxSizer(wx.VERTICAL)
        tag_panel.SetSizer(tag_panel_sz)

        query_field_panel = wx.Panel(
            tag_panel,
            size=(-1, 50),
            name="query_field_panel",
        )
        query_field_panel_sz = wx.BoxSizer(wx.HORIZONTAL)
        query_field_panel.SetSizer(query_field_panel_sz)

        tag_list_panel = wx.Panel(tag_panel)
        tag_list_panel_sz = wx.BoxSizer(wx.VERTICAL)
        tag_list_panel.SetSizer(tag_list_panel_sz)

        tag_panel_sz.Add(query_field_panel, 0, wx.EXPAND | wx.ALIGN_CENTER)
        tag_panel_sz.Add(tag_list_panel, 1, wx.EXPAND)

        self.query_field = wx.TextCtrl(
            query_field_panel,
            -1,
            "",
            style=wx.TE_PROCESS_ENTER
        )

        self.Bind(
            wx.EVT_TEXT,
            self.on_query_text,
            self.query_field,
        )

        self.Bind(
            wx.EVT_MAXIMIZE,
            self.OnMaximize,
        )

        self.Bind(
            wx.EVT_TEXT_ENTER,
            self.on_query_text_enter,
            self.query_field,
        )

        query_field_panel_sz.Add(
            self.query_field,
            1,
            wx.LEFT | wx.RIGHT | wx.UP,
            20)

        # Add Topbar
        topbar_sz = wx.BoxSizer(wx.HORIZONTAL)
        self.topbar = wx.Panel(self.mainPan)
        self.topbar.SetSizer(topbar_sz)

        self.current_directory = wx.StaticText(
            self.topbar,
            label="",
            style=(
                wx.ALIGN_CENTRE_HORIZONTAL |
                wx.ST_ELLIPSIZE_END |
                wx.ST_NO_AUTORESIZE |
                wx.SIMPLE_BORDER
            )
        )

        self.btn_up = wx.Button(self.topbar, -1, "^")
        self.btn_up.Bind(wx.EVT_BUTTON, self.ChangeFolderUp)
        self.btn_up.Disable()

        topbar_sz.Add(self.btn_up, 0, wx.EXPAND)
        topbar_sz.Add(self.current_directory, 1, wx.EXPAND | wx.ALIGN_CENTER)

        self.mainPan.mainsizer.Insert(0, self.topbar, 0, wx.EXPAND)
        self.topbar.Show(False)

        self.cpane = contextpane.ContextPane(self, size=(-1, 200))

        left_panel_sz.Add(tag_panel, 1, wx.EXPAND)
        left_panel_sz.Add(
            self.cpane,
            0,
            flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
            border=15,
        )

        self.main_box.Add(left_panel, 0, wx.EXPAND)
        self.main_box.Add(self.mainPan, 1, wx.EXPAND)

        # Tag Pane

        self.lb_pan = tag_list_panel
        self.lb_sz = tag_list_panel_sz
        self.update_tag_list()

        self.SetSizer(self.main_box)
        self.Layout()
        self.Show(True)

        self.start_overview()

    def on_start_import(self, e):
        dlg_import = wx.DirDialog(
            self,
            "Select the folder containing the "
            "files you want to import",
            style=wx.DD_DIR_MUST_EXIST | wx.DD_DEFAULT_STYLE)

        if dlg_import.ShowModal() == wx.ID_CANCEL:
            print "Import process aborted."
            return

        if self.mode == "tagging":
            self.mode = "import"
            self.on_resume_overview_mode()
        else:
            self.mode = "import"

        # Set Items
        self.import_path = dlg_import.GetPath()
        self.InitImportFiles(self.import_path)

        items = self.GetFolderItems(self.import_path, True)
        self.InitImportFiles(self.import_path)
        self.mainPan.SetItems(items)

        self.current_directory.SetLabelText(self.import_path)
        self.topbar.Show(True)

        self.mainPan.Layout()
        self.mainPan.Refresh()

        self.cpane.SetMode("import")
        self.update_tag_list()
        self.Layout()

    def InitImportFiles(self, path):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                self.temp_file_tags[file_path] = []

            for dir in dirs:
                dir_path = os.path.join(root, dir)
                self.temp_file_tags[dir_path] = []

    def GetFolderItems(self, path, isRoot=False):
        items = []
        folders = []
        files = []

        for item in os.listdir(path):
            try:
                item = os.path.join(path, item).encode('utf-8')
            except:
                print "Could not decode file name with utf-8"
                item = os.path.join(path, item)

            if item not in self.temp_file_tags:
                print item, " is removed from import."
            elif os.path.isfile(item):
                files.append(item)
            elif os.path.isdir(item):
                folders.append(item)

        for folder in folders:
            # if not isRoot:
            #    item = os.path.join(path, folder)
            items.append(folder)

        for file in files:
            # if not isRoot:
            #    item = os.path.join(path, file)
            items.append(file)

        return items

    def CancelImportWarning(self):
        dlg_cancel = wx.MessageBox(
            'Do you really want to exit the import process? '
            'All your progress will be lost. '
            'The tags you have already assigned will not be saved, '
            'and nothing will be imported.\n',
            'In order to save your progress, please import beforehand. '
            'Click "Ok" to continue, and "Cancel" to return.'
            'Warning',
            wx.CANCEL | wx.OK | wx.CANCEL_DEFAULT | wx.ICON_WARNING
        )

        return dlg_cancel == wx.OK

    def on_direct_import(self, e):
        if self.mode == "import":
            if not self.CancelImportWarning():
                return

        dlg_import = wx.FileDialog(self, "Import files", "", "",
                                   "All files (*.*)|*.*",
                                   wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST)

        if dlg_import.ShowModal() == wx.ID_CANCEL:
            print "Import aborted."
        else:
            import_files.import_files(dlg_import.GetPaths())
            self.start_overview(False)

    def on_start_folder_mode(self, e=None):
        if self.mode == "import":
            if not self.CancelImportWarning():
                return

        self.mode = "folder"

        # Set items to all current database items
        # Get gallery connection

        gallery_conn = database.get_current_gallery("connection")
        cursor = gallery_conn.cursor()

        query_gallery_folders = (
            "SELECT pk_id, location, name FROM gallery_folder"
        )
        query_special_folders = "SELECT pk_id, location, name FROM folder"

        cursor.execute(query_gallery_folders)
        gallery_folder_result = cursor.fetchall()

        cursor.execute(query_special_folders)
        special_folder_result = cursor.fetchall()

        folders = []

        for folder in gallery_folder_result:
            path = os.path.join(folder[1], folder[2])
            folders.append(path.encode('utf-8') + "|GALLERYFOLDER")

        for folder in special_folder_result:
            path = os.path.join(folder[1], folder[2])
            folders.append(path.encode('utf-8'))

        self.update_gallery_menu()
        self.lb.EnableAll(False)
        self.cpane.SetMode("folder")

        # Set items
        self.mainPan.SetItems(folders)
        self.Refresh()
        self.Layout()

    def on_show_tagged(self, e):
        self.mode = "overview"

        # Set items to all untagged files
        # Get gallery connection

        self.lb.EnableAll(True)

        gallery_conn = database.get_current_gallery("connection")
        cursor = gallery_conn.cursor()

        query_items = ("SELECT pk_id FROM file "
                       "WHERE pk_id IN "
                       "(select pk_fk_file_id FROM file_has_tag)")
        cursor.execute(query_items)
        result = cursor.fetchall()

        items = []

        for item in result:
            items.append(item[0])

        self.update_gallery_menu()

        # Set items
        self.mainPan.SetItems(items)
        self.Refresh()
        self.Layout()

    def on_show_untagged(self, e):
        self.mode = "overview"

        # Set items to all untagged files
        # Get gallery connection

        self.lb.EnableAll(True)

        gallery_conn = database.get_current_gallery("connection")
        cursor = gallery_conn.cursor()

        query_items = ("SELECT pk_id FROM file "
                       "WHERE pk_id NOT IN "
                       "(select pk_fk_file_id FROM file_has_tag)")
        cursor.execute(query_items)
        result = cursor.fetchall()

        items = []

        for item in result:
            items.append(item[0])

        self.update_gallery_menu()

        # Set items
        self.mainPan.SetItems(items)
        self.Refresh()
        self.Layout()

    def start_tagging_mode(self, e=None, start_file=None):
        self.mode = "tagging"

        self.items = self.mainPan.GetItems()
        self.selected_items = self.mainPan.GetSelectedItems()

        self.main_box.Remove(self.mainPan)
        self.mainPan.Destroy()

        if start_file:
            self.mainPan = taggingview.TaggingView(
                self, self.items, start_file)
        elif self.selected_items:
            start_file = self.selected_items[0]
            self.mainPan = taggingview.TaggingView(
                self, self.items, start_file)
        else:
            self.mainPan = taggingview.TaggingView(self, self.items)

        self.Bind(
            taggingview.EVT_EXIT_TAGGING_VIEW,
            self.on_resume_overview_mode,
        )
        self.Bind(
            taggingview.EVT_ITEM_CHANGE,
            self.on_selection_change,
        )

        self.main_box.Add(self.mainPan, 1, wx.EXPAND)

        self.cpane.SetMode("tagging")

        self.Layout()
        self.Refresh()
        self.mainPan.ReSize()

    def on_resume_overview_mode(self, event=None):

        self.main_box.Remove(self.mainPan)
        self.mainPan.Destroy()
        self.mainPan = itemview.ItemView(self)
        self.Bind(itemview.EVT_ITEM_DOUBLE_CLICK, self.on_double_click_item)
        self.Bind(itemview.EVT_ITEM_RIGHT_CLICK, self.on_right_click_item)
        self.main_box.Add(self.mainPan, 1, wx.EXPAND)
        self.update_tag_list()

        self.start_overview()

    def on_query_text(self, e):

        if self.mode == "overview":
            if self.mainPan.GetSelectedItems():
                return

            query_input = e.GetEventObject().GetValue()

            if query_input == "":
                self.start_overview()
                self.cpane.Remove("create_folder_from_expr")

            else:
                self.cpane.Insert("create_folder_from_expr")
                try:
                    query_files = ("SELECT pk_id FROM file WHERE %s" %
                                   (expression.parse(query_input)))

                    # Get file list
                    cursor = (
                        database.get_current_gallery("connection").cursor()
                    )

                    cursor.execute(query_files)
                    result = cursor.fetchall()

                    items = []

                    for item in result:
                        items.append(item[0])

                    self.mainPan.SetItems(items)
                    self.Layout()

                except:
                    # TODO: Print in statusbar
                    print "Invalid expression!"

    def on_query_text_enter(self, e):

        items = self.GetSelectedItems()
        tag = e.GetEventObject().GetValue()

        if not (items and tag):
            return

        if (not re.match('^' + expression.REG_TAG_NAME + '$', tag) or
                tag == "False"):
            wx.MessageBox(
                ("Invalid input! Tag names can only contain letters, "
                 "numbers and underscores (which will be displayed "
                 "as a sapce). They must start with a letter.\n"
                 "For further information, consult the user manual."),
                "Error",
                wx.OK,
            )
            return

        for item in items:
            if self.mode == "import":

                # Create tag if necessary
                tag_id = tagging.create_tag(tag)

                # Append id
                if tag_id not in self.temp_file_tags[item]:
                    self.temp_file_tags[item].append(tag_id)

            else:
                # FIXME tag not created if necessary?
                tagging.tag_file(item, tag)

        self.update_tag_list()
        self.select_tags()
        e.GetEventObject().Clear()

    def start_overview(self, e=None, warn_import=True):
        # Set items to all current database items
        # Get gallery connection

        if self.mode == "import":
            if warn_import:
                if not self.CancelImportWarning():
                    return
            self.topbar.Show(False)

        self.lb.EnableAll(True)
        self.mode = "overview"

        gallery_conn = database.get_current_gallery("connection")
        cursor = gallery_conn.cursor()

        query_items = "SELECT pk_id FROM file"
        cursor.execute(query_items)
        result = cursor.fetchall()

        items = []

        for item in result:
            items.append(item[0])

        self.update_gallery_menu()
        self.cpane.SetMode("overview")

        # Set items
        self.mainPan.SetItems(items)
        self.Refresh()
        self.Layout()

    def on_selection_change(self, event=None):

        selection = len(self.GetSelectedItems())
        if selection > 2:
            selection = 2
        self.cpane.SetMode(selection=selection)
        self.Refresh()
        self.Layout()
        self.select_tags()

    def select_tags(self):

        if self.mode == "folder":
            return

        else:
            items = self.GetSelectedItems()

        if self.mode == "import":
            item_tags = {}
            for item in items:

                if item not in self.temp_file_tags:
                    self.temp_file_tags[item] = []
                    item_tags[item] = []

                else:
                    tag_ids = self.temp_file_tags[item]
                    tag_names = []
                    for tag_id in tag_ids:
                        tag_names.append(tagging.tag_id_to_name(tag_id))

                    item_tags[item] = tag_names
        else:
            item_tags = {}
            for item in items:
                tag_ids = tagging.get_tags(item)
                tag_names = []
                for tag_id in tag_ids:
                    tag_names.append(tagging.tag_id_to_name(tag_id))

                item_tags[item] = tag_names

        self.lb.CheckAll(wx.CHK_UNCHECKED)

        checked = []
        undetermined = []

        for item in items:

            tags = item_tags[item]

            if not checked:
                for tag in tags:
                    checked.append(tag)

            else:
                scrapbook = []
                for tag in checked:
                    scrapbook.append(tag)

                for checked_tag in scrapbook:
                    if checked_tag not in tags:
                        checked.remove(checked_tag)
                        undetermined.append(checked_tag)

                for tag in tags:
                    if tag not in checked:
                        undetermined.append(tag)

        self.lb.SetCheckedStrings(checked)
        self.lb.SetUndeterminedStrings(undetermined)

    def GetSelectedItems(self, path=None):
        if self.mode == "import":
            items = []
            if path:
                folder_items = []
                children = os.listdir(path)
                for child in children:
                    item = os.path.join(path, child)
                    folder_items.append(item)
            else:
                folder_items = self.mainPan.GetSelectedItems()

            for item in folder_items:
                if os.path.isdir(item):
                    # print "Folder: ", item
                    items = items + self.GetSelectedItems(item)
                else:
                    # print "File: ", item
                    items.append(os.path.join(path, item))

            return items

        elif self.mode in ["overview", "folder"]:
            return self.mainPan.GetSelectedItems()

        elif self.mode == "tagging":
            return [self.mainPan.GetCurrentItem()]

    def ChangeFolder(self, path):
        self.current_directory.SetLabelText(path)
        if path == self.import_path:
            self.btn_up.Disable()
        else:
            self.btn_up.Enable()

        items = self.GetFolderItems(path)
        self.mainPan.SetItems(items)
        self.on_selection_change()
        self.Layout()

    def ChangeFolderUp(self, event=None):
        directory_txt = self.current_directory.GetLabelText()
        directory = os.path.normpath(directory_txt)
        if directory == self.import_path:
            return
        else:
            new_dir = os.path.dirname(directory)
            self.ChangeFolder(new_dir)

    def on_tag_selected(self, e):
        if self.mode in ["overview", "import"]:

            items = self.GetSelectedItems()
            tags = self.lb.GetStrings()
            checked_tags = self.lb.GetCheckedStrings()
            undetermined_tags = self.lb.GetUndeterminedStrings()

            if items:
                # Files are selected -> tag them
                for item in items:
                    if self.mode == "overview":
                        item_tags = tagging.get_tag_names(item)
                        for tag in tags:
                            if(tag not in item_tags and tag in checked_tags):
                                tagging.tag_file(item, tag)

                            elif(tag in item_tags and
                                 tag not in checked_tags and
                                    tag not in undetermined_tags):
                                tagging.untag_file(item, tag)
                    elif self.mode == "import":
                        # Convert ID's to names
                        item_tag_ids = self.temp_file_tags[item]
                        item_tags = []
                        for item_tag_id in item_tag_ids:
                            item_tags.append(
                                tagging.tag_id_to_name(item_tag_id)
                            )

                        for tag in tags:
                            # Convert tag name to ID
                            tag_id = tagging.tag_name_to_id(tag)

                            # If tag should be added
                            if(tag not in item_tags and tag in checked_tags):

                                self.temp_file_tags[item].append(tag_id)

                            # If tag should be removed
                            elif(tag in item_tags and
                                 tag not in checked_tags and
                                    tag not in undetermined_tags):

                                self.temp_file_tags[item].remove(tag_id)

            else:
                # No files are selected -> filter them
                query_input = " ".join(checked_tags)
                self.query_field.SetValue(query_input)

        elif self.mode == "tagging":
            item = self.mainPan.GetCurrentItem()
            tags = self.lb.GetStrings()
            checked_tags = self.lb.GetCheckedStrings()

            item_tags = tagging.get_tag_names(item)
            for tag in tags:
                if(tag not in item_tags and tag in checked_tags):
                    tagging.tag_file(item, tag)

                elif(tag in item_tags and tag not in checked_tags):
                    tagging.untag_file(item, tag)

    def update_tag_list(self, event=None):

        # Remove previous list

        self.lb_pan.DestroyChildren()

        tags = tagging.get_all_tags()

        self.lb = taglist.TagList(
            self.lb_pan,
            id=wx.ID_ANY,
            pos=(0, 0),
            size=(-1, -1),
            tags=tags,
        )

        self.lb_sz.Add(
            self.lb,
            1,
            wx.EXPAND | wx.ALL,
            20,
        )
        if event:
            self.lb.SetCheckedStrings(event.checked)
        self.Bind(taglist.EVT_TAGLIST_CHECK, self.on_tag_selected, self.lb)
        self.Bind(taglist.EVT_TAGLIST_UPDATE, self.update_tag_list, self.lb)
        self.Layout()
        self.Refresh()

    def get_gallery_menu(self):
        menu = wx.Menu()

        # Create list of galleries
        gallery_list = []

        # Get system connection

        sys_conn = database.get_sys_db()
        cursor = sys_conn.cursor()

        # Select galleries
        query_galleries = "SELECT pk_id, name FROM gallery"
        cursor.execute(query_galleries)
        result = cursor.fetchall()
        for gallery in result:
            gallery_list.append(gallery)

        # Open Database menu
        for gallery in gallery_list:
            item = wx.MenuItem(
                id=100 + gallery[0],
                text=gallery[1],
                help="Switch to database: " + gallery[1],
                kind=wx.ITEM_RADIO
            )
            menu.AppendItem(item)

        return menu

    def update_gallery_menu(self):

        menu_open_database = self.filemenu.FindItemByPosition(1)

        self.filemenu.DeleteItem(menu_open_database)
        menu_open_database = self.filemenu.InsertMenu(
            1,
            wx.ID_ANY,
            "Open gallery",
            self.get_gallery_menu(),
            "")

        # Check current gallery

        current_gallery = database.get_current_gallery("id")
        for gallery in menu_open_database.GetSubMenu().GetMenuItems():
            self.Bind(wx.EVT_MENU, self.on_switch_gallery, gallery)
            if gallery.GetId() - 100 == current_gallery:
                gallery.Check()

    def on_switch_gallery(self, e):
        gallery_id = e.GetId() - 100
        database.switch_gallery(gallery_id)
        self.start_overview()
        self.update_tag_list()

    def on_new_database(self, e):
        dlg = new_database.NewDatabase(self)
        dlg.ShowModal()
        self.start_overview()
        self.update_gallery_menu()
        self.update_tag_list()

    def on_reset(self, e):
        dlg_export = wx.MessageBox(
            (
                'This will remove all tags and output folders '
                'from the database \"%s\". Your files will remain. '
                'Do you want to continue?'
                % (database.get_current_gallery("name"))
            ),
            'Warning',
            wx.CANCEL | wx.OK | wx.CANCEL_DEFAULT | wx.ICON_WARNING
        )
        if dlg_export == 4:
            database.reset_gallery(database.get_current_gallery("id"))
            self.update_tag_list()

        elif dlg_export == 16:
            print "Canceled."

    def on_delete(self, e):
        dlg_clear = wx.MessageBox(
            (
                'Are you sure you want to remove the database \"%s\"? '
                'This will remove all data associated with the database.'
                % (database.get_current_gallery("name"))
            ),
            'Information',
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION
        )
        # If the user continues, ask if he wants to export his files.
        if dlg_clear == 2:
            dlg_export = wx.MessageBox(
                (
                    'Do you want to export your saved files? '
                    'Click "Yes" if you want to keep your files, '
                    'and "No" if you want to delete them. '
                    '\n\nWARNING: You will not be able to retrieve '
                    'your files again if you select "No"!'
                ),
                'Export saved files?',
                wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION
            )
            if dlg_export == 2:
                print "Export files now"
                self.OnRestoreAllFiles()

            # Delete everything now!
            database.delete_gallery(database.get_current_gallery("id"))
            if self.mode == "tagging":
                self.on_resume_overview_mode()

            self.update_gallery_menu()

        else:
            print "Aborted clearing of files"

    def OnManual(self, e):
        dlg = wx.MessageDialog(
            self,
            "OctoTagger is the best program and doesn't need any explanation!",
            "User Manual",
            wx.OK
        )
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self, e):
        if self.mode == "import":
            if self.CancelImportWarning():
                self.Close(True)
        else:
            self.Close(True)

    def OnCreateGalleryFolder(self, event=None):
        dlg = create_gallery_folder.CreateGalleryFolder(self)
        dlg.ShowModal()
        dlg.Destroy()

        if self.mode == "folder":
            self.on_start_folder_mode()

    def OnCreateOutputFolder(self, event=None):
        dlg = create_output_folder.CreateOutputFolder(self)
        dlg.ShowModal()
        dlg.Destroy()

        if self.mode == "folder":
            self.on_start_folder_mode()

    def OnSettings(self, e):
        dlg = settings.Settings(self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnMaximize(self, e):

        if self.mode == "tagging":
            self.Layout()
            self.mainPan.imgPan.Layout()
            self.mainPan.Layout()
            self.mainPan.Refresh()
            self.mainPan.ReSize()

    def OnAbout(self, e):
        wx.AboutBox(about.getInfo())

    # Key events

    def OnKey(self, e):
        if self.mode == "tagging":
            if e.GetKeyCode() == wx.WXK_RIGHT:
                self.mainPan.DisplayNext()
            elif e.GetKeyCode() == wx.WXK_LEFT:
                self.mainPan.DisplayPrev()
            elif e.GetKeyCode() == wx.WXK_ESCAPE:
                self.mainPan.OnExit()
            elif e.GetKeyCode() == wx.WXK_DELETE:
                self.RemoveItem()
            elif e.GetKeyCode() == wx.WXK_F2:
                self.RenameItem()
        elif self.mode in ["overview", "import", "folder"]:
            try:
                char = chr(e.GetKeyCode())
            except:
                char = None

            if char:
                if char == "A" and e.ControlDown():
                    if not self.mainPan.IsSelectedAll():
                        self.mainPan.SetSelectedAll(True)
                    else:
                        self.mainPan.SetSelectedAll(False)

                    self.select_tags()

            if e.GetKeyCode() == wx.WXK_DELETE:
                self.RemoveItem()
            elif e.GetKeyCode() == wx.WXK_F2:
                self.RenameItem()

        elif self.mode == "folder":
            if e.GetKeyCode() == wx.WXK_DELETE:
                self.RemoveItem()

        e.Skip()

    def on_double_click_item(self, e):
        if self.mode == "overview":
            item = e.item
            self.start_tagging_mode(item)

        elif self.mode == "import":
            item = e.item
            if os.path.isdir(item):
                self.ChangeFolder(item)
            else:
                # TODO (Optional): Implement tagging view?
                print "Not a folder"

        elif self.mode == "folder":
            self.EditFolder()

    def on_right_click_item(self, e):

        menu = wx.Menu()

        if self.mode == "folder":

            if e.item:
                self.mainPan.OnRightMouseUp(e.item, e.modifiers)

            items = self.GetSelectedItems()

            if len(items) == 0:
                item_add = menu.Append(
                    wx.ID_ANY,
                    "Add folder",
                    "Create a new folder."
                )
                self.Bind(wx.EVT_MENU, self.OnCreateOutputFolder, item_add)

            elif len(items) == 1:
                if e.item.IsGalleryFolder():
                    kind = "gallery"
                else:
                    kind = "custom"

                item_edit = menu.Append(
                    wx.ID_ANY,
                    "Edit",
                    ("Edit this " + kind + " folder.")
                )
                self.Bind(wx.EVT_MENU, self.EditFolder, item_edit)
                # OPTIONAL: Open in file manager option
                item_remove = menu.Append(
                    wx.ID_ANY,
                    "Remove",
                    ("Remove this " + kind + " folder from the "
                     "database (files remain untouched).")
                )
                self.Bind(wx.EVT_MENU, self.RemoveItem, item_remove)

            elif len(items) > 1:

                item_remove = menu.Append(
                    wx.ID_ANY,
                    "Remove",
                    "Remove the selected folders from the database (files remain untouched)."
                )
                self.Bind(wx.EVT_MENU, self.RemoveItem, item_remove)

        elif self.mode == "overview":

            if e.item:
                # Clicked an item

                self.mainPan.OnRightMouseUp(e.item, e.modifiers)
                items = self.mainPan.GetSelectedItems()

                if len(items) == 1:
                    item_rename = menu.Append(
                        wx.ID_ANY,
                        "Rename",
                        "Rename this files."
                    )
                    self.Bind(wx.EVT_MENU, self.RenameItem, item_rename)

                item_remove = menu.Append(
                    wx.ID_ANY,
                    "Delete",
                    "Delete the selected files (this can not be undone)."
                )
                self.Bind(wx.EVT_MENU, self.RemoveItem, item_remove)
                item_restore = menu.Append(
                    wx.ID_ANY,
                    "Restore",
                    "Remove the selected files from the database and move them to the desired location."
                )
                self.Bind(wx.EVT_MENU, self.RestoreSelected, item_restore)
            else:
                query = self.query_field.GetValue()
                if query != "":
                    item_create_folder = menu.Append(
                        wx.ID_ANY,
                        "Create folder from current expression",
                        "Create a special output folder from the current expression."
                    )
                    self.Bind(
                        wx.EVT_MENU, self.CreateFolderFromExpression, item_create_folder)

        elif self.mode == "tagging":

            item_rename = menu.Append(
                wx.ID_ANY,
                "Rename",
                "Rename this file."
            )
            self.Bind(wx.EVT_MENU, self.RenameItem, item_rename)
            item_remove = menu.Append(
                wx.ID_ANY,
                "Delete",
                "Delete this file (this can not be undone)."
            )
            self.Bind(wx.EVT_MENU, self.RemoveItem, item_remove)

            item_restore = menu.Append(
                wx.ID_ANY,
                "Restore",
                ("Remove this file from the database "
                 "and move it to the desired location.")
            )
            self.Bind(wx.EVT_MENU, self.RestoreSelected, item_restore)

        elif self.mode == "import":

            if e.item:
                self.mainPan.OnRightMouseUp(e.item, e.modifiers)

            items = self.mainPan.GetSelectedItems()

            if len(items) == 0:
                item_abort = menu.Append(
                    wx.ID_ANY,
                    "Abort import",
                    "Abort the import, all files remain where they are."
                )
                self.Bind(wx.EVT_MENU, self.start_overview, item_abort)
                item_import_all = menu.Append(
                    wx.ID_ANY,
                    "Import all",
                    "Import all files."
                )
                self.Bind(wx.EVT_MENU, self.ImportAll, item_import_all)
                item_import_tagged = menu.Append(
                    wx.ID_ANY,
                    "Import tagged",
                    "Import all files that have at least one tag assigned."
                )
                self.Bind(wx.EVT_MENU, self.ImportTagged, item_import_tagged)

            elif len(items) >= 1:
                item_remove = menu.Append(
                    wx.ID_ANY,
                    "Remove from import",
                    "Remove the selected items from the import "
                    "(they remain where they are)."
                )
                self.Bind(wx.EVT_MENU, self.RemoveItem, item_remove)

        if menu.GetMenuItemCount() > 0:
            self.PopupMenu(menu, self.ScreenToClient(wx.GetMousePosition()))

    def CreateFolderFromExpression(self, event):
        query = self.query_field.GetValue()

        dlg = create_output_folder.CreateOutputFolder(self, expr=query)
        dlg.ShowModal()
        dlg.Destroy()

    def ImportAll(self, event):
        import_files.import_files(self.temp_file_tags)

    def ImportTagged(self, event):

        tagged_files = {}
        for item, tags in self.temp_file_tags.iteritems():
            if len(tags) > 0:
                tagged_files[item] = tags

        import_files.import_files(tagged_files)

        self.start_overview(warn_import=False)

    def EditFolder(self, event=None):
        if not self.mode == "folder":
            return

        items = self.mainPan.GetSelectedItems()
        if len(items) != 1:
            print "Can not edit more than one folder at once."
            return

        for child in self.mainPan.GetChildren():
            if child is not self.topbar and child.GetPath() == items[0]:
                is_gf = child.IsGalleryFolder()

        if is_gf:
            folder = tagging.gallery_path_to_id(items[0])
            dlg = edit_gallery_folder.EditGalleryFolder(self, folder)
        else:
            folder = tagging.advanced_path_to_id(items[0])
            dlg = edit_output_folder.EditOutputFolder(self, folder)

        dlg.ShowModal()
        dlg.Destroy()

        self.on_start_folder_mode()

    def RenameItem(self, event=None):

        if self.mode == "tagging":
            old_name = self.mainPan.GetName()
        else:
            item = self.GetSelectedItems()[0]
            for child in self.mainPan.GetChildren():
                if child is not self.topbar and child.GetPath() == item:
                    old_name = child.GetText()

        if not old_name:
            return
        dlg = wx.TextEntryDialog(
            self,
            "Enter a new name:",
            defaultValue=old_name,
        )
        dlg.ShowModal()
        new_name = dlg.GetValue()
        output.rename_file(self.GetSelectedItems()[0], new_name)

        if self.mode == "overview":
            self.start_overview()

    def RestoreFiles(self, files, event=None):

        # Ask for target directory
        dlg_import = wx.DirDialog(
            self,
            "Select the location where you want to move "
            "files to.",
            style=wx.DD_DEFAULT_STYLE)

        if dlg_import.ShowModal() == wx.ID_CANCEL:
            # Restoration aborted
            return "ABORT"

        target_dir = dlg_import.GetPath()

        # Restore the files
        export.file(files, target_dir, move=True)

        self.select_tags()

        if self.mode == "overview":
            self.start_overview()

        dlg_complete = wx.MessageDialog(
            self,
            "Restoration complete.",
            "Message",
            wx.OK
        )
        dlg_complete.ShowModal()
        dlg_complete.Destroy()

    def OnRestoreAllFiles(self, event=None):

        # Get all file IDs
        gallery_conn = database.get_current_gallery("connection")
        c = gallery_conn.cursor()

        query_ids = "SELECT pk_id FROM file"
        c.execute(query_ids)
        result = c.fetchall()

        ids = []
        for id in result:
            ids.append(id[0])

        # Restore
        self.RestoreFiles(ids)

    def RestoreSelected(self, event=None):

        item = self.GetSelectedItems()
        self.RestoreFiles(item)

        if self.mode == "tagging":
            self.mainPan.RemoveItem(item[0])

    def RemoveItem(self, event=None):
        if self.mode == "folder":
            items = self.mainPan.GetSelectedItems()
            advanced_ids = []
            gallery_ids = []

            for item in items:
                obj = self.mainPan.GetItemFromPath(item)
                if obj.IsGalleryFolder():
                    gallery_ids.append(str(tagging.gallery_path_to_id(item)))
                else:
                    advanced_ids.append(str(tagging.advanced_path_to_id(item)))

            # Delete folders

            gallery = database.get_current_gallery("connection")
            cursor = gallery.cursor()

            for gallery_id in gallery_ids:
                output.delete_gallery(gallery_id)

            for advanced_id in advanced_ids:
                output.delete_folder(advanced_id)

            self.on_start_folder_mode()

        elif self.mode == "overview":

            items = self.mainPan.GetSelectedItems()
            ids = []

            for item in items:
                ids.append(str(item))

            # TODO: Confirmation?
            # Delete files

            for item in items:
                output.remove(item)

            gallery = database.get_current_gallery("connection")
            cursor = gallery.cursor()

            query_files = (
                "DELETE FROM file WHERE pk_id IN (%s)"
                % ", ".join(ids)
            )
            query_tags = (
                "DELETE FROM file_has_tag WHERE pk_fk_file_id IN (%s)"
                % ", ".join(ids)
            )
            cursor.execute(query_files)
            cursor.execute(query_tags)
            gallery.commit()

            self.select_tags()
            self.start_overview()

        elif self.mode == "tagging":

            item = self.mainPan.GetCurrentItem()

            # TODO: Confirmation?
            # Delete files

            self.mainPan.RemoveItem(item)
            output.remove(item)

            gallery = database.get_current_gallery("connection")
            cursor = gallery.cursor()

            query_files = (
                "DELETE FROM file WHERE pk_id = %d"
                % item
            )
            query_tags = (
                "DELETE FROM file_has_tag WHERE pk_fk_file_id = %d"
                % item
            )
            cursor.execute(query_files)
            cursor.execute(query_tags)
            gallery.commit()

        elif self.mode == "import":

            # Get items to be removed
            sel_items = self.mainPan.GetSelectedItems()
            for item in sel_items:

                # Delete all children if a folder is removed
                if os.path.isdir(item):
                    for root, dirs, files in os.walk(item):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                del self.temp_file_tags[file_path]
                            except:
                                print "Item already removed"

                # Remove the item itself
                try:
                    del self.temp_file_tags[item]
                except:
                    print "Error removing item"

            # Update the import view
            current_dir = self.current_directory.GetLabelText()
            items = self.GetFolderItems(current_dir)
            self.mainPan.SetItems(items)
            self.select_tags()
            self.Layout()

app = wx.App(False)
frame = MainWindow(None, "OctoTagger")
# import wx.lib.inspection
# wx.lib.inspection.InspectionTool().Show()
app.MainLoop()
