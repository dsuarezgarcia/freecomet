# -*- encoding: utf-8 -*-

'''
    The listview module.
'''


# PyGObject imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

 
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	ListView                                                                  #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class ListView(object):

    '''
        The ListView abstract class. Item lists with graphic rendering should 
        inherit this class. 
    '''

    ''' Initialization method. '''
    def __init__(self, treeview):

        self.__treeview = treeview


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                 Methods                                     #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Returns the model. '''
    def get_model(self):
        return self.__treeview.get_model()

    ''' Sets the model. '''
    def set_model(self, model):
        self.__treeview.set_model(model)

    ''' Clears the model. '''
    def clear_model(self):
        self.__treeview.get_model().clear()

    ''' Returns the item's ID at given position. '''
    def get_item_id(self, pos):
        return self.__treeview.get_model()[pos][0]

    ''' Returns the row of the item that matches given ID. '''
    def get_row(self, id):

        row = 0
        while row < len(self.__treeview.get_model()):
            if self.__treeview.get_model()[row][0] == id:
                return row
            row += 1

    ''' Adds a new item to the store at given position if exists. '''
    def add_item(self, item, pos):

        if pos is None:
            self.__treeview.get_model().append(item)
        else:
            self.__treeview.get_model().insert(pos, item)

    ''' Deletes the item from the model with given ID. '''
    def delete_item(self, id):

        pos = 0
        deleted = False

        treeiter = self.__treeview.get_model().get_iter_first()
        while treeiter is not None and not deleted:

            if self.__treeview.get_model()[treeiter][0] == id:         
                self.__treeview.get_model().remove(treeiter)
                deleted = True

            else:
                treeiter = self.__treeview.get_model().iter_next(treeiter)
                pos += 1

        # Return the position where the item was
        return pos

    ''' Treeview grabs the focus and sets the cursor on given row. '''
    def focus_row(self, row):
       
        # Focus grabbed
        self.__treeview.grab_focus()
        # Set curor to given row
        self.__treeview.set_cursor(row)

    ''' Returns the selected TreeView row. '''
    def get_selected_row(self):
        return self.__treeview.get_cursor()[0].get_indices()[0]


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                            Getters and Setters                              #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_treeview(self):
        return self.__treeview

    def set_treeview(self, treeview):
        self.__treeview = treeview


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	SamplesView                                                               #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class SamplesView(ListView):

    '''
        The SamplesView class. The samples view of the application. Stores the
        identifier, name and the number of comets for each sample. 
    '''

    SORT_ASCENDING = 0
    SORT_DESCENDING = 1

    ARROW_DOWN_ICON = "pan-down-symbolic"
    ARROW_UP_ICON = "pan-up-symbolic"

    ''' Initialization method. '''
    def __init__(self, gtk_builder):

        self.__column_label = gtk_builder.get_object(
            "treeview-column-label")
        self.__column_event_box = gtk_builder.get_object(
            "treeview-column-event-box")
        self.__column_event_box.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.__sorting_arrow_icon = gtk_builder.get_object(
            "treeview-column-sorting-arrow")
        self.__add_samples_button = gtk_builder.get_object(
            "treeview-column-add-samples")                 
        self.__scrolledwindow = gtk_builder.get_object(
            "treeview-scrolledwindow")

        # The TreeView store (Gtk.ListStore)
        model = Gtk.ListStore(int, str, str)
        # The TreeView sample name column  
        self.__treeview_renderer_text = Gtk.CellRendererText()
        self.__samples_column = Gtk.TreeViewColumn(
            "", self.__treeview_renderer_text, text=1)
        self.__samples_column.set_sort_column_id(1) 

        # The TreeView number of comets column
        self.__comets_number_column = Gtk.TreeViewColumn(
            "", Gtk.CellRendererText(), text=2)

        # The TreeView 
        treeview = gtk_builder.get_object("treeview")       
        treeview.set_model(model)
        treeview.set_headers_visible(False)
        treeview.append_column(self.__samples_column)
        treeview.append_column(self.__comets_number_column)

        # ListView initialization
        super().__init__(treeview)

        # Default parameters
        self.__initialize()

    ''' Attributes initialization. '''
    def __initialize(self):

        self.get_model().clear()
        self.__sorting = SamplesView.SORT_DESCENDING
        self.__sorting_arrow_icon.set_visible(False)

    ''' Restart behaviour. '''
    def restart(self):
        self.__initialize()


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                  Methods                                    #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Sets the number of comets for sample with given identifier. '''
    def set_sample_number_of_comets(self, sample_id, n_comets, analyzed_flag):

        if n_comets == 0 and not analyzed_flag:
            n_comets_string = "" 
        else:
            n_comets_string = "(" + str(n_comets) + ")"

        row = self.get_sample_row(sample_id)
        self.get_model().set_value(self.get_model().get_iter(row),
            2, n_comets_string)

    ''' Sorts the list. Toggles between ascending and descending. '''
    def sort_list(self):

        # Ascending sort
        if self.__sorting == SamplesView.SORT_DESCENDING:

            self.__sorting = SamplesView.SORT_ASCENDING
            self.__sorting_arrow_icon.set_from_icon_name(
                SamplesView.ARROW_UP_ICON, Gtk.IconSize.MENU)

        # Descending sort
        else:

            self.__sorting = SamplesView.SORT_DESCENDING
            self.__sorting_arrow_icon.set_from_icon_name(
                SamplesView.ARROW_DOWN_ICON, Gtk.IconSize.MENU)

        # Tell the TreeViewColumn to sort
        self.__samples_column.clicked()
        # Arrow icon visible
        self.__sorting_arrow_icon.set_visible(True)

    ''' Returns Sample ID with given position on the list. '''
    def get_sample_id(self, pos):
        return self.get_item_id(pos)

    ''' Returns Sample Name at given position. '''
    def get_sample_name(self, pos):
        return self.get_model()[pos][1]

    ''' Returns the row number of the sample that matches given ID. '''
    def get_sample_row(self, sample_id):
        return self.get_row(sample_id)
      
    ''' Returns selected Sample's position. '''
    def get_selected_sample_row(self):
        return self.get_selected_row()

    ''' Adds a Sample to the store. '''
    def add_sample(self, sample_id, sample_name, pos=None):
        self.add_item((sample_id, sample_name, None), pos)

    ''' Deletes the Sample with given ID from the store. '''
    def delete_sample(self, sample_id):
        return self.delete_item(sample_id)

    ''' Renames the Sample with given ID in the store. '''
    def rename_sample(self, sample_id, text):

        renamed = False
        treeiter = self.get_model().get_iter_first()
        while treeiter is not None and not renamed:
            if self.get_model()[treeiter][0] == sample_id:           
                self.get_model().set_value(treeiter, 1, text)
                renamed = True
            else:
                treeiter = self.get_model().iter_next(treeiter)

    ''' Prepares selected row to be edited. '''
    def prepare_row_for_rename(self):

        # Cell is editable for this operation
        self.__treeview_renderer_text.set_property("editable", True)
        path, column = self.get_treeview().get_cursor()
        self.get_treeview().set_cursor(path, column, True)
        # Cell is no longer editable after focus loss
        self.__treeview_renderer_text.set_property("editable", False) 



# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_column_label(self):
        return self.__column_label

    def set_column_label(self, column_label):
        self.__column_label = column_label

    def get_add_samples_button(self):
        return self.__add_samples_button

    def set_add_samples_button(self, add_samples_button):
        self.__add_samples_button = add_samples_button

    def get_treeview_renderer_text(self):
        return self.__treeview_renderer_text

    def set_treeview_renderer_text(self, treeview_renderer_text):
        self.__treeview_renderer_text = treeview_renderer_text

    def get_sorting_arrow_icon(self):
        return self.__sorting_arrow_icon

    def set_sorting_arrow_icon(self, sorting_arrow_icon):
        self.__sorting_arrow_icon = sorting_arrow_icon

    def get_column_event_box(self):
        return self.__column_event_box

    def set_column_event_box(self, column_event_box):
        self.__column_event_box = column_event_box


 
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	AnalyzeSamplesView                                                        #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ # 

class AnalyzeSamplesView(ListView):

    '''
        The AnalyzeSamplesView class. The list view of AnalyzeSamplesWindow to 
        choose which Samples will be analyzed.
    '''

    ''' Initialization method. '''
    def __init__(self, gtk_builder, observer):

        # Observer
        self.__observer = observer
                
        # TreeView column1
        self.__treeview_renderer_text = Gtk.CellRendererText()
        self.__samples_column_name = Gtk.TreeViewColumn("",
            self.__treeview_renderer_text, text=1)
        self.__samples_column_name.set_expand(True)
        self.__samples_column_name.set_sort_column_id(1)
        self.__samples_column_name.set_alignment(0.5) 

        # TreeView column2
        self.__treeview_renderer_toggle = Gtk.CellRendererToggle()
        self.__samples_column_toggle = Gtk.TreeViewColumn(
            "", self.__treeview_renderer_toggle, active=2)
        self.__samples_column_toggle_checkbox = Gtk.CheckButton()
        self.__samples_column_toggle_checkbox.show_all()
        self.__samples_column_toggle.set_widget(
            self.__samples_column_toggle_checkbox)        
        self.__samples_column_toggle.set_expand(True)
        self.__samples_column_toggle.set_clickable(True)
        self.__samples_column_toggle.set_alignment(0.5)
            
        # The Model (Gtk.ListStore)
        # (SampleID, SampleName, ProcessFlag)
        model = Gtk.ListStore(int, str, bool)

        # The TreeView (Gtk.TreeView)
        treeview = gtk_builder.get_object("analyze-samples-treeview")
        treeview.set_model(model)
        treeview.append_column(self.__samples_column_name)
        treeview.append_column(self.__samples_column_toggle)

        # ListView initialization
        super().__init__(treeview)


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                 Methods                                     #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    ''' Toggles all the samples checkbox. '''
    def toggle_all(self):

        # Toggle column header checkbox
        self.__samples_column_toggle_checkbox.set_active(
            not self.__samples_column_toggle_checkbox.get_active())

        # Set rows checkbox value
        row = 0
        while row < len(self.get_model()):
            treeiter = self.get_model().get_iter(row)        
            self.get_model().set_value(treeiter, 2,
                self.__samples_column_toggle_checkbox.get_active())
            row += 1
        
        # Update the number of samples to analyze
        if self.__samples_column_toggle_checkbox.get_active():
            self.__samples_to_analyze_number = len(self.get_model())
        else:
            self.__samples_to_analyze_number = 0

        # Number of samples to analyze changed
        self.__on_samples_to_analyze_number_changed()

    ''' Behaviour when the number of samples to analyze changes. '''
    def __on_samples_to_analyze_number_changed(self):

        self.__observer.get_next_button().set_sensitive(
            self.__samples_to_analyze_number > 0)

    ''' Sets the store. '''
    def set_model(self, model):
 
        for item in model:
            self.get_model().append((item[0], item[1], True))
        self.__samples_to_analyze_number = len(self.get_model())
        self.__observer.get_next_button().set_sensitive(True)

    ''' Toggle given row. '''
    def toggle_row(self, path):

        # Toggle row value
        value = not self.get_model()[path][2]

        # Set new value
        treeiter = self.get_model().get_iter(path)        
        self.get_model().set_value(treeiter, 2, value)

        # Update number of samples to analyze
        if value:
            self.__samples_to_analyze_number += 1
        else:
            self.__samples_to_analyze_number -= 1

        # Number of samples to analyze changed
        self.__on_samples_to_analyze_number_changed()

    ''' Returns the requested samples identifiers to process by the user. '''
    def get_requested_samples(self):
        return [sample[0] for sample in self.get_model() if sample[2]]


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                             Getters & Setters                               #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

    def get_samples_column_name(self):
        return self.__samples_column_name

    def set_samples_column_name(self, samples_column_name):
        self.__samples_column_name = samples_column_name

    def get_treeview_renderer_toggle(self):
        return self.__treeview_renderer_toggle

    def set_treeview_renderer_toggle(self, renderer_toggle):
        self.__treeview_renderer_toggle = renderer_toggle

    def get_samples_column_toggle(self):
        return self.__samples_column_toggle

    def set_samples_column_toggle(self, samples_column_toggle):
        self.__samples_column_toggle = samples_column_toggle

