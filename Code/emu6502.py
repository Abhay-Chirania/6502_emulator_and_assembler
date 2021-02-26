#!/usr/bin/env python
# coding: utf-8

# In[2]:


import numpy as np
class Memory(object):
    def __init__(self,file=None,byte_array = None):
        self.max_mem = 1024*64
        self.data = [0xFF for i in range(self.max_mem)]
        if file:
            try:
                with open(file ,"rb") as f:
                    a = f.read()
                a=list(a)
                if len(a)>self.max_mem:
                    raise Exception(f"{file} cannot be greater than 64KB")
                self.data = a
            except:
                raise Exception(f"Error Opening {file}.")
        elif byte_array:
            try:
                a=list(byte_array)
                if len(a)>self.max_mem:
                    raise Exception(f"Array cannot be greater than 64KB")
                self.data = a
            except:
                raise Exception(f"Error loading bytearray.")
                
        
        
    def reset(self):
        self.data = [0xFF for i in range(self.max_mem)]
    def get(self,addr):
        return self.data[addr]
    def set(self,addr,val):
        self.data[addr] = val
    def write_byte(self,data2write,addr,cycle):
        self.data[addr] = data2write&0xFF
        cycle-=1
        return cycle
    def write_word(self,data2write,addr,cycle):
        self.data[addr] = data2write&0xFF
        self.data[addr+1] = data2write >> 8
        cycle -= 2
        return cycle 

class CPU(object):
    def __init__(self,memory):
        self.reset(memory)
        #memory.reset()
    def reset(self,memory):
        self.PC = (memory.data[0xFFFD]<<8 & 0xFFFF) | (memory.data[0xFFFC]&0xFF)
        self.SP = 0x0FF
        self.A  = self.X = self.Y = 0x00
        self.C  = self.Z = self.I = self.D = self.B = self.V =self.N = 0b0
    def load_program(self,memory,prog):
        for x in  prog:
            start = (x[1]<<8 & 0xFFFF) | (x[0]&0xFF)
            for i in x[2:]:
                m.data[start]=i
                start += 1
                
        m.data[0xFFFC] = prog[0][0]
        m.data[0xFFFD] = prog[0][1]
        self.PC = (m.data[0xFFFD]<<8 & 0xFFFF) | (m.data[0xFFFC]&0xFF)
        
    def get_flag(self):
        f = [self.C,self.Z,self.I,self.D,self.B,0x0,self.V,self.N]
        FLAG = 0X00
        for i in range(8):
            FLAG |= (f[i]<<i)
        return FLAG
    def set_flag(self,data):
        f = [0x0 for _ in range(8)]
        for i in range(8):
            f[i] = 0x1 if data&(1<<i)>0 else 0x0
        self.C,self.Z,self.I,self.D,self.B,_,self.V,self.N  = f        
    def fetch_byte(self,cycle,memory):
        data = memory.get(self.PC)
        self.PC+=1
        cycle -=1
        return cycle,data
    def fetch_word(self,cycle,memory):
        #Endian matters here
        data = memory.get(self.PC) #lsb
        self.PC+=1
        data |= (memory.get(self.PC) << 8) #msb
        self.PC+=1
        cycle -=2
        return cycle,data
    def read_byte(self,cycle,memory,addr):
        data = memory.get(addr)
        cycle -=1
        return cycle,data
    def read_word(self,cycle,memory,addr):
        data = memory.get(addr) #lsb
        data |= (memory.get(addr+1) << 8) #msb
        cycle -=2
        return cycle,data
    
    '''================STACK-OPS=============='''
    def stack_address(self):
        return np.uint16(0x0100|self.SP)
    def pushWordtoStack(self,data,cycle,memory):
        #Takes 3 cycle
        cycle = memory.write_word(data,self.stack_address()-1,cycle)
        self.SP -= 2  
        return cycle-1
    def popWordfromStack(self,cycle,memory):
        #Takes 3 cycle
        cycle,data = self.read_word(cycle,memory,self.stack_address()+1)
        self.SP += 2  
        return cycle-1,data
    def pushBytetoStack(self,data,cycle,memory):
        #Takes 2 cycle
        cycle = memory.write_byte(data,self.stack_address(),cycle)
        self.SP -= 1
        return cycle-1
    def popBytefromStack(self,cycle,memory):
        #Takes 2 cycle
        cycle,data = self.read_byte(cycle,memory,self.stack_address()+1)
        self.SP += 1 
        return cycle-1,data
    
    '''===============Adressing Modes==============='''
    def addr_zp(self,cycle,memory):
        return self.fetch_byte(cycle,memory)
    def addr_zpx(self,cycle,memory):
        cycle,addr = self.fetch_byte(cycle,memory)
        addr=np.uint8(addr+self.X)
        cycle -= 1
        return cycle,addr
    def addr_zpy(self,cycle,memory):
        cycle,addr = self.fetch_byte(cycle,memory)
        addr=np.uint8(addr+self.Y)
        cycle -= 1
        return cycle,addr
    def addr_abs(self,cycle,memory):
        return self.fetch_word(cycle,memory)
    def addr_absx(self,cycle,memory,zp_cross=True):
        cycle,addrabs = self.fetch_word(cycle,memory)
        addr = np.uint16(addrabs+self.X)
        if not zp_cross:cycle -= 1
        elif (addr-addrabs>=0xFF):cycle-=1
        return cycle,addr
    def addr_absy(self,cycle,memory,zp_cross=True):
        cycle,addrabs = self.fetch_word(cycle,memory)
        addr = np.uint16(addrabs+self.Y)
        if not zp_cross:cycle-=1
        elif (addr-addrabs>=0xFF):cycle-=1
        return cycle,addr
    def addr_indx(self,cycle,memory):
        cycle,addr = self.fetch_byte(cycle,memory)
        absaddr = np.uint8(addr+self.X)
        cycle-=1
        cycle,addr  = self.read_word(cycle,memory,absaddr)
        return cycle,addr
    def addr_indy(self,cycle,memory,zp_cross=True):
        cycle,addr = self.fetch_byte(cycle,memory)
        cycle,addr  = self.read_word(cycle,memory,addr)
        addr = np.uint16(addr+self.Y)
        if not zp_cross: cycle-=1
        elif (self.Y>=0xFF):cycle-=1
        return cycle,addr
    
    #TODO
    def set_flag_add(self,val,old,data):
        self.Z = int(self.A == 0)
        self.N = int((self.A&0b10000000)>0 )
        self.C= int(val>0xFF)
        self.V=0x0
        if (old&0b10000000) ^ (data&0b10000000)==0:
            self.V = int((self.A&0b10000000) != (old&0b10000000))
            

            
    def set_flag_cmp(self,reg,operand):
        x = np.uint8(reg-operand)
        self.N =int((x & 0b10000000) > 0)
        self.Z = int(reg==operand)
        self.C = int(reg>=operand)
        
            
    def rol(self,data):
        n = ((self.C<<8)|data)&0x1FF
        self.C = int((data&0b10000000)>0)
        return (((n << 1)&0x1FF) |((n >> 8)&0x1FF))&0xFF
    
    
    def ror(self,data):
        n = ((self.C<<8)|data)&0x1FF
        self.C = int((data&0b00000001)>0)
        return np.uint8(((n >> 1)&0x1FF) | ((n << 8)&0x1FF) )&0xFF
    
    '''===============LOAD==============='''
    def set_flag_lda(self,val):
        self.Z = int(val == 0)
        self.N = int((val&0b10000000)>0)
    def load(self,ins,cycle,memory):
            reg = 0
            if ins == 0xA9 or ins==0xA2 or ins==0xA0:   #LDA_IM
                cycle, reg = self.fetch_byte(cycle,memory)
                self.set_flag_lda(reg)
            elif ins == 0xA5 or ins==0xA4 or ins==0xA6:  #LDA_ZP
                cycle,addr = self.addr_zp(cycle,memory)
                cycle,reg = self.read_byte(cycle,memory,addr)
                self.set_flag_lda(reg)
            elif ins == 0xB5 or ins==0xB4: #LDA_ZP,X
                cycle,addr = self.addr_zpx(cycle,memory)
                cycle,reg = self.read_byte(cycle,memory,addr)
                self.set_flag_lda(reg)
            elif ins == 0xB6: #LDA_ZP,Y
                cycle,addr = self.addr_zpy(cycle,memory)
                cycle,reg = self.read_byte(cycle,memory,addr)
            elif ins == 0xAD or ins==0xAE or ins==0xAC: #LDA_ABS
                cycle,addr = self.addr_abs(cycle,memory)
                cycle,reg= self.read_byte(cycle,memory,addr)
                self.set_flag_lda(reg)
            elif ins == 0xBD or ins==0xBC: #LDA_ABS,X
                cycle,addr = self.addr_absx(cycle,memory)
                cycle,reg = self.read_byte(cycle,memory,addr)
                self.set_flag_lda(reg)
            elif ins == 0xB9 or ins==0xBE:#LDA_ABS,Y
                cycle,addr = self.addr_absy(cycle,memory)
                cycle,reg = self.read_byte(cycle,memory,addr)
                self.set_flag_lda(reg)
            elif ins == 0xA1: #LDA_INDX
                cycle,addr = self.addr_indx(cycle,memory)
                cycle,reg = self.read_byte(cycle,memory,addr)
                self.set_flag_lda(reg)
            elif ins == 0xB1: #LDA_INDY
                cycle,addr = self.addr_indy(cycle,memory)
                cycle,reg = self.read_byte(cycle,memory,addr)
                self.set_flag_lda(reg)
            return reg,cycle
        
    '''===============STORE==============='''
    def store(self,val,ins,cycle,memory):
        val = np.uint8(val)
        if ins==0x85 or ins==0x86 or ins==0x84: #ZP
            cycle,addr = self.fetch_byte(cycle,memory)
            cycle = memory.write_byte(val,addr,cycle)
        elif ins==0x95 or ins==0x94: #ZP_X
            cycle,addr = self.addr_zpx(cycle,memory)
            cycle = memory.write_byte(val,addr,cycle)
        elif ins==0x96: #ZP_Y
            cycle,addr = self.addr_zpy(cycle,memory)
            cycle = memory.write_byte(val,addr,cycle)
        elif ins == 0x8D or ins==0x8E or ins==0x8C: #ABS
            cycle,addr = self.addr_abs(cycle,memory)
            cycle = memory.write_byte(val,addr,cycle)
        elif ins == 0x9D: #ABS_X
            cycle,addr = self.addr_absx(cycle,memory,zp_cross=False)
            cycle = memory.write_byte(val,addr,cycle)
        elif ins == 0x99: #ABS_Y
            cycle,addr = self.addr_absy(cycle,memory,zp_cross=False)
            cycle = memory.write_byte(val,addr,cycle)
        elif ins == 0x81: #INDX
            cycle,addr = self.addr_indx(cycle,memory)
            cycle = memory.write_byte(val,addr,cycle)
        elif ins == 0x91: #LDA_INDY
            cycle,addr = self.addr_indy(cycle,memory,zp_cross=False)
            cycle = memory.write_byte(val,addr,cycle)
        return cycle
    
    
    '''===============LOGICAL==============='''
    def logical_op(self,op,ins,cycle,memory):
        if ins==0x29 or ins==0x49 or ins==0x09: #IM
            cycle,data = self.fetch_byte(cycle,memory)
            self.A = eval(str(hex(self.A))+op+str(hex(data)))
            self.set_flag_lda(self.A)
        elif ins==0x25 or ins==0x45 or ins==0x05:
            cycle,addr = self.addr_zp(cycle,memory)
            cycle,data = self.read_byte(cycle,memory,addr)
            self.A = eval(str(hex(self.A))+op+str(hex(data)))
            self.set_flag_lda(self.A)
        elif ins==0x35 or ins==0x55 or ins==0x15:
            cycle,addr = self.addr_zpx(cycle,memory)
            cycle,data = self.read_byte(cycle,memory,addr)
            self.A = eval(str(hex(self.A))+op+str(hex(data)))
            self.set_flag_lda(self.A)
        elif ins==0x2D or ins==0x4D or ins==0x0D:
            cycle,addr = self.addr_abs(cycle,memory)
            cycle,data= self.read_byte(cycle,memory,addr)
            self.A = eval(str(hex(self.A))+op+str(hex(data)))
            self.set_flag_lda(self.A)
        elif ins==0x3D or ins==0x5D or ins==0x1D:
            cycle,addr = self.addr_absx(cycle,memory)
            cycle,data= self.read_byte(cycle,memory,addr)
            self.A = eval(str(hex(self.A))+op+str(hex(data)))
            self.set_flag_lda(self.A)
        elif ins==0x39 or ins==0x59 or ins==0x19:
            cycle,addr = self.addr_absy(cycle,memory)
            cycle,data= self.read_byte(cycle,memory,addr)
            self.A = eval(str(hex(self.A))+op+str(hex(data)))
            self.set_flag_lda(self.A)
        elif ins==0x21 or ins==0x41 or ins==0x01:
            cycle,addr = self.addr_indx(cycle,memory)
            cycle,data= self.read_byte(cycle,memory,addr)
            self.A = eval(str(hex(self.A))+op+str(hex(data)))
            self.set_flag_lda(self.A)
        elif ins==0x31 or ins==0x51 or ins==0x11:
            cycle,addr = self.addr_indy(cycle,memory)
            cycle,data= self.read_byte(cycle,memory,addr)
            self.A = eval(str(hex(self.A))+op+str(hex(data)))
            self.set_flag_lda(self.A)
        return cycle
    
    '''===============BRANCH==============='''
    def branch(self,flag,value,cycle,memory):
        cycle,data = self.fetch_byte(cycle,memory)
        if flag==value: 
            tmp=self.PC
            self.PC = np.uint16(self.PC+np.int8(data))
            cycle-=1
            if (self.PC>>8) != (tmp>>8):cycle-=2
        return cycle

        
    
    '''===============Execute==============='''
    def execute(self,cycle,memory):
        while cycle>0:
            cycle,ins = self.fetch_byte(cycle,memory)
            #print(hex(ins),hex(self.A),hex(self.X),hex(self.Y),self.C)
            if ins==0xFF:break #Uncomment this in deployment
            
            #=================LOAD==============#
            if ins == 0xA9 or ins == 0xA5 or ins==0xB5 or ins==0xAD or ins==0xBD or ins==0xB9 or ins==0XB1 or ins==0xA1:#LDA
                self.A,cycle = self.load(ins,cycle,memory)
            elif ins==0xA2 or ins == 0xA6 or ins == 0xB6 or ins==0xAE or ins == 0xBE:#LDX
                self.X,cycle= self.load(ins,cycle,memory)
            elif ins==0xA0 or ins == 0xA4 or ins == 0xB4 or ins==0xAC or ins == 0xBC:#LDY
                self.Y,cycle= self.load(ins,cycle,memory)
            #=================STORE==============#
            elif ins==0x85 or ins==0x95 or ins==0x8D or ins==0x9D or ins==0x99 or ins==0x81 or ins==0x91:
                cycle = self.store(self.A,ins,cycle,memory)
            elif ins==0x86 or ins==0x96 or ins==0x8E:
                cycle = self.store(self.X,ins,cycle,memory)
            elif ins==0x84 or ins==0x94 or ins==0x8C:
                cycle = self.store(self.Y,ins,cycle,memory)
            #=================TRANSFER==============#
            elif ins==0xAA or ins==0xBA:
                self.X=self.A if ins ==0xAA else self.SP
                cycle-=1
                self.set_flag_lda(self.X)
            elif ins==0XA8:
                self.Y=self.A
                cycle-=1
                self.set_flag_lda(self.Y)
            elif ins==0x8A:
                self.A=self.X 
                cycle-=1
                self.set_flag_lda(self.A)
            elif ins==0x98:
                self.A=self.Y
                cycle-=1
                self.set_flag_lda(self.A)
            elif ins==0x9A:
                self.SP=self.X 
                cycle-=1
            #======STACK======
            elif ins==0x48: #PHA
                cycle = self.pushBytetoStack(self.A,cycle,memory)
            elif ins==0x08: #PHP
                flag = self.get_flag()|0b00011000 #php turns on bit 4,5
                #print(bin(self.get_flag()))
                cycle = self.pushBytetoStack(flag,cycle,memory)
            elif ins==0x68: #PLA
                cycle,self.A = self.popBytefromStack(cycle,memory)
                self.set_flag_lda(self.A)
                cycle -= 1
            elif ins==0x28: #PLP
                cycle,data = self.popBytefromStack(cycle,memory)
                self.set_flag(data&0b11100111)
                cycle -= 1
            #===============LOGICAL==========
            elif ins==0x29 or ins==0x25 or ins==0x35 or ins==0x2D or ins==0x3D or ins==0x39 or ins==0x21 or ins==0x31:#AND
                cycle = self.logical_op("&",ins,cycle,memory)
            elif ins==0x49 or ins==0x45 or ins==0x55 or ins==0x4D or ins==0x5D or ins==0x59 or ins==0x41 or ins==0x51:#EOR
                cycle = self.logical_op("^",ins,cycle,memory)
            elif ins==0x09 or ins==0x05 or ins==0x15 or ins==0x0D or ins==0x1D or ins==0x19 or ins==0x01 or ins==0x11: #ORA
                cycle = self.logical_op("|",ins,cycle,memory)
            #================TODO - TEST================
            elif ins == 0x24: #bit_zp  
                cycle,addr = self.addr_zp(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                x = self.A & data
                self.Z = int(x==0)
                self.V = int((x & 0b01000000)>0)
                self.N = int((x & 0b10000000) >0)
            elif ins ==0x2C: #bit_abs
                cycle,addr = self.addr_abs(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                x = self.A & data
                self.Z = int(x==0)
                self.V = int((x & 0b01000000)>0)
                self.N = int((x & 0b10000000) >0)           
            #===============INC-DEC===========
            elif ins==0xE8 or ins==0xCA: #INX,DECX
                val = 1 if ins==0xE8 else -1
                self.X = np.uint8(self.X+val)
                cycle-=1
                self.set_flag_lda(self.X)
            elif ins==0xC8 or ins==0x88: #INY,DEY
                val = 1 if ins==0xC8 else -1
                self.Y=np.uint8(self.Y+val)
                cycle-=1
                self.set_flag_lda(self.Y)
            elif ins == 0xE6 or ins==0xC6:#INC_ZP,DEC_ZP
                val = 1 if ins==0xE6 else -1
                cycle,addr = self.addr_zp(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                data = np.uint8(data+val)
                cycle-=1
                cycle = memory.write_byte(data,addr,cycle)
                self.set_flag_lda(data)
            elif ins == 0xF6 or ins==0xD6:#INC_ZPX,DEC_ZPX
                val = 1 if ins==0xF6 else -1
                cycle,addr = self.addr_zpx(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                data = np.uint8(data+val)
                cycle-=1
                cycle = memory.write_byte(data,addr,cycle)
                self.set_flag_lda(data)
            elif ins == 0xEE or ins == 0xCE:#INC_ABS,DEC_ABS
                val = 1 if ins==0xEE else -1
                cycle,addr = self.addr_abs(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                data = np.uint8(data+val)
                cycle-=1
                cycle = memory.write_byte(data,addr,cycle)
                self.set_flag_lda(data)
            elif ins == 0xFE or ins==0xDE:#INC_ABSX,DEC_ABSX
                val = 1 if ins==0xFE else -1
                cycle,addr = self.addr_absx(cycle,memory,zp_cross=False)
                cycle,data = self.read_byte(cycle,memory,addr)
                data = np.uint8(data+val)
                cycle-=1
                cycle = memory.write_byte(data,addr,cycle)
                self.set_flag_lda(data)
            
            #=============ADD============
            elif ins==0x69 :
                cycle, data = self.fetch_byte(cycle,memory)
                old = self.A
                val = self.A+data+self.C
                self.A = np.uint8(val)
                self.set_flag_add(val,old,data)
            elif ins==0x65:
                cycle,addr = self.addr_zp(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                old = self.A
                val = self.A+data+self.C
                self.A = np.uint8(val)
                self.set_flag_add(val,old,data)
            elif ins==0x75:
                cycle,addr = self.addr_zpx(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                old=self.A
                val = self.A+data+self.C
                self.A = np.uint8(val)
                self.set_flag_add(val,old,data)
            elif ins==0x6D:
                cycle,addr = self.addr_abs(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                old=self.A
                val = self.A+data+self.C
                self.A = np.uint8(val)
                self.set_flag_add(val,old,data)
            elif ins==0X7D:
                cycle,addr = self.addr_absx(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                old=self.A
                val = self.A+data+self.C
                self.A = np.uint8(val)
                self.set_flag_add(val,old,data)
            elif ins==0x79:
                cycle,addr = self.addr_absy(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                old=self.A
                val = self.A+data+self.C
                self.A = np.uint8(val)
                self.set_flag_add(val,old,data)
            elif ins==0x61:
                cycle,addr = self.addr_indx(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                old=self.A
                val = self.A+data+self.C
                self.A = np.uint8(val)
                self.set_flag_add(val,old,data)
            elif ins==0x71:
                cycle,addr = self.addr_indy(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                old=self.A
                val = self.A+data+self.C
                self.A = np.uint8(val)
                self.set_flag_add(val,old,data)
                
                
            #===============SUB=================
            elif ins==0xE9 :
                cycle, data = self.fetch_byte(cycle,memory)
                data = ~(data)&0xFF
                old = self.A
                val = self.A+data+self.C
                self.A = np.uint8(val)
                self.set_flag_add(val,old,data)
            elif ins==0xE5:
                cycle,addr = self.addr_zp(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                data = ~(data)&0xFF
                old = self.A
                val = self.A+data+self.C
                self.A = np.uint8(val)
                self.set_flag_add(val,old,data)
            elif ins==0xF5:
                cycle,addr = self.addr_zpx(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                data = ~(data)&0xFF
                old = self.A
                val = self.A+data+self.C
                self.A = np.uint8(val)
                self.set_flag_add(val,old,data)
            elif ins==0xED:
                cycle,addr = self.addr_abs(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                data = ~(data)&0xFF
                old = self.A
                val = self.A+data+self.C
                self.A = np.uint8(val)
                self.set_flag_add(val,old,data)
            elif ins==0XFD:
                cycle,addr = self.addr_absx(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                data = ~(data)&0xFF
                old = self.A
                val = self.A+data+self.C
                self.A = np.uint8(val)
                self.set_flag_add(val,old,data)
            elif ins==0xF9:
                cycle,addr = self.addr_absy(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                data = ~(data)&0xFF
                old = self.A
                val = self.A+data+self.C
                self.A = np.uint8(val)
                self.set_flag_add(val,old,data)
            elif ins==0xE1:
                cycle,addr = self.addr_indx(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                data = ~(data)&0xFF
                old = self.A
                val = self.A+data+self.C
                self.A = np.uint8(val)
                self.set_flag_add(val,old,data)
            elif ins==0xF1:
                cycle,addr = self.addr_indy(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                data = ~(data)&0xFF
                old = self.A
                val = self.A+data+self.C
                self.A = np.uint8(val)
                self.set_flag_add(val,old,data)
                
                
            #===============CMP=================
            elif ins==0xC9:
                cycle, data = self.fetch_byte(cycle,memory)
                self.set_flag_cmp(self.A,data)
            elif ins==0xC5:
                cycle,addr = self.addr_zp(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                self.set_flag_cmp(self.A,data)
            elif ins==0xD5:
                cycle,addr = self.addr_zpx(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                self.set_flag_cmp(self.A,data)
            elif ins==0xCD:
                cycle,addr = self.addr_abs(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                self.set_flag_cmp(self.A,data)
            elif ins==0xDD:
                cycle,addr = self.addr_absx(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                self.set_flag_cmp(self.A,data)
            elif ins==0xD9:
                cycle,addr = self.addr_absy(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                self.set_flag_cmp(self.A,data)
            elif ins==0xC1:
                cycle,addr = self.addr_indx(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                self.set_flag_cmp(self.A,data)
            elif ins==0xD1:
                cycle,addr = self.addr_indy(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                self.set_flag_cmp(self.A,data)
            
            elif ins==0xE0:
                cycle, data = self.fetch_byte(cycle,memory)
                self.set_flag_cmp(self.X,data)
            elif ins==0xE4:
                cycle,addr = self.addr_zp(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                self.set_flag_cmp(self.X,data)
            elif ins==0xEC:
                cycle,addr = self.addr_abs(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                self.set_flag_cmp(self.X,data)
            
            elif ins==0xC0:
                cycle, data = self.fetch_byte(cycle,memory)
                self.set_flag_cmp(self.Y,data)
            elif ins==0xC4:
                cycle,addr = self.addr_zp(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                self.set_flag_cmp(self.Y,data)
            elif ins==0xCC:
                cycle,addr = self.addr_abs(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                self.set_flag_cmp(self.Y,data)
            
            
            #===============BRANCH==============
            elif ins==0x90 or ins==0xB0: #BCC,BCS
                value = 0x0 if ins==0x90 else 0x1
                cycle = self.branch(self.C,value,cycle,memory)
            elif ins==0xF0 or ins==0xD0: #BEQ,BNE
                value = 0x0 if ins==0xD0 else 0x1
                cycle = self.branch(self.Z,value,cycle,memory)
            elif ins==0x30 or ins==0x10: #BMI,BPL
                value = 0x0 if ins==0x10 else 0x1
                cycle = self.branch(self.N,value,cycle,memory)
            elif ins==0x50 or ins==0x70: #BCC,BCS
                value = 0x0 if ins==0x50 else 0x1
                cycle = self.branch(self.V,value,cycle,memory)
            
            #===============FLAGS===============
            elif ins==0x18:
                self.C = 0x0 
                cycle-=1
            elif ins==0xD8:
                self.D = 0x0 
                cycle-=1
            elif ins==0x58:
                self.I = 0x0
                cycle-=1
            elif ins==0xB8:
                self.V = 0x0
                cycle-=1
            elif ins==0x38:
                self.C = 0x1
                cycle-=1
            elif ins==0xF8:
                self.D = 0x1
                cycle-=1
            elif ins==0x78:
                self.I = 0x1
                cycle-=1
            #===============ASL===============
            
            elif ins==0x0A:
                self.C = int((self.A&0b10000000)>0)
                self.A = (self.A<<1)&0xFF
                cycle-=1
            elif ins==0x06:
                cycle,addr = self.addr_zp(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                self.C = int((data&0b10000000)>0)
                data = (data<<1)&0xFF
                cycle-=1
                cycle = memory.write_byte(data,addr,cycle)
                self.set_flag_lda(data)
            elif ins==0x16:
                cycle,addr = self.addr_zpx(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                self.C = int((data&0b10000000)>0)
                data = (data<<1)&0xFF
                cycle-=1
                cycle = memory.write_byte(data,addr,cycle)
                self.set_flag_lda(data)
            elif ins==0x0E:
                cycle,addr = self.addr_abs(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                self.C = int((data&0b10000000)>0)
                data = (data<<1)&0xFF
                cycle-=1
                cycle = memory.write_byte(data,addr,cycle)
                self.set_flag_lda(data)
            elif ins==0x1E:
                cycle,addr = self.addr_absx(cycle,memory,zp_cross=False)
                cycle,data = self.read_byte(cycle,memory,addr)
                self.C = int((data&0b10000000)>0)
                data = (data<<1)&0xFF
                cycle-=1
                cycle = memory.write_byte(data,addr,cycle)
                self.set_flag_lda(data)
            #==============LSR==================
            elif ins==0x4A:
                self.C = int((self.A&0b00000001)>0)
                self.A = (self.A>>1)&0xFF
                cycle-=1
            elif ins==0x46:
                cycle,addr = self.addr_zp(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                self.C = int((data&0b00000001)>0)
                data = (data>>1)&0xFF
                cycle-=1
                cycle = memory.write_byte(data,addr,cycle)
                self.set_flag_lda(data)
            elif ins==0x56:
                cycle,addr = self.addr_zpx(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                self.C = int((data&0b00000001)>0)
                data = (data>>1)&0xFF
                cycle-=1
                cycle = memory.write_byte(data,addr,cycle)
                self.set_flag_lda(data)
            elif ins==0x4E:
                cycle,addr = self.addr_abs(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                self.C = int((data&0b00000001)>0)
                data = (data>>1)&0xFF
                cycle-=1
                cycle = memory.write_byte(data,addr,cycle)
                self.set_flag_lda(data)
            elif ins==0x5E:
                cycle,addr = self.addr_absx(cycle,memory,zp_cross=False)
                cycle,data = self.read_byte(cycle,memory,addr)
                self.C = int((data&0b00000001)>0)
                data = (data>>1)&0xFF
                cycle-=1
                cycle = memory.write_byte(data,addr,cycle)
                self.set_flag_lda(data)
            #==============ROL-ROR==================
            elif ins==0x2A or ins==0x6A:
                self.A = self.rol(self.A) if ins==0x2A else self.ror(self.A)
                cycle-=1
            elif ins==0x26 or ins==0x66:
                cycle,addr = self.addr_zp(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                data = self.rol(data) if ins==0x26 else self.ror(data)
                cycle-=1
                cycle = memory.write_byte(data,addr,cycle)
                self.set_flag_lda(data)
            elif ins==0x36 or ins==0x76:
                cycle,addr = self.addr_zpx(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                data = self.rol(data) if ins==0x36 else self.ror(data)
                cycle-=1
                cycle = memory.write_byte(data,addr,cycle)
                self.set_flag_lda(data)
            elif ins==0x2E or ins==0x6E:
                cycle,addr = self.addr_abs(cycle,memory)
                cycle,data = self.read_byte(cycle,memory,addr)
                data = self.rol(data) if ins==0x2E else self.ror(data)
                cycle-=1
                cycle = memory.write_byte(data,addr,cycle)
                self.set_flag_lda(data)
            elif ins==0x3E or ins==0x7E:
                cycle,addr = self.addr_absx(cycle,memory,zp_cross=False)
                cycle,data = self.read_byte(cycle,memory,addr)
                data = self.rol(data) if ins==0x3E else self.ror(data)
                cycle-=1
                cycle = memory.write_byte(data,addr,cycle)
                self.set_flag_lda(data)
        
            
            #===============JUMPS===============
            elif ins==0x4C: #JMP_ABS
                cycle,addr = self.addr_abs(cycle,memory)
                self.PC = addr
            elif ins==0x6C: #JMP_IND
                cycle,addr = self.addr_abs(cycle,memory)
                cycle,addr = self.read_word(cycle,memory,addr)
                self.PC = addr
            elif ins == 0x20: #JSR
                cycle,addr = self.fetch_word(cycle,memory)
                cycle = self.pushWordtoStack(self.PC-1,cycle,memory)
                self.PC = addr
            elif ins==0x60: #RTS
                cycle,addr = self.popWordfromStack(cycle,memory)
                self.PC = addr+1
                cycle-=2
            
            #===============BRK-RTI-NOP=================
            elif ins == 0x00:
                cycle = self.pushWordtoStack(self.PC,cycle,memory)
                flag = self.get_flag()|0b00011000 #turns on bit 4,5
                cycle = self.pushBytetoStack(flag,cycle,memory)
                self.PC = (memory.data[0xFFFF]<<8 & 0xFFFF) | (memory.data[0xFFFE]&0xFF)
                self.B = 0x1
                cycle-=1
            elif ins==0x40:
                cycle,data = self.popBytefromStack(cycle,memory)
                self.set_flag(data&0b11100111)
                cycle,addr = self.popWordfromStack(cycle,memory)
                self.PC = addr
            
            elif ins==0xEA: #NOP
                cycle-=1
            else:
                raise Exception(f"Error: Invalid Opcode: {hex(ins)}")
        return cycle


# In[ ]:





# In[ ]:




