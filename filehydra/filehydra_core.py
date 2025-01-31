import os
import glob
import shutil
import pandas as pd


def get_files_in_directory(dir,suffix):
        """Returns list of .txt files in given directory"""
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))    
        DIRECTORY = os.path.join(SITE_ROOT, dir)
        files = glob.glob(DIRECTORY + '/*'+suffix, recursive=True)
        return(files)        
    
def name_contains(s,files):
    """Returns list of files containing given string s in their name"""
    filtered_files=[file for file in files if s in file]
    return(filtered_files) 



class FileHydra:
    """This hydra lives in your folder structure and works with your files"""
    def __init__(self,location="."):
        self.location=location
        
        os.chdir(self.location)
        #self.target=location
        
        self.file_queues=[]
    
    def move_file_in_queue(self,prefix,suffix,olddir,newdir,index):
        """processes only files without spaces in name"""
        files=get_files_in_directory(olddir,suffix)
        list1=name_contains(prefix,files)
        if len(list1)>0:
            filename=list1[index]
            
            
            filename=filename.split(olddir+'\\')[1]
            
            self.move_file(filename,olddir,newdir)
            #path="move "+olddir+"\\"+filename+" "+newdir#+"\\"+filename
            #print(path)
            #os.system(path)
        else:
            print("No files found")
        
    
    def move_file(self,filename,olddir,newdir):
        """processes only files without spaces in name"""
        try:
            os.mkdir(newdir)
            print("Newdir "+newdir+" created")
        except:
            print("Newdir exists")
        
        
        if olddir in filename:
            path="move "+filename+" "+newdir#+"\\"+filename
        else:
            path="move "+olddir+"\\"+filename+" "+newdir#+"\\"+filename
        print(path)
        os.system(path)
        
        

    def rename_file(self,oldfile,newfile):
        os.rename(oldfile,newfile)
                
    def copy_file(self,oldfile,destination):
        shutil.copy(oldfile,destination)

    def create_folder(self,name):
        try:
            os.mkdir(name)
            print("Folder "+name+" was created.")
        except FileExistsError:
            print("folder "+name+" already exists, creation skipped.")

    def remove_folder(self,name):
        os.rmdir(name)

    def delete_file(self,name):
        os.remove(name)
        
        
        
       
        
    def change_hydra_location(self,target_folder):
        self.location=target_folder
        os.chdir(self.location)
        
        
    def create_file_queue(self,name):
        self.file_queues.append(FileQueue(self.location,name))
        self.file_queues[-1].initialize_queue_folders()
        

   
class FileTemplate:
    """Opens file, writes into file, reads file"""
    def __init__(self,prefix,suffix,typ=None):
        """suffix ... usually txt or xlsx"""
        
        self.prefix=prefix
        self.suffix=suffix
        if "txt" in self.suffix:
            self.type="txt"
        elif "xlsx" in self.suffix:
            self.type="xlsx"
        else:
            self.type=typ
        
            
    def extract_data(self,filename):
        if self.type=="txt":
            with open(filename,"r") as f:
                rows=f.readlines()
            return(rows)
        elif self.type=="xlsx":
            df=pd.read_excel(filename,index_col=0)
            return(df)

    
class FileQueue:
    def __init__(self,root_path,name,filehydra=None,filename_order_lambda_function=lambda x:x):
        self.root_path=root_path
        self.name=name
        self.queue_path=self.root_path+"\\"+self.name
        
        if filehydra is None:    
            self.filehydra=FileHydra(self.root_path)
        else:
            self.filehydra=filehydra
            
        self.filename_order_lambda_function=filename_order_lambda_function #e.g. lambda x:int(x.split("_")[0]) - input filename, output ordered unique number
        
        self.files_in_queue=[]
        
    def initialize_queue_folders(self):
        self.filehydra.create_folder(self.name)
        print(self.filehydra.location)
        self.filehydra.change_hydra_location(self.root_path+"\\"+self.name)
        print(self.filehydra.location)
        self.filehydra.create_folder("processed")
        
    def refresh_files_in_queue(self,file_template):
        
        files=get_files_in_directory(self.queue_path,file_template.suffix)
        self.files_in_queue=name_contains(file_template.prefix,files)
        
        order_to_file_dict={self.filename_order_lambda_function(x):x for x in self.files_in_queue}
        ordered_files_in_queue=sorted([self.filename_order_lambda_function(x) for x in self.files_in_queue])
        self.files_in_queue=[order_to_file_dict[x] for x in ordered_files_in_queue]
        print(ordered_files_in_queue)
        
    
    def process_next_file(self,file_template):
       
        self.refresh_files_in_queue(file_template)
        
        try:
            filename=self.files_in_queue[0]
            print(filename)
            data=file_template.extract_data(filename)
            
            self.filehydra.move_file(filename,self.queue_path, self.queue_path+"\\processed")
            
            return(filename,data)
        except IndexError:
            print("No suitable file - no move")
            return("",None)
            
        
        
    def compare_two_files_and_process_first(self,file_template,process_data_function):
        try:
            self.refresh_files_in_queue(file_template)
            filename1=self.files_in_queue[0]
            filename2=self.files_in_queue[1]
            data1=file_template.extract_data(filename1)
            data2=file_template.extract_data(filename2)
            process_data_function(data1,data2)
            
            self.filehydra.move_file(filename1,self.queue_path, self.queue_path+"\\processed")
            return(filename1,filename2,data1,data2)
        except IndexError:
            print("No suitable file - no move")
            return("","",None,None)
            
        
        
        
        
        
        
        
        