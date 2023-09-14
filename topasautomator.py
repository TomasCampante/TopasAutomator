import tkinter as tk
from tkinter import messagebox
from tkinter import font
import copy
import auxiliaryFunctions as aux
from PIL import ImageTk, Image
import subprocess

#####################################################################################################################################

def interface():

    '''
    This function is the program itself. When called, it
    creates the interface, widgets and everything else.

    Making the program in a function makes possible to close the program's window, without shutting down the program.
    '''

    def run_topas(boolean):

        '''
        Generates messagoxes in case something is wrong.
        
        It analyzes if the energy of the beam is in the
        indicated range and if the user has filled every needed value.
        '''

        try:
            aux.inbetween('2.5 eV', '7 MeV', str(beam_energy.get())+' '+str(units.get()), 'eV')
            
            file_manipulator(boolean)
        except AssertionError:
            messagebox.showerror("Error", "Inserted values do not respect the asked range.\nRe-input the beam's energy.")
        #except ValueError:
            #messagebox.showerror("Error", "Most entries accept integers or floats, although make sure the number of neutrons is an integer!")
        except Exception:
            messagebox.showerror("Error", "Make sure to fill every relevant entry!")

        return


    def file_manipulator(boolean):

        '''
        This is the heart and soul of the program. Once the widgets are created
        to receive the inputs from the user, they need to be manipulated to be
        introduced in the .txt output file.
        
        It is necessary to have 6 files similar to those who are being opened
        right below. These files contain the structure of this simulation with nRPCs.
        There are some little things that do not have the input option; although,
        in certain cases, it is possible to just change the file where that is
        featured. Example: if you need the beam to be isotropic, instead of collimated,
        you can swap that directly in the file.

        Requires: boolean is a True or False.
        Ensures: always creates .txt file, but only runs it with TOPAS if boolean is True.
        '''

        # Opening the .txt used as reference to run the program
        other=open('DoNotDelete/other.txt', "r")
        other_lines=other.readlines()
        other.close()
        iselma=open('DoNotDelete/IsElMa.txt', "r") #IsElMa = Isotopes+Elements+Materials
        iselma_lines=iselma.readlines()
        iselma.close()
        pickup=open('DoNotDelete/pickup.txt', "r")
        pickup_lines=pickup.readlines()
        pickup.close()
        beam=open('DoNotDelete/beam.txt', "r")
        beam_lines=beam.readlines()
        beam.close()
        mods=open('DoNotDelete/moderator.txt', "r")
        mods_lines=mods.readlines()
        mods.close()
        scorers=open('DoNotDelete/scorers.txt', "r")
        scorers_lines=scorers.readlines()
        scorers.close()

        to_write=other_lines+iselma_lines+beam_lines
       

        # After opening the text files, we need to replace some of the values with the new inputed ones
        index=0
        # This big if structure does all the work regarding swapping values, when the moderators are left out
        # Don't be scared, I'll try to walk you through it :D
        if moderator.get()=='False':
            # Lets go through every line in the other, IsElMa and beam files
            for line in to_write:
                # Now, lets search for the lines with the parameters we want to change
                axis_index=line.find('b:Gr/ViewA/IncludeAxes')
                boxsize_index=line.find('d:Ge/World/HLZ')
                beamenergy_index=line.find('d:So/NeutronSource/BeamEnergy = ')
                nneutrons_index=line.find('i:So/NeutronSource/NumberOfHistoriesInRun =')
                beamposition_index=line.find('d:Ge/BeamPosition/TransZ =')
                # And change the line accordingly if the parameter is found
                if beamposition_index==0:
                    to_write[index]=line[:2+line.find('=')]+'-'+str(float(distance_rpc_beam.get()))+line[line.find(' cm'):]
                if boxsize_index==0:
                    to_write[index]=line[:2+line.find('=')]+str(float(distance_rpc_beam.get())+float(distance_rpc.get())*float(nnrpc.get()))+line[line.find(' cm'):]
                if axis_index==0:
                    if axis.get()=='On':
                        to_write[index]='b:Gr/ViewA/IncludeAxes ="True" \n'
                    if axis.get()=='Off':
                        to_write[index]='b:Gr/ViewA/IncludeAxes ="False" \n'
                if beamenergy_index==0:
                    to_write[index]='d:So/NeutronSource/BeamEnergy = '+str(float(beam_energy.get()))+' '+str(units.get())+'\n'
                if nneutrons_index==0:
                    to_write[index]='i:So/NeutronSource/NumberOfHistoriesInRun = '+str(int(nneutrons.get()))+'\n'
                index+=1

            # Nice job, now lets all more more pickups, depending on what is asked by the user
            # Lets make a deepcopy of the pickup, just bare with me: I'll explain later
            new_pickup_lines=copy.deepcopy(pickup_lines)
            # Lets go through every RPC (we will not account with the first one because the used file already defines the first RPC correctly)
            for adv_var in range(1,int(nnrpc.get())):
                # We go through every line in the pickup file
                for line in pickup_lines:
                    # And change what needs to be changed
                    if line[0]=='#' and line.find('#Cathode0#')<0: # This changes the number of the "slice" of RPC
                        newline='\n'+line[:-4]+str(adv_var)+line[-3:]
                        new_pickup_lines.append(newline)
                    if line.find('Cathode0')>=0: # This changes the identifying number of the specific "slice" of RPC cathode
                        newline=line[:line.find('0')]+str(adv_var)+line[line.find('0')+1:]
                        if line.find('TransZ')>=0: # This pushes the slice forward, depending on the distance between RPCs
                            distance=float(line[1+line.find('='):line.find('cm')])
                            new_distance=distance+float(distance_rpc.get())*adv_var
                            newline=newline[:2+newline.find('=')]+str(new_distance)+newline[newline.find(' cm'):]
                        new_pickup_lines.append(newline)
                    if line.find('00/')>=0: # This changes the identifying number of the "slice" of RPC
                        newline=line[:line.find('00/')]+str(adv_var)+line[line.find('00/')+1:]
                        if line.find('TransZ')>=0: # This pushes the slice forward, depending on the distance between RPCs
                            distance=float(line[1+line.find('='):line.find('cm')])
                            new_distance=distance+float(distance_rpc.get())*adv_var
                            newline=newline[:2+newline.find('=')]+str(new_distance)+newline[newline.find(' cm'):]
                        new_pickup_lines.append(newline)
                    if line.find('01/')>=0: # This changes the identifying number of the "slice" of RPC
                        newline=line[:line.find('01/')]+str(adv_var)+line[line.find('01/')+1:]
                        if line.find('TransZ')>=0: # This pushes the slice forward, depending on the distance between RPCs
                            distance=float(line[1+line.find('='):line.find('cm')])
                            new_distance=distance+float(distance_rpc.get())*adv_var
                            newline=newline[:2+newline.find('=')]+str(new_distance)+newline[newline.find(' cm'):]
                        new_pickup_lines.append(newline)
                    # If you notice, we have been ading lines to the list: this is why we need to make a deep copy, so we don't make an infinite loop
                new_pickup_lines.append('\n') # Just ading line breaks, don't mind me
            new_pickup_lines.append('\n\n\n') # Just ading line breaks, don't mind me

            # So, ok, now we do a similir line of though for the scorers
            # This one is simpler, I think you can do it by yourself
            new_scorers_lines=copy.deepcopy(scorers_lines)
            for adv_var in range(1,int(nnrpc.get())):
                new_scorers_lines.append('\n\n')
                for line in scorers_lines:                   
                    if line.find('00/')>=0:
                        line=line.replace('00/', str(adv_var)+'0/')
                    if line.find('01/')>=0:
                        line=line.replace('01/', str(adv_var)+'1/')
                    if line.find('00"')>=0:
                        line=line.replace('00"', str(adv_var)+'0"')
                    if line.find('01"')>=0:
                        line=line.replace('01"', str(adv_var)+'1"')
                    if line.find('00 ###')>=0:
                        line=line.replace('00 ###', str(adv_var)+'0 ###')
                    if line.find('01 ###')>=0:
                        line=line.replace('01 ###', str(adv_var)+'1 ###')
                    new_scorers_lines.append(line)

            # Putting it all together
            to_write=to_write+new_pickup_lines+new_scorers_lines


        # So, this other big branch of the if structure runs the same program, in case it works with moderators
        # Really nothing new, all the reasoning is kind of the same from the above (I won't be explaining everything here)

        # Just a variable that will be useful later
        thickness_rpc=0.17655 #cm
        
        if moderator.get()=='True':
            for line in to_write:
                axis_index=line.find('b:Gr/ViewA/IncludeAxes')
                boxsize_index=line.find('d:Ge/World/HLZ')
                beamenergy_index=line.find('d:So/NeutronSource/BeamEnergy = ')
                nneutrons_index=line.find('i:So/NeutronSource/NumberOfHistoriesInRun =')
                beamposition_index=line.find('d:Ge/BeamPosition/TransZ =')
                if beamposition_index==0:
                    to_write[index]=line[:2+line.find('=')]+'-'+str(float(distance_rpc_beam.get()))+line[line.find(' cm'):]
                if boxsize_index==0:
                    to_write[index]=line[:2+line.find('=')]+str(float(distance_rpc_beam.get())+0.2*float(nnrpc.get())+float(thickness_mod.get())*(float(nnrpc.get())+1))+line[line.find(' cm'):]
                    if side_moderator.get()=='True':
                        to_write[index-1]=to_write[index-1][:2+line.find('=')]+str(5+2*float(thickness_mod.get()))+line[line.find(' cm'):]
                        to_write[index-2]=to_write[index-2][:2+line.find('=')]+str(5+2*float(thickness_mod.get()))+line[line.find(' cm'):]
                if axis_index==0:
                    if axis.get()=='On':
                        to_write[index]='b:Gr/ViewA/IncludeAxes ="True" \n'
                    if axis.get()=='Off':
                        to_write[index]='b:Gr/ViewA/IncludeAxes ="False" \n'
                if beamenergy_index==0:
                    to_write[index]='d:So/NeutronSource/BeamEnergy = '+str(float(beam_energy.get()))+' '+str(units.get())+'\n'
                if nneutrons_index==0:
                    to_write[index]='i:So/NeutronSource/NumberOfHistoriesInRun = '+str(int(nneutrons.get()))+'\n'
                index+=1

            # The moderators stuff, but it is more of the same
            new_mods_lines=[]
            for adv_var in range(0,1+int(nnrpc.get())):
                for line in mods_lines:
                    newline=line[:line.find('0')]+str(adv_var)+line[line.find('0')+1:]
                    if line.find('HLZ')>=0:
                        newline=newline[:2+newline.find('=')]+str(float(thickness_mod.get())*0.5)+newline[newline.find(' cm'):]
                    if line.find('TransZ')>=0:
                        distance=float(line[1+line.find('='):line.find('cm')])
                        new_distance=float(thickness_mod.get())*(adv_var+0.5)+float(thickness_rpc)*(adv_var)
                        newline=newline[:2+newline.find('=')]+str(new_distance)+newline[newline.find(' cm'):]
                    new_mods_lines.append(newline)
                new_mods_lines.append('\n')
            
            # The is structure adds side moderators to the simulation, depeding on the needs of the user 
            if side_moderator.get() == 'True': 
                position = ((float(nnrpc.get()) + 1) * float(thickness_mod.get()) + float(nnrpc.get()) * thickness_rpc) / 2
                sides = ['Left', 'Right', 'Top', 'Bottom']
                for side in sides:
                    for line in mods_lines:
                        newline = line[:line.find('0')] + side + line[line.find('0') + 1:]
                        if line.find('HLX') >= 0 and (side == 'Right' or side == 'Left'):
                            newline = newline[:2 + newline.find('=')] + str(float(thickness_mod.get()) * 0.5) + newline[newline.find(' cm'):]
                        if line.find('HLX') >= 0 and (side == 'Top' or side == 'Bottom'):
                            newline = newline[:2 + newline.find('=')] + str(5.0) + newline[newline.find(' cm'):]
                        if line.find('HLY') >= 0 and (side == 'Top' or side == 'Bottom'):
                            newline = newline[:2 + newline.find('=')] + str(float(thickness_mod.get()) * 0.5) + newline[newline.find(' cm'):]
                        if line.find('HLY') >= 0 and (side == 'Right' or side == 'Left'):
                            newline = newline[:2 + newline.find('=')] + str(5.0) + newline[newline.find(' cm'):]
                        if line.find('TransX') >= 0 and side == 'Right':
                            newline = newline[:2 + newline.find('=')] + str(-5-float(thickness_mod.get()) * 0.5) + newline[newline.find(' cm'):]
                        if line.find('TransX') >= 0 and side == 'Left':
                            newline = newline[:2 + newline.find('=')] + str(5+float(thickness_mod.get()) * 0.5) + newline[newline.find(' cm'):]
                        if line.find('TransY') >= 0 and side == 'Top':
                            newline = newline[:2 + newline.find('=')] + str(5+float(thickness_mod.get()) * 0.5) + newline[newline.find(' cm'):]
                        if line.find('TransY') >= 0 and side == 'Bottom':
                            newline = newline[:2 + newline.find('=')] + str(-5-float(thickness_mod.get()) * 0.5) + newline[newline.find(' cm'):]
                        if line.find('HLZ') >= 0:
                            newline = newline[:2 + newline.find('=')] + str(position) + newline[newline.find(' cm'):]
                        if line.find('TransZ') >= 0:
                            newline = newline[:2 + newline.find('=')] + str(position) + newline[newline.find(' cm'):]
                        if line.find('/Color') >= 0:
                            newline = newline[:2 + newline.find('=')] + ' "purple"'
                        new_mods_lines.append(newline)


            new_pickup_lines=[]
            for adv_var in range(0,int(nnrpc.get())):
                for line in pickup_lines:
                    if line[0]=='#' and line.find('#Cathode0#')<0:
                        newline='\n'+line[:-4]+str(adv_var)+line[-3:] # Here I noticed I could've used the .rfind() method, so if you've been wondering, yes it also works that way 
                        new_pickup_lines.append(newline)
                    if line.find('Cathode0')>=0:
                        newline=line[:line.find('0')]+str(adv_var)+line[line.find('0')+1:]
                        if line.find('TransZ')>=0:
                            distance=float(line[1+line.find('='):line.find('cm')])
                            new_distance=distance+(float(thickness_mod.get()))*(adv_var+1)+float(thickness_rpc)*adv_var
                            newline=newline[:2+newline.find('=')]+str(new_distance)+newline[newline.find(' cm'):]
                        new_pickup_lines.append(newline)                  
                    if line.find('00/')>=0:
                        newline=line[:line.find('00/')]+str(adv_var)+line[line.find('00/')+1:]
                        if line.find('TransZ')>=0:
                            distance=float(line[1+line.find('='):line.find('cm')])
                            new_distance=distance+(float(thickness_mod.get()))*(adv_var+1)+float(thickness_rpc)*adv_var
                            newline=newline[:2+newline.find('=')]+str(new_distance)+newline[newline.find(' cm'):]
                        new_pickup_lines.append(newline)
                    if line.find('01/')>=0:
                        newline=line[:line.find('01/')]+str(adv_var)+line[line.find('01/')+1:]
                        if line.find('TransZ')>=0:
                            distance=float(line[1+line.find('='):line.find('cm')])
                            new_distance=distance+(float(thickness_mod.get()))*(adv_var+1)+float(thickness_rpc)*adv_var
                            newline=newline[:2+newline.find('=')]+str(new_distance)+newline[newline.find(' cm'):]
                        new_pickup_lines.append(newline)       
                new_pickup_lines.append('\n')
            new_pickup_lines.append('\n\n\n')
            
            new_scorers_lines=copy.deepcopy(scorers_lines)
            for adv_var in range(1,int(nnrpc.get())):
                new_scorers_lines.append('\n\n')
                for line in scorers_lines:                   
                    if line.find('00/')>=0:
                        line=line.replace('00/', str(adv_var)+'0/')
                    if line.find('01/')>=0:
                        line=line.replace('01/', str(adv_var)+'1/')
                    if line.find('00"')>=0:
                        line=line.replace('00"', str(adv_var)+'0"')
                    if line.find('01"')>=0:
                        line=line.replace('01"', str(adv_var)+'1"')
                    if line.find('00 ###')>=0:
                        line=line.replace('00 ###', str(adv_var)+'0 ###')
                    if line.find('01 ###')>=0:
                        line=line.replace('01 ###', str(adv_var)+'1 ###')
                    new_scorers_lines.append(line)

            to_write=to_write+new_mods_lines+new_pickup_lines+new_scorers_lines


        # Saving the new compiled file with all the new variables
        filename="to_run.txt"
        if moderator.get()=='True':
            filename='rpc-'+str(nnrpc.get())+'_moderators-'+str(moderator.get())+'_sidemoderators-'+str(side_moderator.get())+'_'+str(thickness_mod.get())+'cm_'+str(beam_energy.get())+str(units.get())+'_'+str(nneutrons.get())+".txt"
        else:
            filename='rpc-'+str(nnrpc.get())+'_moderators-'+str(moderator.get())+'_'+str(beam_energy.get())+str(units.get())+'_'+str(nneutrons.get())+".txt"
        newfile=open(filename, 'w') 
        newfile.writelines(to_write)
        newfile.close()

	    # When the program is being run in the terminal (!), it will open the file or TOPAS with the file that was created.
        if boolean is True:
            subprocess.call('bash -i -c "topas '+filename+'"', shell=True)
        if boolean is False:
            aux.open_file(filename)
        else:
            pass   
         
        return    
            
    ####################################################################################################################################
        
    '''
                GUI's WIDGETS
    '''


    # Generating the main window
    main = tk.Tk()
    main.geometry(f"{main.winfo_screenwidth()}x{main.winfo_screenheight()}")
    main.title('TOPAS Automator')
    main.wm_iconphoto(True, ImageTk.PhotoImage(Image.open('DoNotDelete/topas.png')))

    # Generating the menus in the main window
    menu = tk.Menu(main)
    main.config(menu = menu)
    file_menu = tk.Menu(menu, tearoff=False)
    menu.add_cascade(label='Home', menu=file_menu) # When clicked, this button provides more functionalities
    file_menu.add_command(label='Run', command=lambda:run_topas(True)) # This button is the same as the 'Open with TOPAS' button
    file_menu.add_command(label='Reset', command=lambda:(main.destroy(), interface())) # This button closes the window, and open it again, reseting everything
    file_menu.add_command(label='Exit', command=lambda:main.destroy()) # This button shuts everything down
    menu.add_command(label='About', command=lambda:aux.about_popup(main)) # This button opens a new mini-window (see the called function)
    menu.add_command(label='Help', command=lambda:aux.help_popup(main)) # This button opens a new mini-window (see the called function)

    # Creating the frame where the logos will be
    frame_logos = tk.Frame(main)
    frame_logos.pack(padx=15, side=tk.RIGHT,fill=tk.Y)

    # Processing the logos
    logos = Image.open("DoNotDelete/logos_nobg.png")
    logos.thumbnail((200,200))
    logos = ImageTk.PhotoImage(logos)
    logos_label = tk.Label(frame_logos, image = logos)
    logos_label.image = logos
    logos_label.pack(side=tk.TOP, anchor=tk.NE)

    # Creating a customized font
    my_font = font.Font(size=13)

    # The following code creates the widgets necessary to receive the inputs from the user
    frame_initialsettings=tk.Frame(main)
    frame_initialsettings.pack(pady=(10,0))

    axis=tk.StringVar()
    check_axis = tk.Checkbutton(frame_initialsettings, text='Do you want to see the axes in the simulation?', variable=axis, offvalue='Off', onvalue='On')
    check_axis.deselect() 
    check_axis.pack()
    
    label_rpc = tk.Label(frame_initialsettings, text="Number of nRPCs:")
    label_rpc.pack(side=tk.LEFT)

    nnrpc = tk.Scale(frame_initialsettings, from_=1, to=15, orient=tk.HORIZONTAL, length=200)
    nnrpc.pack(side=tk.LEFT)
    
    frame_beamdist=tk.Frame(main)
    frame_beamdist.pack()

    label_beamdist = tk.Label(frame_beamdist, text="Distance between the first nRPC and the beam (in cm):")
    label_beamdist.pack(side=tk.LEFT)

    distance_rpc_beam = tk.Entry(frame_beamdist)
    distance_rpc_beam.insert(0, '5')
    distance_rpc_beam.pack(side=tk.LEFT)

    frame_moderators1=tk.Frame(main)
    frame_moderators1.pack()

    moderator=tk.StringVar()
    moderators = tk.Checkbutton(frame_moderators1, text='Include paraffin moderators?', variable=moderator, offvalue='False', onvalue='True',
                                command=lambda:aux.swap_widgets(str(moderator.get()), [side_moderators,label_thick, thickness_mod], [label_dist, distance_rpc]))
    moderators.select() 
    moderators.pack()
    
    side_moderator=tk.StringVar()
    side_moderators = tk.Checkbutton(frame_moderators1, text='Include side paraffin moderators?', variable=side_moderator, offvalue='False', onvalue='True')
    side_moderators.select() 
    side_moderators.pack()
    
    frame_moderators2=tk.Frame(main)
    frame_moderators2.pack()

    label_thick = tk.Label(frame_moderators2, text="Thickness of the moderators (in cm):")
    label_thick.pack(side=tk.LEFT)

    thickness_mod = tk.Entry(frame_moderators2)
    thickness_mod.insert(0, '1')
    thickness_mod.pack(side=tk.LEFT)

    label_dist = tk.Label(frame_moderators2, text="Distance between nRPCs (in cm):")
    #label_dist.pack(side=tk.LEFT)

    distance_rpc = tk.Entry(frame_moderators2)
    distance_rpc.insert(0, '2')
    #distance_rpc.pack(side=tk.LEFT)

    frame_beam=tk.Frame(main)
    frame_beam.pack()

    label_beamenergy = tk.Label(frame_beam, text="Beam's energy (from 2.5e-6 to 7 MeV):")
    label_beamenergy.grid(row=0, column=0)

    beam_energy = tk.Entry(frame_beam)
    beam_energy.insert(0, '5')
    beam_energy.grid(row=0, column=1)

    units=tk.StringVar()
    units.set('MeV')
    drop_units=tk.OptionMenu(frame_beam, units, 'eV', 'keV', 'MeV')
    drop_units.grid(row=0, column=2)

    frame_quantity=tk.Frame(main)
    frame_quantity.pack()

    label_nneutrons = tk.Label(frame_quantity, text="Amount of neutrons in beam:")
    label_nneutrons.pack(side=tk.LEFT)

    nneutrons = tk.Entry(frame_quantity)
    nneutrons.insert(0, '100')
    nneutrons.pack(side=tk.LEFT)

    # This final frame is special because it contains a label with the name of the file that will be generated
    # It also contains the two principal buttons, vital do run the program
    frame_final=tk.Frame(main)
    frame_final.pack(pady=(20, 0))

    filename_strvar=tk.StringVar()
    filename_strvar.set('Filename: to_run.txt')
    filename_label= tk.Label(frame_final, textvariable= filename_strvar)
    filename_label.pack(pady=(0,40))
    
    def update_filename(event=None):

        '''
        Don't mind this function, its only purpose is to keep updating a label.
        '''

        if beam_energy.get()!='' or thickness_mod.get()!='' or nneutrons.get()!='' or distance_rpc_beam.get()!='' or nnrpc.get()!='' or units.get()!='Units':
            if moderator.get()=='True':
                filename_strvar.set('Filename: '+'rpc-'+str(nnrpc.get())+'_moderators-'+str(moderator.get())+'_sidemoderators-'+str(side_moderator.get())+'_'+str(thickness_mod.get())+'cm_'+str(beam_energy.get())+str(units.get())+'_'+str(nneutrons.get())+".txt")
            else:
                filename_strvar.set('Filename: '+'rpc-'+str(nnrpc.get())+'_moderators-'+str(moderator.get())+'_'+str(beam_energy.get())+str(units.get())+'_'+str(nneutrons.get())+".txt")
        else:
            filename_strvar.set('Filename: '+"to_run.txt")

        return
    
    
    # Creating the setup preview
    label_preview=tk.Label(frame_logos, text="\nSETUP'S PREVIEW", font=('', 13, 'bold'))
    label_preview.pack()
    
    label=tk.Label(frame_logos, text="(top view)")
    label.pack()
    
    canvas_width=400
    canvas_height=600

    def draw_shapes():
        
        '''
        This function creates a visualization in which it is possible to preview the setup where we are going to simulate.
        '''
        
        preview.delete("all")
        
        scale=10 # 1 cm = 10 points in canvas
        
        try:
            # re-scalling if needed
            if moderator.get()=='True' and 20+float(distance_rpc_beam.get())*scale+scale*float(1+nnrpc.get())*float(thickness_mod.get())>canvas_height:
                scale=((-20+canvas_height)*scale)/(20+float(distance_rpc_beam.get())*scale+scale*float(1+nnrpc.get())*float(thickness_mod.get()))
            if moderator.get()=='False' and 20+float(distance_rpc_beam.get())*scale+float(distance_rpc.get())*scale*(nnrpc.get())>canvas_height:
                scale=((-20+canvas_height)*scale)/(20+float(distance_rpc_beam.get())*scale+float(distance_rpc.get())*scale*(nnrpc.get()))            
            
            # scale shape
            preview.create_line(650-20-scale/2, 50, 650-20+scale/2, 50, fill='black',width=3)
            preview.create_text(650-20, 40, text="1 cm")
            
            # beam shape
            preview.create_line(canvas_width/2, canvas_height, canvas_width/2, canvas_height-20-float(distance_rpc_beam.get())*scale, fill='orange', width=2)
 
            # moderators and rpcs
            if moderator.get()=='False':
                for nrpc in range(nnrpc.get()):
                    # rpc shape
                    preview.create_line(canvas_width/2-50, 
                                    canvas_height-20-float(distance_rpc_beam.get())*scale-float(distance_rpc.get())*scale*(nrpc), 
                                    canvas_width/2+50, 
                                    canvas_height-20-float(distance_rpc_beam.get())*scale-float(distance_rpc.get())*scale*(nrpc), 
                                    fill='aqua', width=4)  
            if moderator.get()=='True':
                # moderator shape
                preview.create_rectangle(canvas_width/2-50, 
                                        canvas_height-20-float(distance_rpc_beam.get())*scale-scale*float(1+nnrpc.get())*float(thickness_mod.get()), 
                                        canvas_width/2+50, 
                                        canvas_height-20-float(distance_rpc_beam.get())*scale, 
                                        fill='violet')
                if side_moderator.get()=='True':
                    # side moderator shapes
                    preview.create_rectangle(canvas_width/2-50-scale*float(thickness_mod.get()),  
                                            canvas_height-20-float(distance_rpc_beam.get())*scale-scale*float(1+nnrpc.get())*float(thickness_mod.get()),
                                            canvas_width/2-50, 
                                            canvas_height-20-float(distance_rpc_beam.get())*scale, 
                                            fill='purple') 
                    preview.create_rectangle(canvas_width/2+50, 
                                            canvas_height-20-float(distance_rpc_beam.get())*scale-scale*float(1+nnrpc.get())*float(thickness_mod.get()),
                                            canvas_width/2+50+float(thickness_mod.get())*scale,  
                                            canvas_height-20-float(distance_rpc_beam.get())*scale,  
                                            fill='purple')
                for nrpc in range(nnrpc.get()):
                    # rpc shape
                    preview.create_line(canvas_width/2-50, 
                                    canvas_height-20-float(distance_rpc_beam.get())*scale-float(thickness_mod.get())*scale*(nrpc+1), 
                                    canvas_width/2+50, 
                                    canvas_height-20-float(distance_rpc_beam.get())*scale-float(thickness_mod.get())*scale*(nrpc+1), 
                                    fill='aqua', width=4)       
        except:
            pass

        # beam box
        preview.create_rectangle(canvas_width/2-10, canvas_height-20, canvas_width/2+10, canvas_height, fill='black')
        
        # legend text
        varx=425
        vary=canvas_height
        preview.create_text(canvas_width*1.5,567, font=("Arial", 12), fill="black",
                    text='Blue lines: nRPCs\nOrange line: neutron beam\nViolet and purple boxes: paraffin moderators')
        preview.create_oval(varx,vary-60, varx+12,vary-48, fill='aqua')
        preview.create_oval(varx,vary-40, varx+12,canvas_height-28, fill='orange')
        preview.create_oval(varx,canvas_height-20, varx+12,canvas_height-8, fill='purple')
        preview.create_oval(varx-15,canvas_height-20, varx-3,canvas_height-8, fill='violet')      
        
        # axes picture
        axis_img = ImageTk.PhotoImage(Image.open("DoNotDelete/axes.png"))
        main.axis_img = axis_img
        preview.create_image((674, 20), anchor='nw', image=axis_img)

        return
    

    preview = tk.Canvas(frame_logos, width=800, height=canvas_height)
    preview.pack()

    def automatic_update(event):

        '''
        This function will be triggered when the widgets are changed.
        '''
        
        update_filename()
        widget.after(10, draw_shapes) # Execute draw_shapes after a 10 ms delay

        return


    # This piece of code is particulary interesting because it triggers the function above everytime one of the chosen widgets is used
    for widget in [beam_energy,thickness_mod,nneutrons,distance_rpc_beam,distance_rpc, nnrpc]:
        widget.bind('<KeyRelease>', automatic_update)
    for widget in [drop_units]:
        widget.bind('<Configure>', automatic_update)
    for widget in [moderators, check_axis, side_moderators, nnrpc]:
        widget.bind('<ButtonRelease-1>', automatic_update)

    # The buttons
    button_save = tk.Button(frame_final, text = "Save file",font=("TkDefaultFont", 12, 'bold'), command =  lambda:run_topas(None)).pack(padx=60,side=tk.LEFT)
    button_view = tk.Button(frame_final, text = "View content",font=("TkDefaultFont", 12, 'bold'), command = lambda:run_topas(False)).pack(padx=60,side=tk.LEFT)
    button_open = tk.Button(frame_final, text = "Open with TOPAS",font=("TkDefaultFont", 12, 'bold'), command = lambda:run_topas(True)).pack(padx=60,side=tk.LEFT)

    # Now we'll increase the size of every widget to make the interface bigger
    for widget in [check_axis, label_rpc, nnrpc, label_beamdist, distance_rpc_beam, moderators, side_moderators, label_thick,
                   thickness_mod, label_dist, distance_rpc, label_beamenergy, beam_energy, drop_units, label_nneutrons, 
                   nneutrons, filename_label]:
        widget.config(font=my_font)

    # To open everything
    main.mainloop()

    return

# To run the function
interface()
