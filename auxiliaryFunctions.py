import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import subprocess
import platform
import webbrowser


def opsys():
    
    return platform.system()

def open_file(filename):
    
    '''
    This fucntion opens a file with the default file viewer.
    
    Requires: filename is a string with the format filename.pdf .
    Ensures: the file open, empty return; if we cant detect the OS, messagebox pops up.
    '''

    system=opsys()
    if system == 'Windows':
        subprocess.call('start ' +filename, shell=True)
    elif system == 'Darwin':
        subprocess.call('open ' +filename, shell=True)
    elif system == 'Linux':
        subprocess.call('xdg-open ' +filename, shell=True)
    else:
        messagebox.showerror("Error", "It was not possible to open the file because we could not identify your operative system.")
        
    return
                

def inbetween(lower, upper, value, units):

    '''
    Checks in a value is between other two. These values have physical units.

    Requires:
    lower, upper and value are strings with the format 'float_value units', where units are eV or any multiples, for example.
    units is a string with the main unit: m, eV, N, g, ...
    Ensures:
    Boolean True if it is in range; AssertionError otherwise.
    '''

    submultiples={'d':'e-1', 'c':'e-2', 'm':'e-3', 'u':'e-6', 'n':'e-9', 'p':'e-12', 'f':'e-15', 'a':'e-18', 'z':'e-21', 'y':'e-24',
                  'k':'e3', 'M':'e6', 'G':'e9', 'T':'e12', 'P':'e15', 'E':'e18', 'Z':'e21', 'Y':'e24', 'h':'e2', 'da':'e1', '':''}


    elements=[lower, upper, value]
    adv_var=0
    for element in elements:
        index1=element.find(' ')
        index2=element.rfind(units)
        elements[adv_var]=float(element[:index1]+submultiples[element[index1+1:index2]])
        adv_var+=1   

    if elements[2]>=elements[0] and elements[2]<=elements[1]:
        return True
    else:
        raise AssertionError
        return


def hide_widget(widgets):

    '''
    This functions hides an array of widgets.

    Requires: widgets is a list of the widgets names.
    Ensures: it hides all the widgets.
    '''
    
    for widget in widgets:
        widget.pack_forget()

    return


def show_widget(widgets):

    '''
    This functions shows an array of widgets.

    Requires: widgets is a list of the widgets names.
    Ensures: it shows all the widgets.
    '''
    
    for widget in widgets:
        widget.pack(side=tk.LEFT)

    return


def swap_widgets(state, widgets_topack, widgets_toforget):

    '''
    This functions hides or shows a specified set of widgets, depending on an external variable.

    Requires:
    widgets_topack and widgets_toforget are lists of the widgets names.
    state is a True or False string.
    Ensures:
    It shows all the widgets that are hiding and hides all the widgets that are showing.
    '''

    if state=='True':
        hide_widget(widgets_toforget)
        show_widget(widgets_topack)
    if state=='False':
        hide_widget(widgets_topack)
        show_widget(widgets_toforget)

    return


def set_image_with_white_background(image):

    '''
    If an image has no background, this functions returns the same image with white background as a varibale.

    Requires: image_name.extension .
    Ensures: varibale containing that same image with white background.
    '''

    icon = Image.open(image)

    white_bg = Image.new("RGBA", icon.size, (255, 255, 255))
    
    icon_with_white_bg = Image.alpha_composite(white_bg.convert("RGBA"), icon.convert("RGBA"))

    return icon_with_white_bg


def about_popup(tks):

    '''
    Generates a popup with general info about the program: history, creators, purpose...
    '''

    popup_window = tk.Toplevel(tks)
    popup_window.title("About")
    popup_window.wm_iconphoto(True, ImageTk.PhotoImage(set_image_with_white_background('DoNotDelete/info.png')))

    label = tk.Label(popup_window, text="TOPAS Automator was created by Tomás Campante (B.Sc. at the time) as part of one of many LIP internships at the NUC-RIA group, in the year of 2023.\nCarolina Felgueiras (M.Sc. at the time) was working with the detection of neutrons using resistive plate chambers and was running her simulations in the TOPAS framework.\nHer work required to run several simulations with different setups and this internship came as a way to help her automize this process.\n\n\nVersion 4.1.2")
    label.pack(padx=10, pady=10)

    close_button = tk.Button(popup_window, text="Close", command=popup_window.destroy)
    close_button.pack(pady=10)

    return


def help_popup(tks):
    
    '''
    Generates a popup that will contain a link into a webpage where you'll find a user guide.
    '''
    
    popup_window = tk.Toplevel(tks)
    popup_window.title("Help")
    popup_window.wm_iconphoto(True, ImageTk.PhotoImage(set_image_with_white_background('DoNotDelete/help.png')))

    label = tk.Label(popup_window, text="To learn more about TOPAS Automator,\n left-click on any of these text to read our user guide!")
    label.pack(padx=10, pady=10)
    label.bind("<Button-1>", lambda event:webbrowser.open("https://nuc-ria.notion.site/TOPAS-Automator-User-Guide-4d8877b8c534433aa655322c855499a0"))

    userguide_button=tk.Button(popup_window, text="Open User Guide as .pdf file", command = lambda:open_file('DoNotDelete/TOPASAutomator_UserGuide.pdf'))
    userguide_button.pack(pady=10)

    close_button = tk.Button(popup_window, text="Close", command=popup_window.destroy)
    close_button.pack(pady=10)

    return


def openTOPAS(filename):

    '''
    When the program is being run in the terminal (!), it will open TOPAS with the file that was created.
    '''

    print('Olha o topas a correr aqui!')
    subprocess.call('bash -i -c "topas'+filename+'"', shell=True)

    return
