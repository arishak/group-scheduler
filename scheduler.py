from tkinter import *
from tkinter import filedialog
import datetime
import pickle
from math import log, ceil, floor
from matplotlib import cm
import re

def init(data):
    data.margin = 30
    data.leftmargin = 50
    data.start = 8
    data.end = 24
    data.step = 0.5
    data.slots = int((data.end - data.start) / data.step)
    t = data.start
    data.times = []
    while t < data.end:
        mins = int((t % 1) * 60)
        data.times.append(str(datetime.time(int(t) % 24, mins))[:-3])
        t += data.step
    data.week = [[set() for i in range(data.slots)] for j in range(7)]
    data.rows = 7
    data.cols = len(data.week[0])
    data.cellwidth = (data.width-2*data.margin)//data.rows
    data.cellheight = (data.height-data.margin)//data.cols
    data.name = ''
    data.names = []
    data.groups = dict()
    data.day_names = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
    data.cmap = cm.get_cmap('bone_r')
    createMenu(data)
    createList(data)
    createButtons(data)
    redrawRoot(data.canvas, data)


#---------------#
# color helpers #
#---------------#
# converts (0, 1) rgb values to hex
def normrgb2hex(r, g, b, a=None):
    return "#{:02x}{:02x}{:02x}".format(int(255*r), int(255*g), int(255*b))

# distributes colors nicely across possible availability fractions
def getc(x, n):
    exp = 1 if n < 2 else log(n, 2)
    frac = 0.0 if n == 0 else x/n
    return max(0.02, (frac**exp))

#---------#
# Menubar #
#---------#
# create group + view + theme menus in the menubar
def createMenu(data):
    data.menubar = Menu(data.root)
    data.menu_groups = Menu(data.menubar)
    data.menubar.add_cascade(menu=data.menu_groups, label='Groups')
    view_menu = Menu(data.menubar)
    data.show_availability = BooleanVar()
    view_menu.add_checkbutton(label="Availability", onvalue=True, offvalue=False,
                              variable=data.show_availability,
                              command=lambda: toggledAvailabilityShow(data))
    data.menubar.add_cascade(menu=view_menu, label='View')
    theme_menu = Menu(data.menubar)
    for theme in cm.cmap_d.keys():
        theme_menu.add_command(label=theme,
                               command=lambda theme=theme: setTheme(data, theme))
    data.menubar.add_cascade(menu=theme_menu, label='Theme')
    data.root.config(menu=data.menubar)

# change color scheme
def setTheme(data, theme):
    data.cmap = cm.get_cmap(theme)
    redrawRoot(data.canvas, data)

# restricts selection to desired group
def selectGroup(data, name):
    data.namelist.selection_clear(0, END)
    for i in data.groups[name]:
        data.namelist.selection_set(i)
    redrawRoot(data.canvas, data)


#-------------#
# Main Window #
#-------------#
# creates buttons for main window
def createButtons(data):
    entry = Entry(data.root)
    entry.grid(row=2, column=1, sticky=E)
    data.entry = entry
    b = Button(data.root, text="new/edit", command=lambda: newClick(data))
    b.grid(row=2, column=2, sticky=W)
    entry.bind('<Return>', lambda _: newClick(data))
    entry.focus_force()
    save = Button(data.root, text="save", command=lambda: saveClick(data))
    save.grid(row=3, column=1, pady=5)
    load = Button(data.root, text="load", command=lambda: loadClick(data))
    load.grid(row=3, column=1, sticky=E, pady=5)
    icsadd = Button(data.root, text="batch ics add", command=lambda: icsAddClick(data))
    icsadd.grid(row=3, column=2, sticky=E, pady=5)
    newgroup = Button(data.root, text="group", command=lambda: groupClick(data))
    newgroup.grid(row=2, column=3)

# creates list of names for main window
def createList(data):
    namelist = Listbox(data.root, selectmode=EXTENDED, exportselection=0)
    scrollbar = Scrollbar(data.root, orient=VERTICAL)
    data.namelist = namelist
    namelist.grid(row=1, column=3, pady=(data.margin, 15), padx=data.margin,
                  sticky=N+S)
    scrollbar.grid(row=1, column=3, padx=(data.margin, data.margin-15),
                   pady=(data.margin, 15), sticky=N+S+E)
    namelist.bind('<<ListboxSelect>>', lambda _: redrawRoot(data.canvas, data))
    data.list_created = True
    namelist.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=namelist.yview)

# main screen 'new' button action
# brings up individual screen
def newClick(data, name=None, hidden=False):
    if name:
        data.name = name
    else:
        data.name = data.entry.get().strip()
        data.entry.delete(0, END)
    top = Toplevel(data.root)
    if hidden:
        top.withdraw()
    data.top = top
    indvScreenInit(data)

# main screen 'save' button action
# saves all schedules and groupings to a file
def saveClick(data):
    fname = filedialog.asksaveasfilename(parent=data.root, defaultextension='.pickle', initialdir='.')
    if fname != None and fname != '':
        outfile = open(fname, 'wb')
        pickle.dump((data.names, data.week, data.groups), outfile)
        outfile.close()

# main screen 'load' button action
# clears current schedules and groups and loads new ones from the selected file
def loadClick(data):
    fname = filedialog.askopenfilename(parent=data.root)
    if fname == None or fname == '':
        return
    infile = open(fname, 'rb')
    data.names, data.week, data.groups = pickle.load(infile)
    infile.close()
    data.namelist.delete(0, END)
    data.menu_groups.delete(0, END)
    for name in data.names:
        data.namelist.insert(END, name)
    for group in data.groups:
        data.menu_groups.add_command(label=group,
                                     command=lambda x=group: selectGroup(data, x))
    data.namelist.selection_set(0, END)
    redrawRoot(data.canvas, data)

# main screen 'batch load ics' button action
# adds data from selected .ics files, using file names as person names
def icsAddClick(data):
    fnames = filedialog.askopenfilename(parent=data.root, multiple=True, filetypes=[('ICS', '.ics')])
    for fname in fnames:
        name = fname[fname.rfind('/')+1:].split('.')[0].title()
        if name not in data.names:
            newClick(data, name, hidden=True)
            loadics(data, fname)
            doneClick(data)
    
    
# helper for groupClick, adds/updates group in menu
def addGroup(data, name):
    if name in data.groups:
        data.menu_groups.delete(name)
    data.groups[name] = list(map(int, data.namelist.curselection()))
    data.menu_groups.add_command(label=name,
                                 command=lambda: selectGroup(data, name))
    
# main screen 'group' button action
# creates new group from current selection
def groupClick(data):
    popup = Toplevel()
    msg = Label(popup, text="Name this group:")
    msg.pack(fill=X)
    s = StringVar()
    e = Entry(popup, textvariable=s)
    e.pack()
    e.focus_set()
    e.bind('<Return>', lambda _: (addGroup(data, s.get()), popup.destroy()))

# uses mouse location in order to display availability
def rootHover(event, data):
    if not data.show_availability.get():
        return
    x, y = event.x, event.y
    r = (x - data.leftmargin) // data.cellwidth
    c = (y - data.margin) // data.cellheight
    free = ""
    busy = ""
    cur_sel = set(map(lambda i: data.names[i], data.namelist.curselection()))
    if (0 <= r < data.rows and 0 <= c < data.cols):
        free = "\n".join(cur_sel & data.week[r][c])
        busy = "\n".join(cur_sel - data.week[r][c])
    data.freeNames.set(free)
    data.busyNames.set(busy)
    

# draws main window
def redrawRoot(canvas, data):
    canvas.delete(ALL)
    selected = map(int, data.namelist.curselection())
    names = set()
    for i in selected:
        names.add(data.names[i])
    exp = 1 if len(names) < 2 else log(len(names), 2)
    for r in range(data.rows):
        x = (r+0.5)*data.cellwidth+data.leftmargin
        y = data.margin
        canvas.create_text(x, y, text=data.day_names[r].title(), anchor=S)
        for c in range(data.cols):
            x0 = r*data.cellwidth+data.leftmargin
            y0 = c*data.cellheight+data.margin
            x1 = x0+data.cellwidth
            y1 = y0+data.cellheight
            n = len(data.week[r][c].intersection(names))
            frac = getc(n, len(names))
            fill = normrgb2hex(*(data.cmap(frac)))
            textfill = 'black' if (sum(data.cmap(frac)) - 1)/3 > 0.7 else 'white'
            canvas.create_rectangle(x0, y0, x1, y1, fill=fill)
            canvas.create_text((x0+x1)/2, (y0+y1)/2, text=str(len(names)-n), fill=textfill)
            if r == 0:
                canvas.create_text(x0-5, y0, text=str(data.times[c]), anchor=E)
    canvas.update()


#-------------------#
# Individual Window #
#-------------------#
# draws individual window in data.top window
def indvScreenInit(data):
    name_label = Label(data.top, text=data.name)
    name_label.grid(row=1, column=1, columnspan=7)
    data.lbs = []
    for i in range(7):
        lb = Listbox(data.top, selectmode=EXTENDED, exportselection=False,
                     height=32, width=10)
        data.lbs.append(lb)
        lb.grid(row=2, column=i+1)
        for t in data.times:
            lb.insert(END, str(t))
    bdone = Button(data.top, text="done", command=lambda: doneClick(data))
    bdone.grid(row=3, column=5, columnspan=2)
    binvert = Button(data.top, text="invert", command=lambda: invertClick(data))
    binvert.grid(row=3, column=3, columnspan=3)
    bload = Button(data.top, text="load ics", command=lambda: loadics(data))
    bload.grid(row=3, column=2, columnspan=2)
    data.top.bind('<Return>', lambda _: doneClick(data))
    if data.name in data.names:
        loadSchedule(data)

# load individual schedule from overall schedule
def loadSchedule(data):
    for i in range(7):
        lb = data.lbs[i]
        day = data.week[i]
        for slot in range(len(day)):
            if data.name in day[slot]:
                lb.selection_set(slot)
                
# individual screen 'done' button action
# adds individual schedule to overall schedule
def doneClick(data):
    if data.name not in data.names:
        data.names.append(data.name)
        data.namelist.insert(END, data.name)
        data.namelist.selection_set(END)
    for i in range(7):
        lb = data.lbs[i]
        for t in range(data.cols):
            if lb.selection_includes(t):
                data.week[i][t].add(data.name)
            elif data.name in data.week[i][t]:
                data.week[i][t].remove(data.name)
    data.top.destroy()
    redrawRoot(data.canvas, data)

# individual screen 'invert' button action
# inverts selected availability
def invertClick(data):
    for lb in data.lbs:
        for i in range(data.cols):
            if lb.selection_includes(i):
                lb.selection_clear(i)
            else:
                lb.selection_set(i)

# loads individual schedule from .ics file
def loadics(data, fname=None):
    if not fname:
        fname = filedialog.askopenfilename(parent=data.top)

    if fname == None or fname == '':
        return
    infile = open(fname, 'rb')
    ics_file = open(fname)
    ics_data = ics_file.read()
    ics_file.close()

    # reset in case there is already data
    for i in range(len(data.day_names)):
        data.lbs[i].selection_clear(0, END)
    
    pat = re.compile(r'DTSTART:\d+?T(\d\d)(\d\d).*?DTEND:\d+?T(\d\d)(\d\d).+?BYDAY=(\S+)', re.DOTALL)
    for (start_h, start_m, end_h, end_m, days) in re.findall(pat, ics_data):
        for d in days.split(','):
            i = data.day_names.index(d)
            start_idx = floor((int(start_h) - data.start + int(start_m)/60)/data.step)
            end_idx = ceil((int(end_h) - data.start + int(end_m)/60)/data.step)
            for j in range(start_idx, end_idx):
                data.lbs[i].selection_set(j)
    invertClick(data)


#---------------------#
# Availability Window #
#---------------------#
# hide/show toggled
def toggledAvailabilityShow(data):
    if data.show_availability.get():
        createAvailabilityWindow(data)
    else:
        destroyAvailabilityWindow(data)

def destroyAvailabilityWindow(data):
    data.show_availability.set(False)
    data.availability_window.destroy()
        
# create window
def createAvailabilityWindow(data):
    data.show_availability.set(True)
    data.freeNames = StringVar()
    data.busyNames = StringVar()
    data.availability_window = Toplevel(data.root, background='white')
    data.availability_window.protocol("WM_DELETE_WINDOW",
                                      lambda: destroyAvailabilityWindow(data))
    data.availability_window.minsize(300, 750)
    Label(data.availability_window, text="Available",
          font="lucida-grande 14 bold").grid(row=0, column=0, sticky=E+W)
    Label(data.availability_window, textvar=data.freeNames).grid(row=1, column=0, sticky=N+E+W)
    Label(data.availability_window, text="Unavailable",
          font="lucida-grande 14 bold").grid(row=0, column=1, sticky=E+W)
    Label(data.availability_window, textvar=data.busyNames).grid(row=1, column=1, sticky=N+E+W)
    data.availability_window.columnconfigure(0, weight=1)
    data.availability_window.columnconfigure(1, weight=1)
    

# runs overall application
def run(width=300, height=300):
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.grid(row=1, column=1, columnspan=2)
    data.canvas = canvas
    data.root = root
    root.option_add('*tearOff', FALSE)
    init(data)
    
    # set up events
    root.bind("<Motion>", lambda event: rootHover(event, data))
    
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye :)")

run(400, 650)
