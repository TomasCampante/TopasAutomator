import tkinter as tk
from tkinter import messagebox
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
            aux.inbetween('2.5 eV', '6 MeV', str(beam_energy.get())+' '+str(units.get()), 'eV')
            
            file_manipulator(boolean)
        except AssertionError:
            messagebox.showerror("Error", "Inserted values do not respect the asked range.\nRe-input the beam's energy.")
        except ValueError:
            messagebox.showerror("Error", "Most entries accept integers or floats, although make sure the number of neutrons is an integer!")
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
                    to_write[index]=line[:2+line.find('=')]+str(5+float(distance_rpc.get())*float(nnrpc.get()))+line[line.find(' cm'):]
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
                    to_write[index]=line[:2+line.find('=')]+str(5+0.2*float(nnrpc.get())+float(thickness_mod.get())*(float(nnrpc.get())+1))+line[line.find(' cm'):]
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
                #print(mods_lines)
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
                        #print(newline)
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
            filename='rpc-'+str(nnrpc.get())+'_moderators-'+str(moderator.get())+'_sidemoderators-'+str(side_moderator.get())+'_'+str(thickness_mod.get())+'cm_'+str(beam_energy.get())+str(units.get())+".txt"
        else:
            filename='rpc-'+str(nnrpc.get())+'_moderators-'+str(moderator.get())+'_'+str(beam_energy.get())+str(units.get())+".txt"
        newfile=open(filename, 'w') 
        newfile.writelines(to_write)
        newfile.close()

	    # When the program is being run in the terminal (!), it will open the file or TOPAS with the file that was created.
        if boolean:
            subprocess.call('bash -i -c "topas '+filename+'"', shell=True)
        else:
            system=aux.opsys()
            if system == 'Windows':
                subprocess.call('start ' +filename, shell=True)
            elif system == 'Darwin':
                subprocess.call('open ' +filename, shell=True)
            elif system == 'Linux':
                subprocess.call('xdg-open ' +filename, shell=True)
            else:
                messagebox.showerror("Error", "It was not possible to open the file\nbecause we could not identify your operative system.")
                
         
        return    
            
    ####################################################################################################################################
        
    '''
                GUI's WIDGETS
    '''


    # Generating the main window
    main = tk.Tk()
    main.geometry('750x350')
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
    frame_logos.pack(padx=15,side=tk.RIGHT, fill=tk.Y)

    # Processing the logos
    logos = Image.open("DoNotDelete/logos_nobg.png")
    logos.thumbnail((150,150))
    logos = ImageTk.PhotoImage(logos)
    logos_label = tk.Label(frame_logos, image = logos)
    logos_label.image = logos
    logos_label.pack(side=tk.TOP, anchor=tk.NE)

    # The following code creates the widgets necessary to receive the inputs from the user
    frame_initialsettings=tk.Frame(main)
    frame_initialsettings.pack(pady=(10,0))

    axis=tk.StringVar()
    ##axis.set('Axis')
    ##check_axis=tk.OptionMenu(frame_initialsettings, axis, 'On', 'Off')
    ##check_axis.pack()
    check_axis = tk.Checkbutton(frame_initialsettings, text='Do you want to see the axes in the simulation?', variable=axis, offvalue='Off', onvalue='On')
    check_axis.select() 
    check_axis.pack()

    ##nnrpc=tk.StringVar()
    ##nnrpc.set('Number of nRPCs')
    ##drop_rpcs=tk.OptionMenu(frame_initialsettings, nnrpc, 1, 3, 5, 10)
    ##drop_rpcs.pack()
    
    label = tk.Label(frame_initialsettings, text="Number of nRPCs:")
    label.pack(side=tk.LEFT)

    nnrpc = tk.Scale(frame_initialsettings, from_=1, to=10, orient=tk.HORIZONTAL, length=200)
    nnrpc.pack(side=tk.LEFT)
    
    frame_beamdist=tk.Frame(main)
    frame_beamdist.pack()

    label = tk.Label(frame_beamdist, text="Distance between the first RPC and the beam (in cm):")
    label.pack(side=tk.LEFT)

    distance_rpc_beam = tk.Entry(frame_beamdist)
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
    thickness_mod.pack(side=tk.LEFT)

    label_dist = tk.Label(frame_moderators2, text="Distance between nRPCs (in cm):")
    #label_dist.pack(side=tk.LEFT)

    distance_rpc = tk.Entry(frame_moderators2)
    #distance_rpc.pack(side=tk.LEFT)

    frame_beam=tk.Frame(main)
    frame_beam.pack()

    label = tk.Label(frame_beam, text="Beam's energy (from 2.5e-6 to 6 MeV):")
    label.grid(row=0, column=0)

    beam_energy = tk.Entry(frame_beam)
    beam_energy.grid(row=0, column=1)

    units=tk.StringVar()
    units.set('Units')
    drop_units=tk.OptionMenu(frame_beam, units, 'eV', 'keV', 'MeV')
    drop_units.grid(row=0, column=2)

    frame_quantity=tk.Frame(main)
    frame_quantity.pack()

    label = tk.Label(frame_quantity, text="Amount of neutrons in beam:")
    label.pack(side=tk.LEFT)

    nneutrons = tk.Entry(frame_quantity)
    nneutrons.pack(side=tk.LEFT)

    # This final frame is special because it contains a label with the name of the file that will be generated
    # It also contains the two principal buttons, vital do run the program
    frame_final=tk.Frame(main)
    frame_final.pack(pady=(10, 0))

    filename_strvar=tk.StringVar()
    filename_strvar.set('Filename: to_run.txt')
    filename_label= tk.Label(frame_final, textvariable= filename_strvar)
    filename_label.pack(pady=(0,20))

    def update_filename(event=None):

        '''
        Don't mind this function, its only purpose is to keep updating a label.
        '''

        if beam_energy.get()!='' or thickness_mod.get()!='' or nneutrons.get()!='' or distance_rpc_beam.get()!='' or nnrpc.get()!='' or units.get()!='Units':
            if moderator.get()=='True':
                filename_strvar.set('Filename: '+'rpc-'+str(nnrpc.get())+'_moderators-'+str(moderator.get())+'_sidemoderators-'+str(side_moderator.get())+'_'+str(thickness_mod.get())+'cm_'+str(beam_energy.get())+str(units.get())+".txt")
            else:
                filename_strvar.set('Filename: '+'rpc-'+str(nnrpc.get())+'_moderators-'+str(moderator.get())+'_'+str(beam_energy.get())+str(units.get())+".txt")
        else:
            filename_strvar.set('Filename: '+"to_run.txt")

        return


    # This piece of code is particulary interesting because it triggers the function above everytime one of the chosen widgets is used
    for widget in [beam_energy,thickness_mod,nneutrons,distance_rpc_beam,distance_rpc, nnrpc]:
        widget.bind('<KeyRelease>', update_filename)
    for widget in [drop_units]:
        widget.bind('<Configure>', update_filename)
    for widget in [moderators, check_axis, side_moderators]:
        widget.bind('<ButtonRelease-1>', update_filename)

    # The buttons
    button_save = tk.Button(frame_final, text = "View content",font=('bold'), command =  lambda:run_topas(False)).pack(padx=60,side=tk.LEFT)
    button_run = tk.Button(frame_final, text = "Open with TOPAS",font=('bold'), command = lambda:run_topas(True)).pack(padx=60,side=tk.RIGHT)

    # To open everything
    main.mainloop()

    return

# To run the function
interface()
