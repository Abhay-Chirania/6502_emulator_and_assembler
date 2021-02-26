#!/usr/bin/env python
# coding: utf-8

# In[12]:


opcodes = {
                "lda":{"IM":0xA9,"ZP":0xA5,"ZPX":0xB5,"ABS":0xAD,"ABSX":0xBD,"ABSY":0xB9,"INDX":0xA1,"INDY":0xB1},
                "ldx":{"IM":0xA2,"ZP":0xA6,"ZPY":0xB6,"ABS":0xAE,"ABSY":0xBE},
                "ldy":{"IM":0xA0,"ZP":0xA4,"ZPX":0xB4,"ABS":0xAC,"ABSY":0xBC},
                "sta":{"ZP":0x85,"ZPX":0x95,"ABS":0x8D,"ABSX":0x9D,"ABSY":0x99,"INDX":0x81,"INDY":0x91},
                "stx":{"ZP":0x86,"ZPY":0x96,"ABS":0x8E},
                "sty":{"ZP":0x84,"ZPX":0x94,"ABS":0x8C},
                "tax":{"IMPL":0xAA},
                "tay":{"IMPL":0xA8},
                "txa":{"IMPL":0x8A},
                "tya":{"IMPL":0x98},
                "tsx":{"IMPL":0xBA},
                "txs":{"IMPL":0x9A},
                "pha":{"IMPL":0x48},
                "pla":{"IMPL":0x68},
                "php":{"IMPL":0x08},
                "plp":{"IMPL":0x28},
                "clc":{"IMPL":0x18},
                "cld":{"IMPL":0xD8},
                "cli":{"IMPL":0x58},
                "clv":{"IMPL":0xB8},
                "sec":{"IMPL":0x38},
                "sed":{"IMPL":0xF8},
                "sei":{"IMPL":0x78},
                "and":{"IM":0x29,"ZP":0x25,"ZPX":0x35,"ABS":0x2D,"ABSX":0x3D,"ABSY":0x39,"INDX":0x21,"INDY":0x31},
                "ora":{"IM":0x09,"ZP":0x05,"ZPX":0x15,"ABS":0x0D,"ABSX":0x1D,"ABSY":0x19,"INDX":0x01,"INDY":0x11},
                "eor":{"IM":0x49,"ZP":0x45,"ZPX":0x55,"ABS":0x4D,"ABSX":0x5D,"ABSY":0x59,"INDX":0x41,"INDY":0x51},
                "bit":{"ZP":0x24,"ABS":0x2C},
                "brk":{"IMPL":0x00},
                "nop":{"IMPL":0xEA},
                "rti":{"IMPL":0x40},
                "inx":{"IMPL":0xE8},
                "iny":{"IMPL":0xC8},
                "dex":{"IMPL":0xCA},
                "dey":{"IMPL":0x88},
                "inc":{"ZP":0xE6,"ZPX":0xF6,"ABS":0xEE,"ABSX":0xFE},
                "dec":{"ZP":0xC6,"ZPX":0xD6,"ABS":0xCE,"ABSX":0xDE},
                "jmp":{"ABS":0x4C , "IND":0x6C},
                #TEST
                "jsr":{"ABS":0x20}, #Check this
                "rts":{"IMPL":0x60},
        
                "asl":{"ACC":0x0A,"ZP":0x06,"ZPX":0x16,"ABS":0x0E,"ABSX":0x1E},
                "lsr":{"ACC":0x4A,"ZP":0x46,"ZPX":0x56,"ABS":0x4E,"ABSX":0x5E},
                "rol":{"ACC":0x2A,"ZP":0x26,"ZPX":0x36,"ABS":0x2E,"ABSX":0x3E},
                "ror":{"ACC":0x6A,"ZP":0x66,"ZPX":0x76,"ABS":0x6E,"ABSX":0x7E},
                
                "adc":{"IM":0x69,"ZP":0x65,"ZPX":0x75,"ABS":0x6D,"ABSX":0x7D,"ABSY":0x79,"INDX":0x61,"INDY":0x71},
                "sbc":{"IM":0xE9,"ZP":0xE5,"ZPX":0xF5,"ABS":0xED,"ABSX":0xFD,"ABSY":0xF9,"INDX":0xE1,"INDY":0xF1},
                "cmp":{"IM":0xC9,"ZP":0xC5,"ZPX":0xD5,"ABS":0xCD,"ABSX":0xDD,"ABSY":0xD9,"INDX":0xC1,"INDY":0xD1},
                "cpx":{"IM":0xE0,"ZP":0xE4,"ABS":0xEC},
                "cpy":{"IM":0xC0,"ZP":0xC4,"ABS":0xCC},
        
                "bcc":{"IM":0x90},
                "bcs":{"IM":0xB0},
                "beq":{"IM":0xF0},
                "bmi":{"IM":0x30},
                "bne":{"IM":0xD0},
                "bpl":{"IM":0x10},
                "bvc":{"IM":0x50},
                "bvs":{"IM":0x70}
              }


# In[13]:


def split_acc_to_org(program):
    
    x = []
    
    start = 0
    i=0
    start_address = [0x00,0x02]
    while i<len(program):
        a = program[i].strip().split(" ")[0].strip()
        if a == "org" or a==".org":
            x.append((start_address,program[start:i]))
            start_address = get_start_address(program[i].strip().split(" "))
            start = i+1
        i+=1
    if start!=0:
        start_address = get_start_address(program[start-1].strip().split(" "))
    x.append((start_address,program[start:]))
    x = [i for i in x if i[1]]
    return x


# In[14]:


def get_start_address(a):
    start_address = []
    val  = 0x0200
    t = [j.strip() for j in a if j!=""]
    if len(t)!=2:
        raise Exception(f"Error: \"{a.strip()}\"<-Syntax Error! ")
    if t[1].isnumeric():
        val = int(t[1])
    elif t[1][0].strip() == "$" or t[1][0:2]=="0x":
        t[1] = t[1].replace("$","0x")
        val = int(t[1],16)
    else:
        raise Exception(f"Error: \"{a.strip()}\" is non numeric or hexadecimal")
    if val>65535:
        raise Exception("Error: \"{a.strip()}\" has greater than 0xFFFF")
            
    val = hex(val)
    val = val.replace("0x","")
    val  = "0"*(4-(len(val)))+val
    a,b = "0x"+val[0:math.floor(len(val)/2)] , "0x"+val[math.floor(len(val)/2):]
    start_address.append(int(b,16))
    start_address.append(int(a,16))
    #start_address.append(b)
    #start_address.append(a)
    return start_address


# In[15]:


def get_mode(x):
    x = x.replace("$","0x")
    x = x.replace(" ",',')
    x = x.split(",")
    x = [i.strip() for i in x if i!='']
    #print(x)
    if len(x)>3:
        return False

    if len(x)==2 and x[1][0]=="#":
        x = x[1].replace("#","")
        if x[:2]!="0x" and x.isnumeric():
            x = hex(int(x))
        #if np.uint8(int(x,16))>0xFF:return False
        return ("IM",x)
    elif len(x)==2 and 0<len(x[1].replace("0x",""))<=2:
        return ("ZP",x[1])
    elif len(x)==3 and x[2]=="x" and 0<len(x[1].replace("0x",""))<=2:
        return ("ZPX",x[1])
    elif len(x)==3 and x[2]=="y" and 0<len(x[1].replace("0x",""))<=2:
        return ("ZPY",x[1])
    elif len(x)==2 and 2<len(x[1].replace("0x","")) and "(" not in x[1] and ")" not in x[1]:
        return ("ABS",x[1])
    elif len(x)==3 and "(" not in x[1] and ")" not in x[1] and 2<len(x[1].replace("0x","")) and x[2]=="x":
        return ("ABSX",x[1])
    elif len(x)==3 and "(" not in x[1] and ")" not in x[1] and 2<len(x[1].replace("0x","")) and x[2]=="y":
        return ("ABSY",x[1])
    elif len(x)==3 and "x" in x[2] and x[1][0]=="(" and x[2][-1]==")":
        x = x[1].replace("(","")
        if x[:2]!="0x" and x.isnumeric():
            x = hex(int(x))
        #if np.uint8(int(x,16))>0xFF:return False
        return ("INDX",x)
    elif len(x)==3 and  x[2]=="y" and x[1][0]=="(" and x[1][-1]==")":
        x = x[1].replace("(","")
        x = x.replace(")","")
        x = x.strip()
        if x[:2]!="0x" and x.isnumeric():
            x = hex(int(x))
        #if np.uint8(int(x,16)) >0xFF:return False
        return ("INDY",x)
    elif x[0].strip()=="jmp" and len(x)==2 and x[1][0]=="(" and x[1][-1]==")":
        x = x[1].replace("(","")
        x = x.replace(")","")
        x = x.strip()
        if x[:2]!="0x" and x.isnumeric():
            x = hex(int(x))
        #if np.uint8(int(x,16))>0xFFFF:x=hex(0xFFFF)
        x = x.replace("0x","")
        x  = "0x"+"0"*(4-(len(x)))+x
        return ("IND",x)
    
    return False


# In[16]:


def convert(program,line_offset=0):

  
    '''
    program = program.lower()
    program = program.splitlines()
    for i in range(len(program)):
            if ';' in program[i]:
                idx = program[i].index(';')
                program[i] = program[i][:idx]
    '''
    program = [i.strip() for i in program if i!='' ]
    pgm = []
    #print(program)
    for line_no , i in enumerate(program):
        try:
            tokenize =i.strip().split(" ")
            tokenize = [k.strip() for k in tokenize if k!='']
            if tokenize[0] not in opcodes and tokenize[0]!="byte" and tokenize[0]!=".byte" and tokenize[0]!="word" and tokenize[0]!=".word":
                raise Exception(f"Error: Line {line_no+line_offset+1} - {tokenize[0]} is not a valid command!")
               
            op = tokenize[0].strip()
            
            if op=="byte" or op==".byte" :
                if len(tokenize)!=2:raise Exception(f"Error: Line {line_no+line_offset+1}")
                val = tokenize[1].replace("$","0x").strip()
                t = int(val,16) if "0x" in val else int(val)
                if abs(t)>0xFF:raise Exception(f"Error: Line {line_no+line_offset+1} - Value greater than 0xFF")
                if "0x" not in val:
                    val = hex(np.uint8(int(val)))
                val = val.replace("0x","")
                pgm.append(np.uint8(int(val,16)))
                continue
            elif op=="word" or op==".word":
                val = tokenize[1].replace("$","0x").strip()
                t = int(val,16) if "0x" in val else int(val)
                if abs(t)>0xFFFF:raise Exception(f"Error: Line {line_no+line_offset+1} - Value greater than 0xFFFF")
                if "0x" not in val:
                        val = hex(np.uint16(int(val)))
                val = hex(np.uint16(int(val,16)))
                val = val.replace("0x","")
                val = "0"*(4-len(val))+val
                a,b = "0x"+val[0:math.floor(len(val)/2)] , "0x"+val[math.floor(len(val)/2):]
                pgm.append(np.uint8(int(b,16)))
                pgm.append(np.uint8(int(a,16)))
                continue
                
            if len(tokenize)==1:
                pgm.append(opcodes[tokenize[0]]["IMPL"])
                continue
            
            
            if op=="asl" or op=="lsr" or op=="rol" or op=="ror":
                if tokenize[1].strip()=="a":
                    pgm.append(opcodes[op]["ACC"])
                    continue
    
                
                
                
            
            
            var = get_mode(i)
            #print(var)
            if not var: raise Exception(f"Error: Line {line_no+line_offset+1}")
            addr,val = var
            
            if addr=="IM" or addr=="ZP" or addr=="ZPX" or addr=="ZPY" or addr=="INDX" or addr=="INDY":
                t = int(val,16) if "0x" in val else int(val)
                if abs(t)>0xFF:raise Exception(f"Error: Line {line_no+line_offset+1} - Value greater than 0xFF")
                t = np.uint8(t)
                pgm.append(opcodes[op][addr])
                if "0x" not in val:
                    val = hex(np.uint8(int(val)))
                val = val.replace("0x","")
                pgm.append(np.uint8(int(val,16)))
                
            elif addr=="ABS" or addr=="ABSX" or addr=="ABSY" or addr=="IND":
                t = int(val,16) if "0x" in val else int(val)
                if abs(t)>0xFFFF:raise Exception(f"Error: Line {line_no+line_offset+1} - Value greater than 0xFFFF")
                t = np.uint16(t)
                pgm.append(opcodes[op][addr])
                if "0x" not in val:
                        val = hex(np.uint16(int(val)))
                val = hex(np.uint16(int(val,16)))
                val = val.replace("0x","")
                val = "0"*(4-len(val))+val
                a,b = "0x"+val[0:math.floor(len(val)/2)] , "0x"+val[math.floor(len(val)/2):]
                pgm.append(np.uint8(int(b,16)))
                pgm.append(np.uint8(int(a,16)))
            else:
                raise Exception(f"Error: Line {line_no+line_offset+1}")

        except Exception as e:
            #print(e)
            raise Exception(f"Error: Line {line_no+line_offset+1}")
        
    return pgm


# In[17]:


def get_labels(program,prevstart):
    labels = []
    i=0
    while i < len(program):
        if program[i][-1].strip()==':':
            program[i] += program[i+1]
            del program[i+1]
        
        i+=1
        
    for i in program:
        if i.count(":")>=2:
            raise Exception(f"Error: Label - \"{i}\" ")
    start = prevstart
    line_no = []
    for i in range(len(program)):
        x = program[i].strip()
        token =x.strip().split(" ")
        #if token[0].strip() == "bcc" or token[0].strip() == "bcs" or token[0].strip() == "beq" or token[0].strip() == "bmi" or token[0].strip() == "bne" or token[0].strip() == "bpl" or token[0].strip() == "bvc" or token[0].strip() == "bvs":
        line_no.append([start,program[i].strip()])
        
        if ':' in program[i]:
            idx = program[i].index(':')
            label = program[i][:idx].strip()
            if " " in label:
                raise Exception(f"Error: Line {i+1} - Label cannot have space")
            if label in opcodes.keys() or label.startswith("org") or label.startswith(".org"):
                raise Exception(f"Error: Line {i+1} - Label cannot be keyword")
            if not any(c.isalpha() for c in label):
                raise Exception(f"Error: Line {i+1} - Label should contain alphabet!")
            program[i] = program[i][idx+1:].strip()
            val = start #if start==prevstart else start+1
            labels.append([label,val])
        if program[i]!='':
            x = program[i].strip()
            
            tokenize =x.strip().split(" ")
            tokenize = [k.strip() for k in tokenize if k!='']
            if tokenize[0] not in opcodes and tokenize[0]!="byte" and tokenize[0]!=".byte" and tokenize[0]!="word" and tokenize[0]!=".word":
                raise Exception(f"Error: Line {i+1} - {tokenize[0]} is not a valid command!")
            
            if tokenize[0]=="word" or tokenize[0]==".word":
                start+=2
            elif tokenize[0]=="byte" or tokenize[0]==".byte" or "IMPL" in opcodes[tokenize[0]]  :
                start+=1
            
            
            elif tokenize[0]=="jmp" or tokenize[0]=="jsr":
                start+=3
            
            elif tokenize[0]=="bcc" or tokenize[0]=="bcs" or tokenize[0]=="beq" or tokenize[0]=="bmi" or tokenize[0]=="bne" or tokenize[0]=="bpl" or tokenize[0]=="bvc" or tokenize[0]=="bvs":
                start+=2
                
            else:
                mode = get_mode(program[i])
                if not mode:raise Exception(f"Error: Line {i+1} - \"{program[i]}\"")    

                if mode[0] == "IM" or mode[0] == "ZP" or mode[0] == "ZPX" or mode[0] == "ZPY" or mode[0] == "INDX" or mode[0] == "INDY":
                    start += 2
                elif mode[0] == "IMPL":
                    start += 1
                elif mode[0] == "ABS" or mode[0]=="ABSX" or mode[0]=="ABSY":
                    start += 3
    #print(line_no)
    #print(labels)
    return line_no,labels,program


# In[18]:


def substitute_for_label(labels,program,all_line_no):
    #print(program)
    #print(all_line_no)
    for i in labels:
        label_name,label_val = i
        
        for j in range(len(program)):
            rel_val = 0
            token = [k.strip() for k in program[j].strip().replace(","," ").replace("(","").replace(")","").replace("#","").split(" ") if k!='']
            if any(label_name == c for c in token):
                if token[0].strip() == "bcc" or token[0].strip() == "bcs" or token[0].strip() == "beq" or token[0].strip() == "bmi" or token[0].strip() == "bne" or token[0].strip() == "bpl" or token[0].strip() == "bvc" or token[0].strip() == "bvs":
                    for p in range(len(all_line_no)):
                        if all_line_no[p][1].strip()==program[j].strip():
                            line_val = all_line_no[p][0]
                            all_line_no.pop(p)
                            break
                    if "0x" in str(label_val).strip():
                        label_val = np.uint16(int(label_val,16))
                    if label_val<line_val:
                        #print(label_name , line_val)
                        rel_val = label_val-line_val-2
                    elif label_val>=line_val:
                        rel_val = label_val-line_val-2
                    rel_val = np.uint8(rel_val)
                    if rel_val>0xFF:raise Exception(f"Error: {program[j].strip()} - Branch Value exceeds 255!")

                    program[j] = program[j].replace(label_name,hex(rel_val).replace("0x","#$").strip())
                    #print(program[j])

                else:
                    label_val = str(label_val).strip()
                    if "0x" not in label_val: 
                        label_val = hex(np.uint16(int(label_val)))
                    label_val = hex(np.uint16(int(label_val,16)))
                    label_val = label_val.replace("0x","")
                    label_val = "0x"+("0"*(4-len(label_val)))+label_val
                    program[j] = program[j].replace(label_name,label_val.replace("0x","$").strip())
    return program


# In[19]:


def start_assembly(program):
    program = program.lower().replace("\t"," ")
    program = program.splitlines()
    for i in range(len(program)):
            if ';' in program[i]:
                program[i] = program[i].strip()
                idx = program[i].index(';')
                program[i] = program[i][:idx]
    program = [i.strip() for i in program if i!='' ]
    program = split_acc_to_org(program)
    
    all_labels = []
    all_program = []
    all_line_no = []
    for j,i in enumerate(program):
        start = i[0][1]<<8|i[0][0]
        t = [k.strip() for k in i[1] if k!='']
        line_no,labels,prog = get_labels(t,start)
        prog = [k.strip() for k in prog if k!='']
        #print(labels)
        all_program.append((i[0],prog))
        all_labels+=labels
        all_line_no += line_no
    
    for i in range(len(all_labels)):
        for j in range(i+1,len(all_labels)):
            if i==j:continue
            if all_labels[i][0] == all_labels[j][0]:
                raise Exception(f"Error: Duplicate label \"{all_labels[i][0]}\" ")
                break
    
    for j,i in enumerate(all_program):
        pgm = substitute_for_label(all_labels,i[1],all_line_no)
        all_program[j] = (i[0],pgm)
        
    #print(all_program,all_labels)
  
    code = []
    offset = int(not(all_program[0][0][0]==0 and all_program[0][0][1]==2))
   
    for i in all_program:
        prog = [j.strip() for j in i[1] if j!='' ]
        code.append(i[0]+convert(prog,line_offset=offset))
        offset += len(i[1])+1
    return code


# In[20]:


import math
import numpy as np
    
class Abhays_6502_Assembler(object):
    def assemble(self,program):
        self.result = start_assembly(program)
        self.binary = self.make_binary(self.result)
        return self.binary
    def make_binary(self,prog):
        max_mem = 1024*64
        data = [0xFF for i in range(max_mem)]
        for x in  prog:
            start = (x[1]<<8 & 0xFFFF) | (x[0]&0xFF)
            for i in x[2:]:
                data[start]=i
                start += 1

        data[0xFFFC] = prog[0][0]
        data[0xFFFD] = prog[0][1]
        data = bytearray(data)
        return data
    def get_keywords(self):
        return list(opcodes.keys())


# In[ ]:




