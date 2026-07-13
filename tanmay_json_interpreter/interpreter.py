from tkinter import *
import tkinter.font as tkFont
import json
import tkinter.messagebox as messagebox

main = Tk()
main.geometry("500x500")
main.title("TQL Editor")

def load():
   with open("data.json", "r") as f:
      return json.load(f)

def save(data):
   with open("data.json", "w") as f:
      f.write(json.dumps(data, indent=4))

try:
   f = open("data.json", "r")
   f.close()
except:
   data = {"root": {"class": "TABLE"}}
   save(data)

Font = tkFont.Font(family="Arial", size=16, weight=tkFont.NORMAL)
Bolded = tkFont.Font(size=16, weight=tkFont.BOLD)

styleMap = {
   "SCOPE": ["#FF69B4", Bolded],
   "NEW": ["#FFA500", Bolded],
   "ROOT": ["#7DF9FF", Font],
   "SET": ["#FF69B4", Bolded],
   "AS": ["#FF69B4", Bolded],
   "PARENT": ["#1E90FF", Font],
   "True": ["#00FF00", Font],
   "False": ["#FF0000", Font],
   "DEL": ["#FF00FF", Bolded]
}

def checkType(val: str):
   if val == "True" or val == "False": return bool
   if val.isdigit(): return int

   try:
      float(val)
      return float
   except ValueError:
      return str

datatypes = {"STRING": [str, int], "BOOL": bool, "NUMBER": [int, float], "TABLE": str}
dtColor = "#66FF00"

class Formatter():
    def __init__(self, styles: dict[str, list[str, tkFont.Font]]):
       self.styling = styles

       self.box = Text(
          main,
          font=Font,
       )

       self.box.tag_config("DataType", foreground=dtColor)

       self.box.bind("<KeyRelease>", self.add)

       self.box.grid(row=0, column=0)
    
    def add(self, _):
       for tag in self.box.tag_names():
          self.box.tag_remove(tag, '1.0', END)
       vals = self.styling.keys()
        
       prev = "1.0"
      
       lines = self.box.get('1.0', END).split("\n")
       for j in lines:
          for i in j.split(" "):
              i = i.strip()
              if i in datatypes:
                index = self.box.search(i, prev, nocase=0, stopindex=END)
                if not index: continue
                
                split = index.split(".")
                prev = f"{split[0]}.{int(split[1]) + int(len(i))}"
                self.box.tag_add("DataType", index, prev)
                
              elif i in vals:
                index = self.box.search(i, prev, nocase=0, stopindex=END)
                if not index: continue
                
                split = index.split(".")
                prev = f"{split[0]}.{int(split[1]) + int(len(i))}"

                self.box.tag_add(i+prev, index, prev)
                self.box.tag_config(i+prev, foreground=self.styling[i][0], font=self.styling[i][1])

class Interpreter():
    def __init__(self, styleMap=dict[str, list[str, tkFont.Font]]):
       self.formatter = Formatter(styleMap)  
       self.currentScope = None
       self.data = load()
       #self.scope = self.data

    def interpret(self):
       lines = self.formatter.box.get('1.0', END)
       lines = [x for x in lines.split("\n") if x != ""]
       
       for i in lines:   
          i = [x for x in i.split(" ") if x != ""]
          for j, val in enumerate(i):
             if val in self.formatter.styling.keys():
                try:
                   next = i[j+1]
                except:
                   next = 0
                if val == "SCOPE":
                   if next == 0:
                     messagebox.showwarning(message="No scope specified")
                   else: 
                      if next == "ROOT":
                         self.currentScope = "root"
                      elif next == "PARENT":
                         if self.currentScope == "root": 
                            messagebox.showwarning(message="Cannot get parent scope of ROOT")
                            return
                         elif not self.currentScope:
                            messagebox.showwarning(message="Cannot get parent scope when a scope is not defined")
                            return
                         current = self.currentScope
                         current = current.split("/")
                         current = current[:len(current)-1]
                         self.currentScope = "/".join(current)
                      else:
                         if not self.currentScope:
                           messagebox.showwarning(message="No valid scope specified")
                           return 
                         
                         scope = self.data
                         for level in self.currentScope.split("/"):
                            scope = scope[level]
                         if next not in scope.keys():
                            messagebox.showwarning(message=f"Given scope {next} not found")
                            return
                         if scope[next]["class"] != "TABLE":
                            messagebox.showwarning(message=f"Cannot set scope as object of type {scope[next]["class"]}")
                            return
                         self.currentScope += f"/{next}"

                elif val == "NEW":
                   if next == 0: 
                     messagebox.showwarning(message="Expected data type after \"NEW\"") 
                     return
                   elif next not in datatypes.keys(): 
                      messagebox.showwarning(message="Valid data type not specified")
                      return
                   if not self.currentScope:
                      messagebox.showwarning(message="No scope specified")
                      return
                   
                   try:
                     name = i[j+2]
                   except:
                     messagebox.showwarning(message="No name / value specified")

                   if name in datatypes.keys():
                      messagebox.showwarning(message=f"Cannot have name set as data type {name}")
                      return
                   elif name == "class":
                      messagebox.showwarning(message=f"Cannot set variable name as class, it is already reserved.")
                      return
                   elif name in self.formatter.styling.keys():
                      messagebox.showwarning(message=f"Cannot set name as keyword {name}")
                      return

                   curScope = self.data
                   for i in self.currentScope.split("/"):
                      curScope = curScope[i]               

                   try:
                      curScope[name]
                      messagebox.showwarning(message=f"A {next} already exists with the name {name}")
                      return
                   except:
                      curScope[name] = {"class": next}
                      if next != "TABLE":
                         curScope[name]["value"] = None
                      save(self.data)
                elif val == "SET":
                   try:
                      next = i[j+1]
                      if not self.currentScope:
                         messagebox.showwarning(message="No scope defined")
                         return
                     
                      scope = self.data
                      for level in self.currentScope.split("/"):
                         scope = scope[level]
                      if next not in scope:
                         messagebox.showwarning(message=f"{next} not found within scope {self.currentScope.split("/")[::-1][0]}")
                         return
                         
                      checkAs = i[j+2]
                      if checkAs != "AS":
                         messagebox.showwarning(message=f"Expected 'AS' after {next}")
                         return
                         
                      val = i[j+3]
                      dt = checkType(val)
                      
                      className = scope[next]["class"]
                      validDt = datatypes[className]
                      if className == "TABLE":
                         messagebox.showwarning(message=f"Cannot set a value to a TABLE")
                         return
                      if type(validDt) == list:
                         if dt not in validDt:
                            messagebox.showwarning(message=f"Cannot set value of type {className} as a {dt}")
                            return  
                      else:
                         if dt != validDt:
                            messagebox.showwarning(message=f"Cannot set value of type {className} as a {dt}")      
                            return
                      
                      if dt == int:
                         val = int(val)
                      if dt == bool:
                         val = val == "True"
                      scope[next]["value"] = val 
                      save(self.data)                 
                   except:
                     messagebox.showwarning(message="Expected STRING after 'SET'")
                elif val == "DEL":
                   try:
                      next = i[j+1]
                      if not self.currentScope:
                         messagebox.showwarning(message="No scope defined")
                         return
                      
                      scope = self.data
                      for i in self.currentScope.split("/"):
                         scope = scope[i]
                      if next == "class":
                         messagebox.showwarning(message=f"Cannot remove an object's class")
                         return
                      elif next not in scope:
                         messagebox.showwarning(message=f"{next} not found in scope {self.currentScope.split("/")[::-1][0]}")
                         return
                      
                      del scope[next]
                      
                      save(self.data)
                   except:
                      messagebox.showwarning(message="Expected STRING after 'DEL'")
                      

interpreter = Interpreter(styleMap)

while True:
   inp = input("Would you like to interpret? ").strip()
   if inp.upper() == "Y":
      interpreter.interpret()
   else:
      break

mainloop()