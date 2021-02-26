def organise_memory_data(data):
    string = ""
    s = ''
    index = 0x0000
    for i in range(1,len(data)+1):
        val_text =  hex(data[i-1]).replace("0x",'')
        val_text = "0"*(2-len(val_text))+val_text+' '
        s += val_text
        
        if i%16==0:
            index_string = hex(index).replace("0x",'')
            index_string = '$'+"0"*(4-len(index_string))+index_string+'  '
            string += index_string+s+"\n"
            s=''
            index += 16
            if index==0x0100:
                string+="\t\t*STACK BEGIN*\n"
            elif index==0x0200:
                string+="\t\t*STACK END*\n"
                
    return string
def adjustfontsize(event):
    global fontsize
    screen_width = root.winfo_width()
    screen_height = root.winfo_height()
    percentage_width = screen_width / (WIDTH / 100)
    percentage_height = screen_height / (HEIGHT / 100)
    scale_factor = ((percentage_width + percentage_height) / 2) / 100
    fontsize = int(14 * scale_factor)
    fontsize_small = int(10*scale_factor)
    minimum_size = 2
    if fontsize < minimum_size:
        fontsize = minimum_size
    if fontsize_small < 1:
        fontsize_small = 1
    
    tk.Label(reg_frame,text="A:",bg=reg_bg,fg="#ffffff",font=("Courier", fontsize)).place(relx=0.06,rely=0.09,relwidth=0.06,relheight=0.12,anchor="nw")
    tk.Label(reg_frame,text="X:",bg=reg_bg,fg="#ffffff",font=("Courier", fontsize)).place(relx=0.06,rely=0.29,relwidth=0.06,relheight=0.12,anchor="nw")
    tk.Label(reg_frame,text="Y:",bg=reg_bg,fg="#ffffff",font=("Courier", fontsize)).place(relx=0.06,rely=0.49,relwidth=0.06,relheight=0.12,anchor="nw")
    tk.Label(reg_frame,text="PC:",bg=reg_bg,fg="#ffffff",font=("Courier", fontsize)).place(relx=0.62,rely=0.09,relwidth=0.075,relheight=0.12,anchor="nw")
    tk.Label(reg_frame,text="SP:",bg=reg_bg,fg="#ffffff",font=("Courier", fontsize)).place(relx=0.62,rely=0.29,relwidth=0.075,relheight=0.12,anchor="nw")
    
    
    tk.Label(reg_frame,text="N",bg=reg_bg,fg="#ffffff",font=("Courier", fontsize-1)).place(relx=0.24,rely=0.78,relwidth=0.045,relheight=0.1,anchor="nw")
    tk.Label(reg_frame,text="V",bg=reg_bg,fg="#ffffff",font=("Courier", fontsize-1)).place(relx=0.31,rely=0.78,relwidth=0.045,relheight=0.1,anchor="nw")
    tk.Label(reg_frame,text="-",bg=reg_bg,fg="#ffffff",font=("Courier", fontsize-1)).place(relx=0.38,rely=0.78,relwidth=0.045,relheight=0.1,anchor="nw")
    tk.Label(reg_frame,text="B",bg=reg_bg,fg="#ffffff",font=("Courier", fontsize-1)).place(relx=0.45,rely=0.78,relwidth=0.045,relheight=0.1,anchor="nw")
    tk.Label(reg_frame,text="D",bg=reg_bg,fg="#ffffff",font=("Courier", fontsize-1)).place(relx=0.52,rely=0.78,relwidth=0.045,relheight=0.1,anchor="nw")
    tk.Label(reg_frame,text="I",bg=reg_bg,fg="#ffffff",font=("Courier", fontsize-1)).place(relx=0.59,rely=0.78,relwidth=0.045,relheight=0.1,anchor="nw")
    tk.Label(reg_frame,text="Z",bg=reg_bg,fg="#ffffff",font=("Courier", fontsize-1)).place(relx=0.66,rely=0.78,relwidth=0.045,relheight=0.1,anchor="nw")
    tk.Label(reg_frame,text="C",bg=reg_bg,fg="#ffffff",font=("Courier", fontsize-1)).place(relx=0.73,rely=0.78,relwidth=0.045,relheight=0.1,anchor="nw")
    
    tk.Label(search_frame,text="ADDR:",bg=reg_bg,fg="#ffffff",font=("Courier", fontsize_small)).place(relx=0.46,rely=0.465,relwidth=0.12,anchor="nw")
    tk.Label(search_frame,text="DATA:",bg=reg_bg,fg="#ffffff",font=("Courier", fontsize_small)).place(relx=0.68,rely=0.465,relwidth=0.12,anchor="nw")


# In[11]:


def search(text_widget, keyword, tag):
    
    pos = '1.0'
    keyword=keyword.lower()
    while True:
        idx = text_widget.search(keyword, pos,nocase=1,stopindex= END)
        if not idx:
            break
        if keyword==';':
            eol_index = text_widget.search('\n', idx,END)
            if not eol_index:break
            length = int(eol_index.split('.')[1].strip())-int(idx.split('.')[1].strip())
            pos = '{}+{}c'.format(idx, len(keyword)+length)
            text_widget.tag_add(tag, idx, pos)

        
        elif keyword==':':
            tkn = idx.split('.')
            line = tkn[0].strip()+'.0' 
            length = int(tkn[1].strip())+len(keyword)
            pos = '{}+{}c'.format(line,length)
            text_widget.tag_add(tag, line, pos)

            
        else:
            pos = '{}+{}c'.format(idx, len(keyword))
            text_widget.tag_add(tag, idx, pos)
def scan_for_words(event):
    for tag in prog_text.tag_names():
        prog_text.tag_delete(tag)
    for j in keywords:
        prog_text.tag_config(j, foreground='#ffae00')
    prog_text.tag_config("byte", foreground='#00bbff')
    prog_text.tag_config(".byte", foreground='#00bbff')
    prog_text.tag_config("word", foreground='#00bbff')
    prog_text.tag_config(".word", foreground='#00bbff')
    prog_text.tag_config("org", foreground='#15ff00')
    prog_text.tag_config(".org", foreground='#15ff00')
    prog_text.tag_config(":",foreground="#ff2b2b")
    prog_text.tag_config(";", foreground='#919191')
    for i in keywords+['.byte','byte','.word','word','.org','org',':',';']:  
        search(prog_text,i,i)


# In[12]:


def get_entry(entry_widget,name):
    text = entry_widget.get().replace(" ",'').replace("$","0x").strip()
    text=text.lower()
    if "0x" not in text and text.replace("-",'').isnumeric():
        if abs(int(text))>255:
                raise Exception(f"Error: {name}:{text} - Value cannot exceed 0xFF")
        try:
            val = np.uint8(int(text))
            return val
        except:
            raise Exception(f"Error:Invalid Entry in {name}:{text}")

            
    elif "0x" in text:
        if abs(int(text,16))>255:
                raise Exception(f"Error: {name}:{text} - Value cannot exceed 0xFF")
        try:
            val = np.uint8(int(text,16))
            return val
        except:
            raise Exception(f"Error:Invalid Entry in {name}:{text}")

    
    raise Exception(f"Error:Invalid Entry in {name}:{text}")
        
        
    


# In[13]:


def get_address(widget):
    text = widget.get().replace(" ",'').replace("$","0x").strip()
    text=text.lower()
    if "0x" not in text and text.isnumeric():
        try:
            if int(text)>65535:
                raise Exception(f"Error:Address can't be greater than 0xFFFF!")
            val = np.uint16(int(text))
            return val
        except:
            raise Exception(f"Error:Invalid Address {text} in address box!")

            
    elif text[:2].strip()=="0x":
        try:
            if int(text,16)>65535:
                raise Exception(f"Error:Address can't be greater than 0xFFFF!")
            val = np.uint16(int(text,16))
            return val
        except:
            raise Exception(f"Error:Invalid Address {text} in address box!")
    raise Exception(f"Error:Invalid Address {text} in address box!")

def search_addr():
    try:
        address = get_address(addr_box)
    except Exception as e:
        console_message=default_console_message
        console_message +='\n\n'+str(e)
        update_console(console_message)
        return
    data_box.configure(state=NORMAL)
    data_box.delete(0,END)
    data_box.insert(0,hex(data[address]))
    data_box.configure(state='readonly')
    
    line = (address//16)
    tot_line = (0xFFFF//16)
    
    if address>0xff:line+=1
    if address>0x1ff:line+=1
    if address>0x1150:line-=1
    if address>0x5500:line-=1
    if address>0x9500:line-=1
    if address>0xd500:line-=1
    
    frac = line/tot_line
    
    mem_text.yview_moveto(frac)
    
    
    


# In[14]:


def update_console(text):
    console_text.configure(state='normal')
    console_text.delete("1.0","end")
    console_text.insert(END,text)
    search(console_text, 'Error', 'Error')
    search(console_text, 'successfully', 'successfully')
    console_text.update()
    console_text.configure(state='disabled')
    console_text.see(END)

def assemble_program():
    text = str(prog_text.get(1.0,END))
    if len(text.strip())<1 or text.strip()=='':
        raise Exception("Error: Nothing to assemble")
    result = assembler.assemble(text)
    memory_text = organise_memory_data(result)
    mem_text.configure(state='normal')
    mem_text.delete("1.0","end")
    mem_text.insert(END,memory_text)
    mem_text.update()
    
    PC = (result[0xFFFD]<<8&0xFFFF) | (result[0xFFFC]&0xFF) 
    PC_entry.config(state=NORMAL)
    PC_entry.delete(0,END)
    PC_entry.insert(0,hex(PC))
    PC_entry.config(state="readonly")
    
    mem_text.configure(state='disabled')
    return result
def run():
    global data
    #Clear Console
    console_message = default_console_message
    update_console(console_message)
    
    #Assembly
    console_message += '\n\n'+"Running Assembler..."
    update_console(console_message)
    try:
        result = assemble_program()
    except Exception as e:
        console_message += '\n'+str(e)
        update_console(console_message)
        return
    
    #Run Emulator
    console_message += "\nAssembled Successfully!"+'\n\n'+"Running Emulator..."
    update_console(console_message)
    max_cpu_cycle = 100000
    try:
        m = emu6502.Memory(byte_array = result)
        c = emu6502.CPU(m)
        c.A = get_entry(A_entry,"A")
        c.X = get_entry(X_entry,"X") 
        c.Y = get_entry(Y_entry,"Y")
        c.SP= get_entry(SP_entry,"SP")
        c.N = get_entry(N,"N")
        c.V = get_entry(V,"V")
        c.B = get_entry(B,"B")
        c.D = get_entry(D,"D")
        c.I = get_entry(I,"I")
        c.Z = get_entry(Z,"Z")
        c.C = get_entry(C,"C")
        
        c.execute(max_cpu_cycle,m)
    except Exception as e:
        console_message += '\n'+str(e)
        update_console(console_message)
        return
    console_message+='\n'+"Program built and ran Successfully!"
    update_console(console_message)


    
    A_entry.delete(0,END)
    A_entry.insert(0,hex(c.A))
    X_entry.delete(0,END)
    X_entry.insert(0,hex(c.X))
    Y_entry.delete(0,END)
    Y_entry.insert(0,hex(c.Y))
    PC_entry.config(state=NORMAL)
    PC_entry.delete(0,END)
    PC_entry.insert(0,hex(c.PC))
    PC_entry.config(state="readonly")
    SP_entry.delete(0,END)
    SP_entry.insert(0,hex(c.SP))
    N.delete(0,END)
    N.insert(0,c.N)
    V.delete(0,END)
    V.insert(0,c.V)
    X.delete(0,END)
    X.insert(0,1)
    B.delete(0,END)
    B.insert(0,c.B)
    D.delete(0,END)
    D.insert(0,c.D)
    I.delete(0,END)
    I.insert(0,c.I)
    Z.delete(0,END)
    Z.insert(0,c.Z)
    C.delete(0,END)
    C.insert(0,c.C)
    
    data = m.data
    memory_text = organise_memory_data(m.data)
    mem_text.configure(state='normal')
    mem_text.delete("1.0","end")
    mem_text.insert(END,memory_text)
    mem_text.update()
    mem_text.configure(state='disabled')
    search_addr()

def download_binary():
    console_message = default_console_message
    update_console(console_message)
    console_message += '\n\n'+"Running Assembler..."
    update_console(console_message)
    try:
        result = assemble_program()
    except Exception as e:
        console_message += '\n'+str(e)
        update_console(console_message)
        return
    console_message += '\n'+"Assembled Successfully!"
    update_console(console_message)
    
    file = filedialog.asksaveasfile(mode = "wb",defaultextension='.bin',filetypes=[("Binary file",".bin"),("All files",".*")])
    file.write(result)
    file.close()
    
    console_message += '\n\n'+"Downloaded Successfully!"
    update_console(console_message)
def save():
    console_message=default_console_message
    text = str(prog_text.get(1.0,END))
    if len(text.strip())<1 or text.strip()=='':
        console_message += '\n\n'+"Error: Nothing to save"
        update_console(console_message)
        return
    
    file = filedialog.asksaveasfile(mode = "w",defaultextension='.txt',filetypes=[("Text file",".txt"),("All files",".*")])
    file.write(text)
    file.close()
    console_message=default_console_message
    console_message += '\n\n'+"Downloaded Successfully!"
    update_console(console_message)
def open_file():
    console_text = default_console_message
    try:
        file = filedialog.askopenfilename(title= "Select file",filetypes=[("Text file",".txt"),("All files",".*")])
        with open(file,"r") as f:
                content = f.read()
        prog_text.delete("1.0","end")
        prog_text.insert(END,content)
        prog_text.update()
        scan_for_words('')
        console_text+="\n\n"+"File Opened Successfully!"
        update_console(console_text)
    except:
        console_text+="\n\n"+"Error Opening File!"
        update_console(console_text)


# In[16]:


'''======================MAIN=========================='''

from tkinter import *
import tkinter as tk
from tkinter import filedialog
from Abhays_6502_Assembler import Abhays_6502_Assembler
import emu6502
import numpy as np
assembler = Abhays_6502_Assembler()


HEIGHT,WIDTH = 550,950
root = tk.Tk()
root.title("6502_Emulator")
fontsize=12
data = [0xFF for i in range(1024*64)]
memory_text = organise_memory_data(data)

canvas = tk.Canvas(root,height=HEIGHT,width=WIDTH)
canvas.pack()

reg_bg = "#3b3232"

reg_frame = tk.Frame(root,bg=reg_bg)    ##80c1ff
reg_frame.place(relwidth=0.4,relheight=0.3,anchor="nw")

search_frame = tk.Frame(root,bg=reg_bg)
search_frame.place(rely=0.3 ,relwidth=0.4,relheight=0.1,anchor="nw")

mem_frame = tk.Frame(root,bg="#ffffff")
mem_frame.place(rely=0.4 ,relwidth=0.4,relheight=0.6,anchor="nw")

prog_frame = tk.Frame(root,bg="#ffffff")
prog_frame.place(relx=0.4,relwidth=0.6,rely=0.05,relheight=0.8)

bar_frame = tk.Frame(root,bg="#050505")
bar_frame.place(relx=0.4,relwidth=0.6,relheight=0.05)


console_frame = tk.Frame(root,bg="#4d4d4d")
console_frame.place(relx=0.4,rely=0.85,relwidth=0.45,relheight=0.15)

button_frame = tk.Frame(root,bg="#3b3232")
button_frame.place(relx=0.85,rely=0.85,relwidth=0.15,relheight=0.15)




#=======MEMORY_FRAME============
scrollbar_mem_y = Scrollbar(mem_frame)
scrollbar_mem_y.pack( side = RIGHT, fill = Y )
scrollbar_mem_x = Scrollbar(mem_frame,orient="horizontal")
scrollbar_mem_x.pack( side = BOTTOM, fill = X )
mem_text = tk.Text(mem_frame,wrap=NONE,bg="#151515",fg="#ffffff",yscrollcommand=scrollbar_mem_y.set,xscrollcommand = scrollbar_mem_x.set)
mem_text.insert(END,memory_text)
mem_text.configure(state='disabled')
mem_text.pack( side = TOP,fill=BOTH,expand="true")
scrollbar_mem_y.config( command = mem_text.yview )
scrollbar_mem_x.config( command = mem_text.xview )

#=======PROGRAM_FRAME===========
keywords=assembler.get_keywords()
scrollbar_prog_y = Scrollbar(prog_frame)
scrollbar_prog_y.pack( side = RIGHT, fill = Y )
scrollbar_prog_x = Scrollbar(prog_frame,orient="horizontal")
scrollbar_prog_x.pack( side = BOTTOM, fill = X )
prog_text = tk.Text(prog_frame,bg="#050505",fg="#f5f5f5",insertbackground='#f5f5f5',padx=5,undo=True,autoseparators=True,maxundo=-1,bd=2,wrap=NONE,font=("Courier", 13),yscrollcommand=scrollbar_prog_y.set,xscrollcommand = scrollbar_prog_x.set)
prog_text.bind('<KeyRelease>',scan_for_words)
prog_text.insert(END,'')    
prog_text.pack( side = TOP,fill=BOTH,expand="true")
scrollbar_prog_y.config( command = prog_text.yview )
scrollbar_prog_x.config( command = prog_text.xview)

#=======REGISTER_FRAME===========
reg_frame.bind('<Configure>',adjustfontsize)
A_entry = tk.Entry(reg_frame,bd = 2)
A_entry.place(relwidth=0.18,relheight=0.12,relx=0.12,rely=0.1,anchor="nw")
A_entry.insert(0,hex(0))
X_entry = tk.Entry(reg_frame,bd = 2)
X_entry.place(relwidth=0.18,relheight=0.12,relx=0.12,rely=0.3,anchor="nw")
X_entry.insert(0,hex(0))
Y_entry = tk.Entry(reg_frame,bd = 2)
Y_entry.place(relwidth=0.18,relheight=0.12,relx=0.12,rely=0.5,anchor="nw")
Y_entry.insert(0,hex(0))

PC_entry = tk.Entry(reg_frame,bd = 2)
PC_entry.place(relwidth=0.18,relheight=0.12,relx=0.7,rely=0.1,anchor="nw")
PC_entry.insert(0,'-')
PC_entry.config(state="readonly")
SP_entry = tk.Entry(reg_frame,bd = 2)
SP_entry.place(relwidth=0.18,relheight=0.12,relx=0.7,rely=0.3,anchor="nw")
SP_entry.insert(0,hex(0xFF))

#=======FLAGS===========
N= tk.Entry(reg_frame,bd = 2)
N.place(relwidth=0.05,relheight=0.12,relx=0.23,rely=0.88,anchor="nw")
N.insert(0,0)
V = tk.Entry(reg_frame,bd = 2)
V.place(relwidth=0.05,relheight=0.12,relx=0.30,rely=0.88,anchor="nw")
V.insert(0,0)
X = tk.Entry(reg_frame,bd = 2)
X.place(relwidth=0.05,relheight=0.12,relx=0.37,rely=0.88,anchor="nw")
X.insert(0,1)
B = tk.Entry(reg_frame,bd = 2)
B.place(relwidth=0.05,relheight=0.12,relx=0.44,rely=0.88,anchor="nw")
B.insert(0,0)
D = tk.Entry(reg_frame,bd = 2)
D.place(relwidth=0.05,relheight=0.12,relx=0.51,rely=0.88,anchor="nw")
D.insert(0,0)
I = tk.Entry(reg_frame,bd = 2)
I.place(relwidth=0.05,relheight=0.12,relx=0.58,rely=0.88,anchor="nw")
I.insert(0,0)
Z = tk.Entry(reg_frame,bd = 2)
Z.place(relwidth=0.05,relheight=0.12,relx=0.65,rely=0.88,anchor="nw")
Z.insert(0,0)
C = tk.Entry(reg_frame,bd = 2)
C.place(relwidth=0.05,relheight=0.12,relx=0.72,rely=0.88,anchor="nw")
C.insert(0,0)



#=======CONSOLE===========
default_console_message = "6502 Emulator-Created by Abhay Chirania(SRM IST)"
console_message = default_console_message

scrollbar_console = Scrollbar(button_frame)
scrollbar_console.pack( side = RIGHT, fill = Y )
console_text = tk.Text(console_frame,font=("Helvetica", 10,"bold"),padx=5,bg="#3b3232",fg="#ffffff",yscrollcommand=scrollbar_console.set)
console_text.insert(END,console_message)
console_text.tag_config('Error', foreground='#ff2e2e')
console_text.tag_config('successfully', foreground='#3bde04')
console_text.configure(state='disabled')
scrollbar_console.config( command = console_text.yview )
#console_text.place( relwidth=0.65,anchor="nw")

console_text.pack( side = TOP,fill=BOTH,expand="true")

#=======SEARCH===========


addr_box= tk.Entry(search_frame,bd = 2)
addr_box.place(relwidth=0.1,relheight=0.4,relx=0.58,rely=0.45,anchor="nw")
addr_box.insert(0,"0x0000")

data_box= tk.Entry(search_frame,bd = 2)
data_box.place(relwidth=0.1,relheight=0.4,relx=0.8,rely=0.45,anchor="nw")
data_box.insert(0,"0xff")
data_box.configure(state='readonly')

search_button = tk.Button(search_frame,bd=2,text=">>",command=search_addr)
search_button.place(relx=0.92,rely=0.45,relwidth=0.06,relheight=0.4,anchor="nw")

#=======BUTTONS===========
download_button = tk.Button(button_frame,bd=2,text="Download binary",command=download_binary)
download_button.place(relx=0.05,rely=0.65,relwidth=0.75,relheight=0.28,anchor="nw")

single_step_button = tk.Button(button_frame,bd=2,text="Single Step")
single_step_button.place(relx=0.05,rely=0.35,relwidth=0.75,relheight=0.28,anchor="nw")

run_button = tk.Button(button_frame,bd=2,text="Run",command=run)
run_button.place(relx=0.05,rely=0.05,relwidth=0.75,relheight=0.28,anchor="nw")

save_button = tk.Button(bar_frame,bd=2,text="Save",command=save)
save_button.place(relx=0.01,rely=0.08,relwidth=0.1,relheight=0.84,anchor="nw")
open_button = tk.Button(bar_frame,bd=2,text="Open",command=open_file)
open_button.place(relx=0.12,rely=0.08,relwidth=0.1,relheight=0.84,anchor="nw")

prog_text.focus()
prog_text.update()

mainloop()

